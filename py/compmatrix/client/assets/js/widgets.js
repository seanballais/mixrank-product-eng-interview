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

export class Table extends StatefulWidget {
    constructor(rootNode, state) {
        super(rootNode, state);
    }

    createNodes(state) {
        const headers = state['headers'];

        let html = '';
        html += '<tbody>'
        html += '<tr><th></th>';
        for (let i = 0; i < headers['to_sdks'].length; i++) {
            html += `<th>${headers['to_sdks'][i]}</th>`;
        }
        html += '</tr>';

        const presentedData = state['data']['raw'];
        for (let i = 0; i < presentedData.length; i++) {
            const rowData = presentedData[i];
            html += '<tr>';
            html += `<th>${headers['from_sdks'][i]}</th>`;
            for (let j = 0; j < rowData.length; j++) {
                html += `<td>${rowData[j]}</td>`
            }
            html += '</tr>';
        }

        html += '</tbody>';

        return htmlToNodes(html);
    }
}
