import { MAX_APP_LIST_SIZE } from './constants.js';
import { DataState, fetchAppListData, FetchDirection } from './fetching.js';
import { htmlToNodes } from './html.js';
import udomdiff from './udomdiff.js';

export class Widget {
    constructor(rootNodeID) {
        this.rootNode = document.getElementById(rootNodeID);
        this.nodes = [];
        this.states = {}
    }

    subscribeTo(refName, state) {
        this.states[refName] = state;
        state.addReactor(() => { this.update(); });
    }

    batchSubscribe(states) {
        for (let i = 0; i < states.length; i++) {
            const state = states[i];
            this.states[state['refName']] = state['state'];
            state.state.addReactor(() => { this.update(); }, false, false);
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
        udomdiff(
            this.rootNode,
            [...this.rootNode.childNodes],
            [...this.nodes],
            (o) => o
        );
    }
}

export class Button extends Widget {
    constructor(rootNode) {
        super(rootNode);
    }

    setOnClick(f) {
        this.rootNode.addEventListener('click', f);
    }
}

export class CompMatrixDataToggler extends Widget {
    constructor(rootNode) {
        super(rootNode);

        this.rootNode.addEventListener('change', (e) => {
            if (e.target.checked) {
                // Data should be presented as normalized.
                this.states['data'].setValue((s) => {
                    s['active-data'] = 'normalized';
                });
            } else {
                // Data should be presented as raw.
                this.states['data'].setValue((s) => {
                    s['active-data'] = 'raw';
                });
            }
        });
    }
}

export class SDKSelect extends Widget {
    constructor(rootNode) {
        super(rootNode);

        this.idToIndexMap = new Map();
    }

    get value() {
        return Number(this.rootNode.value);
    }

