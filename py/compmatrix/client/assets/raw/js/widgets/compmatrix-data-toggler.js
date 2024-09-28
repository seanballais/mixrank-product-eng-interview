import { Widget } from "./base";

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
