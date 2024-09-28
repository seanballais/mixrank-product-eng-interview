import { Widget } from "./base.js";

export class AppListDesc extends Widget {
    constructor(rootNode) {
        super(rootNode);
    }

    createHTML() {
        const compmatrixData = this.states['compmatrix-data'].getValue();

        let html = '<p>';
        if (compmatrixData['selected-cell'] === null) {
            html += 'Select a cell in the competitive matrix to get started.';
        } else {
            const fromSDK = compmatrixData['selected-cell']['from-sdk'];
            const toSDK = compmatrixData['selected-cell']['to-sdk'];

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

        return html;
    }
}
