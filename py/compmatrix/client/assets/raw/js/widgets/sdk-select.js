import { Widget } from './base.js';

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

    createHTML() {
        const sdks = this.states['sdks'].getValue();

        let html = '';
        for (let i = 0; i < sdks.length; i++) {
            const sdk = sdks[i];
            html += `<option value="${sdk.id}">${sdk.name}</option>`;
        }

        return html;
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
