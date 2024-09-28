import { Widget } from "./base.js";

export class Button extends Widget {
    constructor(rootNode) {
        super(rootNode);
    }

    setOnClick(f) {
        this.rootNode.addEventListener('click', f);
    }
}
