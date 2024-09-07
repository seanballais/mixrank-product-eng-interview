import { htmlToNodes } from './html.js';
import udomdiff from './udomdiff.js';

export class Widget {
    constructor(rootNodeID) {
        this.rootNode = document.getElementById(rootNodeID);
        this.nodes = [];
    }

    init() {}

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

export class Button extends Widget {
    constructor(rootNode) {
        super(rootNode);
    }

    setOnClick(f) {
        this.rootNode.addEventListener('click', f);
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
}