    get selectedIndex() {
        const index = this.idToIndexMap.get(this.value);
        if (index === undefined) {
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
        const sdks = this.states['sdks'].getValue();
        for (let i = 0; i < sdks.length; i++) {
            this.idToIndexMap.set(sdks[i].id, i);
        }

        super.update();
    }

    createNodes() {
        const sdks = this.states['sdks'].getValue();

        let html = '';
        for (let i = 0; i < sdks.length; i++) {
            const sdk = sdks[i];
            html += `<option value="${sdk.id}">${sdk.name}</option>`;
        }

        return htmlToNodes(html);
    }

    moveSelectedOptionUp() {
        const selectedID = this.selectedIndex;
        const newIndex = Math.max(selectedID - 1, 0);
        this.states['sdks'].setValue((v) => {
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
        this.states['sdks'].setValue((v) => {
            [v[newIndex], v[selectedID]] = [v[selectedID], v[newIndex]];
        });
        this.selectedIndex = newIndex;
    }
}

export class CompMatrix extends Widget {
    constructor(rootNode) {
        super(rootNode);

        this.cellToSDKs = {};
    }

    update() {
        // Reset. An update may result in some cells being removed.
        this.cellToSDKs = {};

        super.update();

        const data = this.states['data'].getValue();
        const dataState = data['state'];

        if (dataState == DataState.LOADED) {
            for (const [key, sdks] of Object.entries(this.cellToSDKs)) {
                const cell = document.getElementById(key);
                cell.addEventListener('click', () => {
                    this.states['data'].setValue((v) => {
                        v['selected-cell']['from-sdk'] = sdks['from-sdk'];
                        v['selected-cell']['to-sdk'] = sdks['to-sdk'];
                    });
                });
            }
        }
    }

    createNodes() {
        const data = this.states['data'].getValue();
        const dataState = data['state'];

        let html = '';
        const fromSDKData = this.states['from-sdks'].getValue();
        const toSDKData = this.states['to-sdks'].getValue();

        const fromSDKHeaders = [...fromSDKData];
        const toSDKHeaders = [...toSDKData];

        fromSDKHeaders.push({'id': null, 'name': '(none)'});
        toSDKHeaders.push({'id': null, 'name': '(none)'});

        const numFromSDKsHeaders = fromSDKHeaders.length;
        const numToSDKsHeaders = toSDKHeaders.length;

        html += '<tr>';
        html += '<th></th>';
        html += `<th colspan="${numToSDKsHeaders + 1}">To SDK</th>`;
        html += '</tr>';
        html += '<tr>';
        html += `<th rowspan="${numFromSDKsHeaders + 2}">`;
        html += '<span>From SDK</span>';
        html += '</th>';
        html += '</tr>';

        if (dataState == DataState.LOADED) {
            html += '<tr>';
            html += '<th></th>';
            for (let i = 0; i < numToSDKsHeaders; i++) {
                html += `<th>${toSDKHeaders[i]['name']}</th>`;
            }
            html += '</tr>';

            const activeData = data['active-data'];
            const presentedData = data['data'][activeData];
            const percentageData = data['data']['normalized']
            for (let i = 0; i < presentedData.length; i++) {
                const rowData = presentedData[i];
                html += '<tr>';
                html += `<th>${fromSDKHeaders[i]['name']}</th>`;
                for (let j = 0; j < rowData.length; j++) {
                    let cellData = rowData[j];
                    if (activeData == 'normalized') {
                        cellData = `${(cellData * 100).toFixed(0)}%`;
                    }

                    const opacity = percentageData[i][j];

                    const id = `cmc-${i}${j}`;
                    const colour = `hsla(0, 80%, 55%, ${opacity * 100}%)`
                    const style = `background-color: ${colour}`;
                    html += `<td id="${id}" style="${style}">${cellData}</td>`;

                    this.cellToSDKs[id] = {
                        'from-sdk': fromSDKHeaders[i],
                        'to-sdk': toSDKHeaders[j]
                    };
                }
                html += '</tr>';
            }
        } else if (dataState == DataState.LOADING) {
            html += '<tr>';
            html += '<td>';
            html += '<span class="fas fa-circle-notch fa-spin"></span>'
            html += '</td>';
            html += '</tr>';
        }

        return htmlToNodes(html);
    }
}

export class AppList extends Widget {
    constructor(rootNode) {
        super(rootNode);

        this.prevBatchTriggerObserver = null;
        this.nextBatchTriggerObserver = null;

        this.isBatchLoading = false;
    }

    update() {
        super.update();

        const appList = this.states['app-list'].getValue();
        const observerOptions = {
            root: this.rootNode,
        };

        if (appList['need-prev-batch-trigger']) {
            const callback = (entries, observer) => {
                entries.forEach(async (entry) => {
                    // Guard check to make sure we don't keep on loading a
                    // batch of apps when we already previously initiated this
                    // trigger and we're already loading things. Not exactly an
                    // ideal solution, since this will also block the other
                    // trigger from calling its callback (which also helps make
                    // sure we don't screw up the app list if we already
                    // exceeded the maximum number of apps allowed to be loaded
                    // in). However, it should work for the time being. This
                    // might end up being enough, but we might have to change
                    // if need be depending on feedback.
                    if (
                        entry &&
                        entry.isIntersecting &&
                        !this.isBatchLoading
                    ) {
                        this.isBatchLoading = true;

                        await fetchAppListData(
                            this.states['app-list'],
                            this.states['compmatrix-data'],
                            this.states['from-sdks'],
                            this.states['to-sdks'],
                            appList['start-cursor'],
                            FetchDirection.PREVIOUS
                        );

                        // If we pruned our current displayed apps, then we
                        // need to scroll down to where our view was before we
                        // loaded in a new batch of apps.
                        if (appList['pruned'] && recentBatchSize !== 0) {
                            this.rootNode.scrollBy(
                                0,
                                baseScrollAmount + prevTriggerHeight
                            );
                        }

                        this.isBatchLoading = false;
                    } 
                });
            };
            this.prevBatchTriggerObserver = new IntersectionObserver(
                callback,
                observerOptions
            );
            const trigger = document.getElementById('app-prev-batch-trigger');
            this.prevBatchTriggerObserver.observe(trigger);
        }

        if (appList['need-next-batch-trigger']) {
            const callback = (entries, observer) => {
                for (let i = 0; i < entries.length; i++) {
                    const e = entries[i];
                    // Guard check to make sure we don't keep on loading a
                    // batch of apps when we already previously initiated this
                    // trigger and we're already loading things. Not exactly an
                    // ideal solution, since this will also block the other
                    // trigger from calling its callback (which also helps make
                    // sure we don't screw up the app list if we already
                    // exceeded the maximum number of apps allowed to be loaded
                    // in). However, it should work for the time being. This
                    // might end up being enough, but we might have to change
                    // if need be depending on feedback.
                    if (e && e.isIntersecting && !this.isBatchLoading) {
                        this.#runBatchTriggerEvent(
                            appList['end-cursor'],
                            FetchDirection.NEXT
                        );
                    }
                }
            };
            this.nextBatchTriggerObserver = new IntersectionObserver(
                callback,
                observerOptions
            );
            const trigger = document.getElementById('app-next-batch-trigger');
            this.nextBatchTriggerObserver.observe(trigger);
        }
    }

    createNodes() {
        const appList = this.states['app-list'].getValue();

        let html = '';

        html += '<ol id="apps-list-items">';

        if (appList['need-prev-batch-trigger']) {
            html += '<li id="app-prev-batch-trigger" class="batch-trigger">';
            html += '    <span class="fas fa-circle-notch fa-spin"></span>';
            html += '</li>';
        }

        for (let i = 0; i < appList['displayed-apps'].length; i++) {
            const app = appList['displayed-apps'][i];
            html += '<li class="app-card">';
            html += '  <div class="app-card-icon">';
            html += `    <img src=${app['artwork_large_url']}/>`
            html += '  </div>';
            html += '  <div class="app-card-info">';
            html += `    <h1>${app['name']}</h1>`;
            html += '    <p class="app-card-info-company">'
            html += `      <a href=${app['company_url']}">`
            html += `      ${app['seller_name']}`;
            html += '      </a>'
            html += '    </p>';
            html += '    <p>';
            html += '      <span class="fa-solid fa-star app-rating-icon">';
            html += '      </span>';
            html += `      ${app['rating'].toFixed(2)}`
            html += '    </p>';
            html += '  </div>';
            html += '</li>';
        }

        if (appList['need-next-batch-trigger']) {
            html += '<li id="app-next-batch-trigger" class="batch-trigger">';
            html += '    <span class="fas fa-circle-notch fa-spin"></span>';
            html += '</li>';
        }
        
        html += '</ol>';

        return htmlToNodes(html);
    }

    async #runBatchTriggerEvent(cursor, fetchDirection) {
        const appList = this.states['app-list'].getValue();
        const recentBatchSize = appList['recent-batch-size'];
        
        this.isBatchLoading = true;

        await fetchAppListData(
            this.states['app-list'],
            this.states['compmatrix-data'],
            this.states['from-sdks'],
            this.states['to-sdks'],
            cursor,
            fetchDirection
        );

        // If we pruned our current displayed apps, then we need to scroll up
        // or down to where our view was before we loaded in a new batch of
        // apps. Note that, prior to scrolling, we're at the either ends of
        // the app list, before we initially scrolled towards the triggers.
        if (appList['pruned'] && recentBatchSize !== 0) {
            // To compute the amount of scrolling needed, we just need to get
            // the total height of occupied by the new batch of apps in the app
            // list.
            const list = document.getElementById('apps-list-items');
            const loadedApps = [...list.children];
            const newApps = (
                fetchDirection == FetchDirection.PREVIOUS
                ? loadedApps.slice(0, recentBatchSize + 1)
                : loadedApps.slice(-recentBatchSize - 1)
            );
            const listStyle = window.getComputedStyle(list);
            
            let scrollHeight = 0;

            // Get the total height occupied by just the app cards first.
            if (newApps.length > 0) {
                // We should only be adding in the height of each row that only
                // contains the new apps (note that some rows might include
                // apps that are not part of the new batch) since they make
                // new rows, and not by each card.
                //
                // NOTE: At the moment, we won't be considering margins and
                //       paddings in the computations since the app cards
                //       don't set those yet. Maybe at a later time, we might
                //       have to include them. However, for now, YAGNI.
                const listBounds = list.getBoundingClientRect();
                const rowStartXPos = listBounds['x'];
                
                let numRows = 0;

                for (let i = 0; i < newApps.length; i++) {
                    const cardBounds = newApps[i].getBoundingClientRect();
                    if (cardBounds['x'] == rowStartXPos) {
                        // This indicates that a new row has started.
                        scrollHeight += cardBounds['height'];
                        numRows++;
                    }
                }

                // And let's add in the heights occupied by the row gaps of the
                // new batch of apps. This does not include the gap between
                // the app cards and triggers.
                const rowGap = listStyle.getPropertyValue('row-gap');
                const rowGapSize = parseInt(rowGap);
                scrollHeight += rowGapSize * (numRows - 1);

                // Let's reduce the offset just a bit more. This handles the
                // case where the first pruning may result in the former
                // topmost or bottommost row in the app list from being
                // partially covered after scrolling. This is a temporary hack,
                // and the ideal fix may involve computing the original scroll
                // position. However, in the interest of time, we'll use this
                // hack for now.
                scrollHeight -= rowGapSize * 3.5;
            }

            // We have to negate the scroll height since we have to scroll up
            // if we loaded in a new batch of apps at the end of the list.
            if (fetchDirection === FetchDirection.NEXT) {
                scrollHeight = -scrollHeight;
            }

            // We're using scrollBy() instead of scrollTo() (which would also
            // change our scroll computations) because the latter resets the
            // scrollbar to the top before scrolling down to the location we
            // want to scroll to, which wrongfully triggers the topmost batch
            // trigger. Using the former is not exactly ideal and is arguably
            // less precise, but it does not result in the aforementioned
            // issues and the effect are still within acceptable thresholds.
            this.rootNode.scrollBy(0, scrollHeight);
        }

        this.isBatchLoading = false;
    }
}

export class AppListDesc extends Widget {
    constructor(rootNode) {
        super(rootNode);
    }

    createNodes() {
        const appList = this.states['app-list'].getValue();

        let html = '<p>';
        if (appList['displayed-apps'].length == 0) {
            html += 'No apps loaded in yet.';
        } else {
            const fromSDK = appList['sdks']['from-sdk'];
            const toSDK = appList['sdks']['to-sdk'];

            let fromSDKName = '';
            if (fromSDK === null) {
                fromSDKName = '(none)';
            } else {
                fromSDKName = fromSDK['name'];
            }

            let toSDKName = '';
            if (toSDK === null) {
                toSDKName = '(none)';
            } else {
                toSDKName = toSDK['name'];
            }

            html += `Migrated from ${fromSDKName} to ${toSDKName}.`;
        }
        html += '</p>'

        return htmlToNodes(html);
    }
}
