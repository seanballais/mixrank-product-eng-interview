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
            state.state.addReactor(() => { this.update(); }, false);
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
        return this.idToIndexMap.get(this.value);
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
    }

    createNodes() {
        const data = this.states['data'].getValue();
        const fromSDKData = this.states['from-sdks'].getValue();
        const toSDKData = this.states['to-sdks'].getValue();

        const fromSDKHeaders = [...fromSDKData];
        const toSDKHeaders = [...toSDKData];

        fromSDKHeaders.push({'id': null, 'name': '(none)'});
        toSDKHeaders.push({'id': null, 'name': '(none)'});

        const numFromSDKsHeaders = fromSDKHeaders.length;
        const numToSDKsHeaders = toSDKHeaders.length;

        let idToSDKs = {};

        let html = '';
        html += '<tr>';
        html += '<th></th>';
        html += `<th colspan="${numToSDKsHeaders + 1}">To SDK</th>`;
        html += '</tr>';
        html += '<tr>';
        html += `<th rowspan="${numFromSDKsHeaders + 2}">From SDK</th>`;
        html += '</tr>';
        html += '<tr>';
        html += '<th></th>';
        for (let i = 0; i < numToSDKsHeaders; i++) {
            html += `<th>${toSDKHeaders[i]['name']}</th>`;
        }
        html += '</tr>';

        const activeData = data['active-data'];
        const presentedData = data['data'][activeData];
        for (let i = 0; i < presentedData.length; i++) {
            const rowData = presentedData[i];
            html += '<tr>';
            html += `<th>${fromSDKHeaders[i]['name']}</th>`;
            for (let j = 0; j < rowData.length; j++) {
                let cellData = rowData[j];
                if (activeData == 'normalized') {
                    cellData = `${(cellData * 100).toFixed(0)}%`;
                }

                html += `<td>${cellData}</td>`
            }
            html += '</tr>';
        }

        return htmlToNodes(html);
    }
}

export class AppList extends Widget {
    constructor(rootNode) {
        super(rootNode);
    }

    createNodes() {
        
    }
}
