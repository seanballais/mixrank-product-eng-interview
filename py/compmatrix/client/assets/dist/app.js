(() => {
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

  // py/compmatrix/client/assets/raw/js/interactivity.js
  function moveSDKFromComboBoxToList(comboBox, selectableSDKs, activeSDKs) {
    const selectables = selectableSDKs.getValue();
    if (selectables.length > 0) {
      const selectedIndex = comboBox.selectedIndex;
      activeSDKs.setValue((v) => {
        v.push(selectableSDKs.getValue()[selectedIndex]);
      });
      selectableSDKs.setValue((v) => {
        v.splice(selectedIndex, 1);
      });
      const newSelectedIndex = Math.min(
        selectedIndex,
        comboBox.options.length - 1
      );
      comboBox.selectedIndex = newSelectedIndex;
    }
  }
  function moveSDKFromListToComboBox(comboBox, activeSDKsList, selectableSDKs, activeSDKs) {
    const actives = activeSDKs.getValue();
    if (actives.length > 0) {
      const activeSelectedIndex = activeSDKsList.selectedIndex;
      const comboBoxSelectedIndex = comboBox.selectedIndex;
      let comboBoxIndexOffset = 0;
      const comboBoxSDKName = selectableSDKs.getValue()[comboBoxSelectedIndex].name;
      const activeSDKName = activeSDKs.getValue()[activeSelectedIndex].name;
      if (comboBoxSDKName.toLowerCase() >= activeSDKName.toLowerCase() && comboBoxSDKName > activeSDKName) {
        comboBoxIndexOffset = 1;
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
      const newCBSelIndex = comboBoxSelectedIndex + comboBoxIndexOffset;
      comboBox.selectedIndex = newCBSelIndex;
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
      return this.idToIndexMap.get(this.value);
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
      this.cellToSDKIDs = {};
    }
    update() {
      this.cellToSDKIDs = {};
      super.update();
      const data = this.states["data"].getValue();
      const dataState = data["state"];
      if (dataState == DataState.LOADED) {
        for (const [key, sdks] of Object.entries(this.cellToSDKIDs)) {
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
      html += `<th rowspan="${numFromSDKsHeaders + 2}">From SDK</th>`;
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
        for (let i = 0; i < presentedData.length; i++) {
          const rowData = presentedData[i];
          html += "<tr>";
          html += `<th>${fromSDKHeaders[i]["name"]}</th>`;
          for (let j = 0; j < rowData.length; j++) {
            let cellData = rowData[j];
            if (activeData == "normalized") {
              cellData = `${(cellData * 100).toFixed(0)}%`;
            }
            const id = `cmc-${i}${j}`;
            html += `<td id=${id}>${cellData}</td>`;
            this.cellToSDKIDs[id] = {
              "from-sdk": fromSDKHeaders[i]["id"],
              "to-sdk": toSDKHeaders[j]["id"]
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
    }
    // TODO: - Find a way to load the next batch of apps when a certain div
    //         becomes visible.
    //       - Allow updating the app list when a cell in the matrix is
    //         clicked.
    createNodes() {
      const appList = this.states["appList"].getValue();
      let html = "";
      for (let i = 0; i < appList["apps"].length; i++) {
        const app = appList["apps"][i];
        html += "<div>";
        html += "  <div>";
        html += `    <img src=${app["artwork_large_url"]}/>`;
        html += "  </div>";
        html += "  <div>";
        html += `    <h1>${app["name"]}</h1>`;
        html += "    <p>";
        html += `      <a href=${app["company_url"]}">`;
        html += `      ${app["seller_name"]}`;
        html += "      </a>";
        html += "    </p>";
        html += "    <p>";
        html += '      <span class="fa-solid fa-star"></span>';
        html += `      ${app["rating"]}`;
        html += "    </p>";
        html += "  </div>";
        html += "</div>";
      }
      return htmlToNodes(html);
    }
  };

  // py/compmatrix/client/assets/raw/js/app.js
  var BASE_API_ENDPOINT = "/api/v1";
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
        "apps": [],
        "start-cursor": null,
        "end-cursor": null
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
      this.appList.subscribeTo("appList", this.appListData);
      this.fromSDKAddBtn.setOnClick(() => {
        moveSDKFromComboBoxToList(
          this.fromSDKComboBox,
          this.selectableFromSDKs,
          this.activeFromSDKs
        );
      });
      this.selectedFromSDKRemoveBtn.setOnClick(() => {
        moveSDKFromListToComboBox(
          this.fromSDKComboBox,
          this.activeFromSDKsList,
          this.selectableFromSDKs,
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
          this.activeToSDKs
        );
      });
      this.selectedToSDKRemoveBtn.setOnClick(() => {
        moveSDKFromListToComboBox(
          this.toSDKComboBox,
          this.activeToSDKsList,
          this.selectableToSDKs,
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
        this.#fetchNewAppList();
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
      this.#fetchNewAppList();
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
    async #fetchNewAppList() {
      const url = `${BASE_API_ENDPOINT}/sdk-compmatrix/apps`;
      const compmatrixData = this.compmatrixData.getValue();
      const fromSDKID = compmatrixData["selected-cell"]["from-sdk"];
      const toSDKID = compmatrixData["selected-cell"]["to-sdk"];
      const activeFromSDKs = this.activeFromSDKs.getValue();
      const activeToSDKs = this.activeToSDKs.getValue();
      const otherFromSDKIDs = activeFromSDKs.filter((s) => {
        if (fromSDKID !== null) {
          return s.id != fromSDKID.id;
        }
        return true;
      });
      const otherToSDKIDs = activeToSDKs.filter((s) => {
        if (toSDKID !== null) {
          return s.id != toSDKID.id;
        }
        return true;
      });
      let rawParamPairs = [];
      if (fromSDKID !== null) {
        rawParamPairs.push(["from_sdk", fromSDKID]);
      } else if (otherFromSDKIDs.length !== 0) {
        rawParamPairs.push(
          ...otherFromSDKIDs.map((s) => ["other_from_sdks", s["id"]])
        );
      }
      if (toSDKID !== null) {
        rawParamPairs.push(["to_sdk", toSDKID]);
      } else if (otherToSDKIDs.length !== 0) {
        rawParamPairs.push(
          ...otherToSDKIDs.map((s) => ["other_to_sdks", s["id"]])
        );
      }
      rawParamPairs.push(["count", 50]);
      const params = new URLSearchParams(rawParamPairs);
      const paramString = params.toString();
      let appsJSON;
      try {
        const response = await fetch(`${url}?${paramString}`);
        appsJSON = await response.json();
      } catch (error) {
        console.error(error.message);
      }
      this.appListData.setValue((v) => {
        v["apps"] = [];
        for (let i = 0; i < appsJSON["data"]["apps"].length; i++) {
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
          v["apps"].push({
            "name": app["name"],
            "seller_name": app["seller_name"],
            "company_url": companyURL,
            "artwork_large_url": app["artwork_large_url"],
            "rating": rating
          });
        }
        v["start-cursor"] = appsJSON["data"]["start_cursor"];
        v["end-cursor"] = appsJSON["data"]["end_cursor"];
      });
    }
  };
  function onDocumentLoad() {
    const app = new App();
    app.init();
  }
})();
