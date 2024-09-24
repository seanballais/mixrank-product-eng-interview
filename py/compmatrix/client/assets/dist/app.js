(() => {
  // py/compmatrix/client/assets/raw/js/constants.js
  var APP_LIST_BATCH_SIZE = 50;
  var MAX_APP_LIST_SIZE = 100;
  var BASE_API_ENDPOINT = "/api/v1";
  console.assert(APP_LIST_BATCH_SIZE <= MAX_APP_LIST_SIZE);

  // py/compmatrix/client/assets/raw/js/fetching.js
  var DataState = class {
    static #_EMPTY = 0;
    // Data was just initialized.
    static #_LOADING = 1;
    static #_ERRORED = 2;
    static #_LOADED = 3;
    static get EMPTY() {
      return this.#_EMPTY;
    }
    static get LOADING() {
      return this.#_LOADING;
    }
    static get ERRORED() {
      return this.#_ERRORED;
    }
    static get LOADED() {
      return this.#_LOADED;
    }
  };
  var FetchDirection = class {
    static get PREVIOUS() {
      return "previous";
    }
    static get NEXT() {
      return "next";
    }
  };
  async function fetchAppListData(appListDataState, compmatrixDataState, activeFromSDKsState, activeToSDKsState, cursor = null, direction = null) {
    const url = `${BASE_API_ENDPOINT}/sdk-compmatrix/apps`;
    const compmatrixData = compmatrixDataState.getValue();
    const fromSDK = compmatrixData["selected-cell"]["from-sdk"];
    const toSDK = compmatrixData["selected-cell"]["to-sdk"];
    const activeFromSDKs = activeFromSDKsState.getValue();
    const activeToSDKs = activeToSDKsState.getValue();
    const otherFromSDKIDs = activeFromSDKs.filter((s) => {
      if (fromSDK !== null) {
        return s.id != fromSDK["id"];
      }
      return true;
    });
    const otherToSDKIDs = activeToSDKs.filter((s) => {
      if (toSDK !== null) {
        return s.id != toSDK["id"];
      }
      return true;
    });
    let rawParamPairs = [];
    if (fromSDK !== null && fromSDK["id"] !== null) {
      rawParamPairs.push(["from_sdk", fromSDK["id"]]);
    } else if (otherFromSDKIDs.length !== 0) {
      rawParamPairs.push(
        ...otherFromSDKIDs.map((s) => ["other_from_sdks", s["id"]])
      );
    }
    if (toSDK !== null && toSDK["id"] !== null) {
      rawParamPairs.push(["to_sdk", toSDK["id"]]);
    } else if (otherToSDKIDs.length !== 0) {
      rawParamPairs.push(
        ...otherToSDKIDs.map((s) => ["other_to_sdks", s["id"]])
      );
    }
    rawParamPairs.push(["count", APP_LIST_BATCH_SIZE]);
    if (cursor !== null) {
      rawParamPairs.push(["cursor", cursor]);
      rawParamPairs.push(["direction", direction]);
    }
    const params = new URLSearchParams(rawParamPairs);
    const paramString = params.toString();
    let appsJSON;
    try {
      const response = await fetch(`${url}?${paramString}`);
      appsJSON = await response.json();
    } catch (error) {
      console.error(error.message);
    }
    appListDataState.setValue((v) => {
      const numApps = appsJSON["data"]["apps"].length;
      const totalCount = appsJSON["data"]["total_count"];
      v["total-app-count"] = totalCount;
      if (cursor === null) {
        v["displayed-apps"] = [];
      }
      for (let i = 0; i < numApps; i++) {
        const app = appsJSON["data"]["apps"][i];
        let companyURL = null;
        if (app["company_url"] != "") {
          companyURL = app["company_url"];
        }
        let totalRatings = app["five_star_ratings"];
        totalRatings += app["four_star_ratings"];
        totalRatings += app["three_star_ratings"];
        totalRatings += app["two_star_ratings"];
        totalRatings += app["one_star_ratings"];
        let rating = 0;
        rating += app["five_star_ratings"] * 5;
        rating += app["four_star_ratings"] * 4;
        rating += app["three_star_ratings"] * 3;
        rating += app["two_star_ratings"] * 2;
        rating += app["one_star_ratings"] * 1;
        rating /= totalRatings;
        const newApp = {
          "name": app["name"],
          "seller_name": app["seller_name"],
          "company_url": companyURL,
          "artwork_large_url": app["artwork_large_url"],
          "rating": rating
        };
        if (cursor !== null && direction === FetchDirection.PREVIOUS) {
          v["displayed-apps"].unshift(newApp);
        } else {
          v["displayed-apps"].push(newApp);
        }
      }
      v["sdks"]["from-sdk"] = fromSDK;
      v["sdks"]["to-sdk"] = toSDK;
      v["start-cursor"] = appsJSON["data"]["start_cursor"];
      v["end-cursor"] = appsJSON["data"]["end_cursor"];
      let wasLeftPruned = false;
      let wasRightPruned = false;
      const numDisplayedApps = v["displayed-apps"].length;
      if (numDisplayedApps > MAX_APP_LIST_SIZE) {
        const numExtraApps = numDisplayedApps - MAX_APP_LIST_SIZE;
        if (direction === FetchDirection.PREVIOUS) {
          wasLeftPruned = true;
          v["displayed-apps"].splice(-numExtraApps);
          const startApp = v["displayed-apps"][0];
          v["start-cursor"] = createCursorFromDisplayedApp(startApp);
        } else {
          wasRightPruned = true;
          v["displayed-apps"].splice(0, numExtraApps);
          const numDisplayedApps2 = v["displayed-apps"].length;
          const endApp = v["displayed-apps"][numDisplayedApps2 - 1];
          v["end-cursor"] = createCursorFromDisplayedApp(endApp);
        }
      }
      if (numApps == totalCount) {
        v["need-prev-batch-trigger"] = false;
        v["need-next-batch-trigger"] = false;
      } else if (numApps == 0) {
        if (direction === FetchDirection.PREVIOUS) {
          v["need-prev-batch-trigger"] = false;
        } else {
          v["need-next-batch-trigger"] = false;
        }
      } else {
        if (direction === FetchDirection.PREVIOUS) {
          v["need-prev-batch-trigger"] = true;
        } else {
          v["need-next-batch-trigger"] = true;
        }
      }
      if (wasLeftPruned) {
        v["need-prev-batch-trigger"] = true;
      } else if (wasRightPruned) {
        v["need-next-batch-trigger"] = true;
      }
    });
  }
  function createCursorFromDisplayedApp(app) {
    return `${app["name"]};${app["seller_name"]}`;
  }

  // py/compmatrix/client/assets/raw/js/interactivity.js
  function moveSDKFromComboBoxToList(comboBox, selectableSDKs, activeSDKsList, activeSDKs) {
    const selectables = selectableSDKs.getValue();
    const actives = activeSDKs.getValue();
    if (selectables.length > 0) {
      const cBoxSelectedIndex = comboBox.selectedIndex;
      const activeSelectedIndex = activeSDKsList.selectedIndex;
      activeSDKs.setValue((v) => {
        v.push(selectableSDKs.getValue()[cBoxSelectedIndex]);
      });
      selectableSDKs.setValue((v) => {
        v.splice(cBoxSelectedIndex, 1);
      });
      const newSelectedIndex = Math.min(
        cBoxSelectedIndex,
        comboBox.options.length - 1
      );
      comboBox.selectedIndex = newSelectedIndex;
      if (actives.length > 0 && activeSelectedIndex !== null) {
        activeSDKsList.selectedIndex = activeSelectedIndex;
      }
    }
  }
  function moveSDKFromListToComboBox(comboBox, selectableSDKs, activeSDKsList, activeSDKs) {
    const selectables = selectableSDKs.getValue();
    const actives = activeSDKs.getValue();
    const comboBoxSelectedIndex = comboBox.selectedIndex;
    const activeSelectedIndex = activeSDKsList.selectedIndex;
    if (actives.length > 0 && activeSelectedIndex !== null) {
      let cBoxIdxOffset = 0;
      if (selectables.length > 0) {
        const cBoxSDKName = selectableSDKs.getValue()[comboBoxSelectedIndex].name;
        const activeSDKName = activeSDKs.getValue()[activeSelectedIndex].name;
        if (cBoxSDKName.toLowerCase() >= activeSDKName.toLowerCase() && cBoxSDKName > activeSDKName) {
          cBoxIdxOffset = 1;
        }
      }
      selectableSDKs.setValue((v) => {
        v.push(activeSDKs.getValue()[activeSelectedIndex]);
        v.sort((a, b) => {
          if (a.name.toLowerCase() < b.name.toLowerCase()) {
            return -1;
          } else if (a.name.toLowerCase() > b.name.toLowerCase()) {
            return 1;
          } else {
            return 0;
          }
        });
      });
      activeSDKs.setValue((v) => {
        v.splice(activeSelectedIndex, 1);
      });
      if (selectables.length > 0) {
        comboBox.selectedIndex = comboBoxSelectedIndex + cBoxIdxOffset;
      } else {
        comboBox.selectedIndex = 0;
      }
      const newListSelectedIndex = Math.min(
        activeSelectedIndex,
        activeSDKsList.options.length - 1
      );
      activeSDKsList.selectedIndex = newListSelectedIndex;
    }
  }

  // py/compmatrix/client/assets/raw/js/state.js
  var State = class {
    // Note: We're not using the get and set property syntax since the usage
    //       will be awkward when passing a function to the setter (which we
    //       allow so that modification of the internal value can be modified
    //       more easily). For example:
    //
    //         s.value = (v) => { v.push('Come inside of my heart'); };
    //
    //       feels like I'm setting the value of state `s` to a function.
    //       On the contrary:
    //
    //         s.setValue((v) => { v.push('If you\'re looking for answers'); }
    //
    //       feels more natural.
    constructor(initialValue) {
      this.value = initialValue;
      this.subscriptions = [];
    }
    getValue() {
      return this.value;
    }
    setValue(v) {
      if (typeof v === "function") {
        v(this.value);
      } else {
        this.value = v;
      }
      for (const f of this.subscriptions) {
        f(this.value);
      }
    }
    addReactor(f, runOnAdd = true, prioritize = false) {
      if (prioritize) {
        this.subscriptions.unshift(f);
      } else {
        this.subscriptions.push(f);
      }
      if (runOnAdd) {
        f(this.value);
      }
    }
  };

  // py/compmatrix/client/assets/raw/js/html.js
  function htmlToNodes(html) {
    const template = document.createElement("template");
    template.innerHTML = html;
    return template.content.childNodes;
  }

  // py/compmatrix/client/assets/raw/js/udomdiff.js
  var udomdiff_default = (parentNode, a, b, get, before) => {
    const bLength = b.length;
    let aEnd = a.length;
    let bEnd = bLength;
    let aStart = 0;
    let bStart = 0;
    let map = null;
    while (aStart < aEnd || bStart < bEnd) {
      if (aEnd === aStart) {
        const node = bEnd < bLength ? bStart ? get(b[bStart - 1], -0).nextSibling : get(b[bEnd - bStart], 0) : before;
        while (bStart < bEnd)
          parentNode.insertBefore(get(b[bStart++], 1), node);
      } else if (bEnd === bStart) {
        while (aStart < aEnd) {
          if (!map || !map.has(a[aStart]))
            parentNode.removeChild(get(a[aStart], -1));
          aStart++;
        }
      } else if (a[aStart] === b[bStart]) {
        aStart++;
        bStart++;
      } else if (a[aEnd - 1] === b[bEnd - 1]) {
        aEnd--;
        bEnd--;
      } else if (a[aStart] === b[bEnd - 1] && b[bStart] === a[aEnd - 1]) {
        const node = get(a[--aEnd], -1).nextSibling;
        parentNode.insertBefore(
          get(b[bStart++], 1),
          get(a[aStart++], -1).nextSibling
        );
        parentNode.insertBefore(get(b[--bEnd], 1), node);
        a[aEnd] = b[bEnd];
      } else {
        if (!map) {
          map = /* @__PURE__ */ new Map();
          let i = bStart;
          while (i < bEnd)
            map.set(b[i], i++);
        }
        if (map.has(a[aStart])) {
          const index = map.get(a[aStart]);
          if (bStart < index && index < bEnd) {
            let i = aStart;
            let sequence = 1;
            while (++i < aEnd && i < bEnd && map.get(a[i]) === index + sequence)
              sequence++;
            if (sequence > index - bStart) {
              const node = get(a[aStart], 0);
              while (bStart < index)
                parentNode.insertBefore(get(b[bStart++], 1), node);
            } else {
              parentNode.replaceChild(
                get(b[bStart++], 1),
                get(a[aStart++], -1)
              );
            }
          } else
            aStart++;
        } else
          parentNode.removeChild(get(a[aStart++], -1));
      }
    }
    return b;
  };

  // py/compmatrix/client/assets/raw/js/widgets.js
  var Widget = class {
    constructor(rootNodeID) {
      this.rootNode = document.getElementById(rootNodeID);
      this.nodes = [];
      this.states = {};
    }
    subscribeTo(refName, state) {
      this.states[refName] = state;
      state.addReactor(() => {
        this.update();
      });
    }
    batchSubscribe(states) {
      for (let i = 0; i < states.length; i++) {
        const state = states[i];
        this.states[state["refName"]] = state["state"];
        state.state.addReactor(() => {
          this.update();
        }, false, false);
      }
      this.update();
    }
    update() {
      this.nodes = this.createNodes();
      this.render();
    }
    createNodes() {
      return [];
    }
    render() {
      udomdiff_default(
        this.rootNode,
        [...this.rootNode.childNodes],
        [...this.nodes],
        (o) => o
      );
    }
  };
  var Button = class extends Widget {
    constructor(rootNode) {
      super(rootNode);
    }
    setOnClick(f) {
      this.rootNode.addEventListener("click", f);
    }
  };
  var CompMatrixDataToggler = class extends Widget {
    constructor(rootNode) {
      super(rootNode);
      this.rootNode.addEventListener("change", (e) => {
        if (e.target.checked) {
          this.states["data"].setValue((s) => {
            s["active-data"] = "normalized";
          });
        } else {
          this.states["data"].setValue((s) => {
            s["active-data"] = "raw";
          });
        }
      });
    }
  };
  var SDKSelect = class extends Widget {
    constructor(rootNode) {
      super(rootNode);
      this.idToIndexMap = /* @__PURE__ */ new Map();
    }
    get value() {
      return Number(this.rootNode.value);
    }
    get selectedIndex() {
      const index = this.idToIndexMap.get(this.value);
      if (index === void 0) {
        return null;
      } else {
        return index;
      }
    }
    get options() {
      return this.rootNode.options;
    }
    set selectedIndex(newIndex) {
      this.rootNode.selectedIndex = newIndex;
    }
    update() {
      const sdks = this.states["sdks"].getValue();
      for (let i = 0; i < sdks.length; i++) {
        this.idToIndexMap.set(sdks[i].id, i);
      }
      super.update();
    }
    createNodes() {
      const sdks = this.states["sdks"].getValue();
      let html = "";
      for (let i = 0; i < sdks.length; i++) {
        const sdk = sdks[i];
        html += `<option value="${sdk.id}">${sdk.name}</option>`;
      }
      return htmlToNodes(html);
    }
    moveSelectedOptionUp() {
      const selectedID = this.selectedIndex;
      const newIndex = Math.max(selectedID - 1, 0);
      this.states["sdks"].setValue((v) => {
        [v[newIndex], v[selectedID]] = [v[selectedID], v[newIndex]];
      });
      this.selectedIndex = newIndex;
    }
    moveSelectedOptionDown() {
      const selectedID = this.selectedIndex;
      const newIndex = Math.min(
        selectedID + 1,
        this.options.length - 1
      );
      this.states["sdks"].setValue((v) => {
        [v[newIndex], v[selectedID]] = [v[selectedID], v[newIndex]];
      });
      this.selectedIndex = newIndex;
    }
  };
  var CompMatrix = class extends Widget {
    constructor(rootNode) {
      super(rootNode);
      this.cellToSDKs = {};
    }
    update() {
      this.cellToSDKs = {};
      super.update();
      const data = this.states["data"].getValue();
      const dataState = data["state"];
      if (dataState == DataState.LOADED) {
        for (const [key, sdks] of Object.entries(this.cellToSDKs)) {
          const cell = document.getElementById(key);
          cell.addEventListener("click", () => {
            this.states["data"].setValue((v) => {
              v["selected-cell"]["from-sdk"] = sdks["from-sdk"];
              v["selected-cell"]["to-sdk"] = sdks["to-sdk"];
            });
          });
        }
      }
    }
    createNodes() {
      const data = this.states["data"].getValue();
      const dataState = data["state"];
      let html = "";
      const fromSDKData = this.states["from-sdks"].getValue();
      const toSDKData = this.states["to-sdks"].getValue();
      const fromSDKHeaders = [...fromSDKData];
      const toSDKHeaders = [...toSDKData];
      fromSDKHeaders.push({ "id": null, "name": "(none)" });
      toSDKHeaders.push({ "id": null, "name": "(none)" });
      const numFromSDKsHeaders = fromSDKHeaders.length;
      const numToSDKsHeaders = toSDKHeaders.length;
      html += "<tr>";
      html += "<th></th>";
      html += `<th colspan="${numToSDKsHeaders + 1}">To SDK</th>`;
      html += "</tr>";
      html += "<tr>";
      html += `<th rowspan="${numFromSDKsHeaders + 2}">`;
      html += "<span>From SDK</span>";
      html += "</th>";
      html += "</tr>";
      if (dataState == DataState.LOADED) {
        html += "<tr>";
        html += "<th></th>";
        for (let i = 0; i < numToSDKsHeaders; i++) {
          html += `<th>${toSDKHeaders[i]["name"]}</th>`;
        }
        html += "</tr>";
        const activeData = data["active-data"];
        const presentedData = data["data"][activeData];
        const percentageData = data["data"]["normalized"];
        for (let i = 0; i < presentedData.length; i++) {
          const rowData = presentedData[i];
          html += "<tr>";
          html += `<th>${fromSDKHeaders[i]["name"]}</th>`;
          for (let j = 0; j < rowData.length; j++) {
            let cellData = rowData[j];
            if (activeData == "normalized") {
              cellData = `${(cellData * 100).toFixed(0)}%`;
            }
            const opacity = percentageData[i][j];
            const id = `cmc-${i}${j}`;
            const colour = `hsla(0, 80%, 55%, ${opacity * 100}%)`;
            const style = `background-color: ${colour}`;
            html += `<td id="${id}" style="${style}">${cellData}</td>`;
            this.cellToSDKs[id] = {
              "from-sdk": fromSDKHeaders[i],
              "to-sdk": toSDKHeaders[j]
            };
          }
          html += "</tr>";
        }
      } else if (dataState == DataState.LOADING) {
        html += "<tr>";
        html += "<td>";
        html += '<span class="fas fa-circle-notch fa-spin"></span>';
        html += "</td>";
        html += "</tr>";
      }
      return htmlToNodes(html);
    }
  };
  var AppList = class extends Widget {
    constructor(rootNode) {
      super(rootNode);
      this.prevBatchTriggerObserver = null;
      this.nextBatchTriggerObserver = null;
      this.isBatchLoading = false;
    }
    update() {
      super.update();
      const appList = this.states["app-list"].getValue();
      const observerOptions = {
        root: this.rootNode
      };
      if (appList["need-prev-batch-trigger"]) {
        const callback = () => {
          entries.forEach((entry) => {
            if (entry && entry.isIntersecting && !this.isBatchLoading) {
              this.isBatchLoading = true;
              fetchAppListData(
                this.states["app-list"],
                this.states["compmatrix-data"],
                this.states["from-sdks"],
                this.states["to-sdks"],
                appList["start-cursor"],
                FetchDirection.PREVIOUS
              );
              this.isBatchLoading = false;
            }
          });
        };
        this.prevBatchTriggerObserver = new IntersectionObserver(
          callback,
          observerOptions
        );
        const trigger = document.getElementById("app-prev-batch-trigger");
        this.prevBatchTriggerObserver.observe(trigger);
      }
      if (appList["need-next-batch-trigger"]) {
        const callback = (entries2, observer) => {
          entries2.forEach((entry) => {
            if (entry && entry.isIntersecting && !this.isBatchLoading) {
              this.isBatchLoading = true;
              fetchAppListData(
                this.states["app-list"],
                this.states["compmatrix-data"],
                this.states["from-sdks"],
                this.states["to-sdks"],
                appList["end-cursor"],
                FetchDirection.NEXT
              );
              this.isBatchLoading = false;
            }
          });
        };
        this.nextBatchTriggerObserver = new IntersectionObserver(
          callback,
          observerOptions
        );
        const trigger = document.getElementById("app-next-batch-trigger");
        this.nextBatchTriggerObserver.observe(trigger);
      }
    }
    createNodes() {
      const appList = this.states["app-list"].getValue();
      let html = "";
      if (appList["need-prev-batch-trigger"]) {
        html += '<div id="app-prev-batch-trigger" class="batch-trigger">';
        html += '    <span class="fas fa-circle-notch fa-spin"></span>';
        html += "</div>";
      }
      for (let i = 0; i < appList["displayed-apps"].length; i++) {
        const app = appList["displayed-apps"][i];
        html += '<div class="app-card">';
        html += '  <div class="app-card-icon">';
        html += `    <img src=${app["artwork_large_url"]}/>`;
        html += "  </div>";
        html += '  <div class="app-card-info">';
        html += `    <h1>${app["name"]}</h1>`;
        html += '    <p class="app-card-info-company">';
        html += `      <a href=${app["company_url"]}">`;
        html += `      ${app["seller_name"]}`;
        html += "      </a>";
        html += "    </p>";
        html += "    <p>";
        html += '      <span class="fa-solid fa-star app-rating-icon">';
        html += "      </span>";
        html += `      ${app["rating"].toFixed(2)}`;
        html += "    </p>";
        html += "  </div>";
        html += "</div>";
      }
      if (appList["need-next-batch-trigger"]) {
        html += '<div id="app-next-batch-trigger" class="batch-trigger">';
        html += '    <span class="fas fa-circle-notch fa-spin"></span>';
        html += "</div>";
      }
      return htmlToNodes(html);
    }
  };
  var AppListDesc = class extends Widget {
    constructor(rootNode) {
      super(rootNode);
    }
    createNodes() {
      const appList = this.states["app-list"].getValue();
      let html = "<p>";
      if (appList["displayed-apps"].length == 0) {
        html += "No apps loaded in yet.";
      } else {
        const fromSDK = appList["sdks"]["from-sdk"];
        const toSDK = appList["sdks"]["to-sdk"];
        let fromSDKName = "";
        if (fromSDK === null) {
          fromSDKName = "(none)";
        } else {
          fromSDKName = fromSDK["name"];
        }
        let toSDKName = "";
        if (toSDK === null) {
          toSDKName = "(none)";
        } else {
          toSDKName = toSDK["name"];
        }
        html += `Migrated from ${fromSDKName} to ${toSDKName}.`;
      }
      html += "</p>";
      return htmlToNodes(html);
    }
  };

  // py/compmatrix/client/assets/raw/js/app.js
  document.addEventListener("DOMContentLoaded", onDocumentLoad, false);
  var App = class {
    constructor() {
      this.selectableFromSDKs = new State([]);
      this.activeFromSDKs = new State([]);
      this.selectableToSDKs = new State([]);
      this.activeToSDKs = new State([]);
      this.compmatrixData = new State({
        "data": {
          "raw": [],
          "normalized": []
        },
        "state": DataState.EMPTY,
        "active-data": "raw",
        "selected-cell": {
          "from-sdk": null,
          "to-sdk": null
        }
      });
      this.appListData = new State({
        "displayed-apps": [],
        "total-app-count": 0,
        "sdks": {
          "from-sdk": null,
          "to-sdk": null
        },
        "start-cursor": null,
        "end-cursor": null,
        "need-prev-batch-trigger": false,
        "need-next-batch-trigger": false
      });
      this.matrixTable = new CompMatrix("compmatrix");
      this.matrixTable.batchSubscribe([
        { "refName": "data", "state": this.compmatrixData },
        { "refName": "from-sdks", "state": this.activeFromSDKs },
        { "refName": "to-sdks", "state": this.activeToSDKs }
      ]);
      this.matrixTableDataToggler = new CompMatrixDataToggler(
        "compmatrix-data-toggle"
      );
      this.matrixTableDataToggler.subscribeTo("data", this.compmatrixData);
      this.fromSDKComboBox = new SDKSelect("from-sdk-selectables");
      this.fromSDKComboBox.subscribeTo("sdks", this.selectableFromSDKs);
      this.activeFromSDKsList = new SDKSelect("from-sdk-selected");
      this.activeFromSDKsList.subscribeTo("sdks", this.activeFromSDKs);
      this.toSDKComboBox = new SDKSelect("to-sdk-selectables");
      this.toSDKComboBox.subscribeTo("sdks", this.selectableToSDKs);
      this.activeToSDKsList = new SDKSelect("to-sdk-selected");
      this.activeToSDKsList.subscribeTo("sdks", this.activeToSDKs);
      this.fromSDKAddBtn = new Button("from-sdk-config-list-add-btn");
      this.selectedFromSDKRemoveBtn = new Button(
        "from-sdk-selected-remove-btn"
      );
      this.selectedFromSDKUpBtn = new Button(
        "from-sdk-selected-move-up-btn"
      );
      this.selectedFromSDKDownBtn = new Button(
        "from-sdk-selected-move-down-btn"
      );
      this.toSDKAddBtn = new Button("to-sdk-config-list-add-btn");
      this.selectedToSDKRemoveBtn = new Button("to-sdk-selected-remove-btn");
      this.selectedToSDKUpBtn = new Button("to-sdk-selected-move-up-btn");
      this.selectedToSDKDownBtn = new Button(
        "to-sdk-selected-move-down-btn"
      );
      this.appList = new AppList("apps-list");
      this.appList.batchSubscribe([
        { "refName": "app-list", "state": this.appListData },
        { "refName": "compmatrix-data", "state": this.compmatrixData },
        { "refName": "from-sdks", "state": this.activeFromSDKs },
        { "refName": "to-sdks", "state": this.activeToSDKs }
      ]);
      this.appListDesc = new AppListDesc("app-list-desc");
      this.appListDesc.subscribeTo("app-list", this.appListData);
      this.fromSDKAddBtn.setOnClick(() => {
        moveSDKFromComboBoxToList(
          this.fromSDKComboBox,
          this.selectableFromSDKs,
          this.activeFromSDKsList,
          this.activeFromSDKs
        );
      });
      this.selectedFromSDKRemoveBtn.setOnClick(() => {
        moveSDKFromListToComboBox(
          this.fromSDKComboBox,
          this.selectableFromSDKs,
          this.activeFromSDKsList,
          this.activeFromSDKs
        );
      });
      this.selectedFromSDKUpBtn.setOnClick(() => {
        this.activeFromSDKsList.moveSelectedOptionUp();
      });
      this.selectedFromSDKDownBtn.setOnClick(() => {
        this.activeFromSDKsList.moveSelectedOptionDown();
      });
      this.toSDKAddBtn.setOnClick(() => {
        moveSDKFromComboBoxToList(
          this.toSDKComboBox,
          this.selectableToSDKs,
          this.activeToSDKsList,
          this.activeToSDKs
        );
      });
      this.selectedToSDKRemoveBtn.setOnClick(() => {
        moveSDKFromListToComboBox(
          this.toSDKComboBox,
          this.selectableToSDKs,
          this.activeToSDKsList,
          this.activeToSDKs
        );
      });
      this.selectedToSDKUpBtn.setOnClick(() => {
        this.activeToSDKsList.moveSelectedOptionUp();
      });
      this.selectedToSDKDownBtn.setOnClick(() => {
        this.activeToSDKsList.moveSelectedOptionDown();
      });
      this.compmatrixData.addReactor(() => {
        fetchAppListData(
          this.appListData,
          this.compmatrixData,
          this.activeFromSDKs,
          this.activeToSDKs
        );
      });
      this.activeFromSDKs.addReactor(() => {
        this.#fetchCompMatrixValues();
      }, true, true);
      this.activeToSDKs.addReactor(() => {
        this.#fetchCompMatrixValues();
      }, true, true);
    }
    async init() {
      this.#fetchSDKs();
      fetchAppListData(
        this.appListData,
        this.compmatrixData,
        this.activeFromSDKs,
        this.activeToSDKs
      );
    }
    async #fetchSDKs() {
      const url = `${BASE_API_ENDPOINT}/sdks`;
      try {
        const response = await fetch(url);
        const sdks_json = await response.json();
        const sdks_data = sdks_json.data.sdks;
        let sdks = [];
        for (let i = 0; i < sdks_data.length; i++) {
          sdks.push({
            "id": sdks_data[i].id,
            "name": sdks_data[i].name
          });
        }
        this.selectableFromSDKs.setValue(structuredClone(sdks));
        this.selectableToSDKs.setValue(structuredClone(sdks));
      } catch (error) {
        console.error(error.message);
      }
    }
    async #fetchCompMatrixValues() {
      const url = `${BASE_API_ENDPOINT}/sdk-compmatrix/numbers`;
      const fromSDKs = this.activeFromSDKs.getValue().map((s) => s.id);
      const toSDKs = this.activeToSDKs.getValue().map((s) => s.id);
      let rawParamPairs = [];
      if (fromSDKs.length !== 0) {
        rawParamPairs.push(...fromSDKs.map((s) => ["from_sdks", s]));
      } else {
        rawParamPairs.push(["from_sdks", ""]);
      }
      if (toSDKs.length !== 0) {
        rawParamPairs.push(...toSDKs.map((s) => ["to_sdks", s]));
      } else {
        rawParamPairs.push(["to_sdks", ""]);
      }
      const params = new URLSearchParams(rawParamPairs);
      const paramString = params.toString();
      let numbersJSON;
      try {
        this.compmatrixData.setValue((v) => {
          v["state"] = DataState.LOADING;
        });
        const response = await fetch(`${url}?${paramString}`);
        numbersJSON = await response.json();
      } catch (error) {
        console.error(error.message);
        this.compmatrixData.setValue((v) => {
          v["state"] = DataState.ERRORED;
        });
      }
      const rawValues = numbersJSON.data.numbers;
      let normalizedValues = [];
      for (let i = 0; i < numbersJSON.data.numbers.length; i++) {
        let row = numbersJSON.data.numbers[i];
        const sum = row.reduce((partialSum, n) => partialSum + n, 0);
        let normalized = [];
        for (let j = 0; j < row.length; j++) {
          normalized.push(row[j] / sum);
        }
        normalizedValues.push(normalized);
      }
      this.compmatrixData.setValue((v) => {
        v["data"]["raw"] = rawValues;
        v["data"]["normalized"] = normalizedValues;
        v["state"] = DataState.LOADED;
      });
    }
  };
  function onDocumentLoad() {
    const app = new App();
    app.init();
  }
})();
