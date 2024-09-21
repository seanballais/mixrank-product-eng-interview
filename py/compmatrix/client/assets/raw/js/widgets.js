import { DataState } from './fetching.js';
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

        this.cellToSDKIDs = {};
    }

    update() {
        // Reset. An update may result in some cells being removed.
        this.cellToSDKIDs = {};

        super.update();

        const data = this.states['data'].getValue();
        const dataState = data['state'];

        if (dataState == DataState.LOADED) {
            for (const [key, sdks] of Object.entries(this.cellToSDKIDs)) {
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
        html += `<th rowspan="${numFromSDKsHeaders + 2}">From SDK</th>`;
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

                    this.cellToSDKIDs[id] = {
                        'from-sdk': fromSDKHeaders[i]['id'],
                        'to-sdk': toSDKHeaders[j]['id']
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
    }

    // TODO: - Find a way to load the next batch of apps when a certain div
    //         becomes visible.
    //       - Allow updating the app list when a cell in the matrix is
    //         clicked.

    createNodes() {
        const appList = this.states['appList'].getValue();

        let html = '';
        for (let i = 0; i < appList['apps'].length; i++) {
            const app = appList['apps'][i];
            html += '<div>';
            html += '  <div>';
            html += `    <img src=${app['artwork_large_url']}/>`
            html += '  </div>';
            html += '  <div>';
            html += `    <h1>${app['name']}</h1>`;
            html += '    <p>'
            html += `      <a href=${app['company_url']}">`
            html += `      ${app['seller_name']}`;
            html += '      </a>'
            html += '    </p>';
            html += '    <p>';
            html += '      <span class="fa-solid fa-star"></span>';
            html += `      ${app['rating']}`
            html += '    </p>';
            html += '  </div>';
            html += '</div>';
        }

        return htmlToNodes(html);
    }
}
