import { htmlToNodes } from './html.js';
import udomdiff from './udomdiff.js';

export class Widget {
    constructor(rootNodeID) {
        this.rootNode = document.getElementById(rootNodeID);
        this.nodes = [];
    }

    onStateValueChange(newValue) {
        this.updateWithValue(newValue);
    }

    updateWithValue(value) {
        this.nodes = this.createNodes(value);
        this.render();
    }

    createNodes(stateValue) {
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

export class StatefulWidget extends Widget {
    constructor(rootNode, state) {
        super(rootNode);

        this.state = state;
        this.state.addReactor((value) => { this.onStateValueChange(value); });
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

export class CompMatrixDataToggler extends StatefulWidget {
    constructor(rootNode, state) {
        super(rootNode, state);

        this.rootNode.addEventListener('change', (e) => {
            if (e.target.checked) {
                // Data should be presented as normalized.
                this.state.setValue((s) => {
                    s['active-data'] = 'normalized';
                });
            } else {
                // Data should be presented as raw.
                this.state.setValue((s) => {
                    s['active-data'] = 'raw';
                });
            }
        });
    }
}

export class SDKSelect extends StatefulWidget {
    constructor(rootNode, state) {
        super(rootNode, state);

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

    onStateValueChange(sdks) {
        for (let i = 0; i < sdks.length; i++) {
            this.idToIndexMap.set(sdks[i].id, i);
        }

        super.onStateValueChange(sdks);
    }

    createNodes(sdks) {
        let html = '';
        for (let i = 0; i < sdks.length; i++) {
            html += `<option value="${sdks[i].id}">${sdks[i].name}</option>`;
        }

        return htmlToNodes(html);
    }

    moveSelectedOptionUp() {
        const selectedID = this.selectedIndex;
        const newIndex = Math.max(selectedID - 1, 0);
        this.state.setValue((v) => {
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
        this.state.setValue((v) => {
            [v[newIndex], v[selectedID]] = [v[selectedID], v[newIndex]];
        });
        this.selectedIndex = newIndex;
    }
}

export class CompMatrix extends StatefulWidget {
    constructor(rootNode, state) {
        super(rootNode, state);
    }

    createNodes(state) {
        const headers = state['headers'];
        const from_sdks = headers['from_sdks'];
        const to_sdks = headers['to_sdks'];
        const num_from_sdks = headers['from_sdks'].length;
        const num_to_sdks = headers['to_sdks'].length;

        let html = '';
        html += '<tr>';
        html += '<th></th>';
        html += `<th colspan="${num_to_sdks + 1}">To SDK</th>`;
        html += '</tr>';
        html += '<tr>';
        html += `<th rowspan="${num_from_sdks + 2}">From SDK</th>`;
        html += '</tr>';
        html += '<tr>';
        html += '<th></th>';
        for (let i = 0; i < num_to_sdks; i++) {
            html += `<th>${to_sdks[i]}</th>`;
        }
        html += '</tr>';

        const activeData = state['active-data'];
        const presentedData = state['data'][activeData];
        for (let i = 0; i < presentedData.length; i++) {
            const rowData = presentedData[i];
            html += '<tr>';
            html += `<th>${from_sdks[i]}</th>`;
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
