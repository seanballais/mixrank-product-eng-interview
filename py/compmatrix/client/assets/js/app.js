import { DataState } from './fetching.js';
import * as interactivity from './interactivity.js';
import { State } from './state.js';
import { Button, SDKSelect } from './widgets.js';

const BASE_API_ENDPOINT = '/api/v1';

document.addEventListener('DOMContentLoaded', onDocumentLoad, false);

class App {
    constructor() {
        this.selectableFromSDKs = new State([]);
        this.activeFromSDKs = new State([]);
        
        this.selectableToSDKs = new State([]);
        this.activeToSDKs = new State([]);

        this.compmatrixValues = new State({
            'status': DataState.EMPTY,
            'data': {
                'raw': [],
                'normalized': []
            }
        });

        this.fromSDKComboBox = new SDKSelect(
            'from-sdk-selectables',
            this.selectableFromSDKs
        );
        this.activeFromSDKsList = new SDKSelect(
            'from-sdk-selected',
            this.activeFromSDKs
        );

        this.toSDKComboBox = new SDKSelect(
            'to-sdk-selectables',
            this.selectableToSDKs
        );
        this.activeToSDKsList = new SDKSelect(
            'to-sdk-selected',
            this.activeToSDKs
        );

        this.fromSDKAddBtn = new Button('from-sdk-config-list-add-btn');
        this.selectedFromSDKRemoveBtn = new Button(
            'from-sdk-selected-remove-btn'
        );
        this.selectedFromSDKUpBtn = new Button(
            'from-sdk-selected-move-up-btn'
        );
        this.selectedFromSDKDownBtn = new Button(
            'from-sdk-selected-move-down-btn'
        );

        this.toSDKAddBtn = new Button('to-sdk-config-list-add-btn');
        this.selectedToSDKRemoveBtn = new Button('to-sdk-selected-remove-btn');
        this.selectedToSDKUpBtn = new Button('to-sdk-selected-move-up-btn');
        this.selectedToSDKDownBtn = new Button(
            'to-sdk-selected-move-down-btn'
        );

        this.fromSDKAddBtn.setOnClick(() => {
            interactivity.moveSDKFromComboBoxToList(
                this.fromSDKComboBox,
                this.selectableFromSDKs,
                this.activeFromSDKs
            );
        });
        this.selectedFromSDKRemoveBtn.setOnClick(() => {
            interactivity.moveSDKFromListToComboBox(
                this.fromSDKComboBox,
                this.activeFromSDKsList,
                this.selectableFromSDKs,
                this.activeFromSDKs
            );
        });
        this.selectedFromSDKUpBtn.setOnClick(() => {
            this.activeFromSDKsList.moveSelectedOptionUp();
        });
        this.selectedFromSDKDownBtn.setOnClick(() => {
            this.activeFromSDKsList.moveSelectedOptionDown();
        });
        
        this.toSDKAddBtn.setOnClick(() => {
            interactivity.moveSDKFromComboBoxToList(
                this.toSDKComboBox,
                this.selectableToSDKs,
                this.activeToSDKs
            )
        });
        this.selectedToSDKRemoveBtn.setOnClick(() => {
            interactivity.moveSDKFromListToComboBox(
                this.toSDKComboBox,
                this.activeToSDKsList,
                this.selectableToSDKs,
                this.activeToSDKs
            );
        });
        this.selectedToSDKUpBtn.setOnClick(() => {
            this.activeToSDKsList.moveSelectedOptionUp();
        });
        this.selectedToSDKDownBtn.setOnClick(() => {
            this.activeToSDKsList.moveSelectedOptionDown();
        });

        this.activeFromSDKs.addReactor(() => {
            this.#fetchCompMatrixValues();
        });

        this.activeToSDKs.addReactor(() => {
            this.#fetchCompMatrixValues();
        });
    }

    async init() {
        // Get the SDK IDs.
        const url = `${BASE_API_ENDPOINT}/sdks`
        try {
            const response = await fetch(url);
            const sdks_json = await response.json();
            const sdks_data = sdks_json.data.sdks;
            let sdks = [];
            for (let i = 0; i < sdks_data.length; i++) {
                sdks.push({
                    'id': sdks_data[i].id,
                    'name': sdks_data[i].name
                })
            }

            this.selectableFromSDKs.setValue(structuredClone(sdks));
            this.selectableToSDKs.setValue(structuredClone(sdks));
        } catch (error) {
            console.error(error.message);
        }
    }

    async #fetchCompMatrixValues() {
        const url = `${BASE_API_ENDPOINT}/sdk-compmatrix/numbers`;
        const fromSDKs = this.activeFromSDKs.getValue().map((s) => s.id);
        const toSDKs = this.activeToSDKs.getValue().map((s) => s.id);

        let rawParamPairs = [];
        if (fromSDKs.length !== 0) {
            rawParamPairs.push(...fromSDKs.map((s) => ['from_sdks', s.id]));
        } else {
            rawParamPairs.push(['from_sdks', '']);
        }

        if (toSDKs.length !== 0) {
            rawParamPairs.push(...toSDKs.map((s) => ['to_sdks', s.id]));
        } else {
            rawParamPairs.push(['to_sdks', '']);
        }

        const params = new URLSearchParams(rawParamPairs);
        const paramString = params.toString();
        try {
            const response = await fetch(`${url}?${paramString}`);
            const numbersJSON = await response.json();
            console.log(numbersJSON);
        } catch (error) {
            console.error(error.message);
        }
    }
}

function onDocumentLoad() {
    const app = new App();
    app.init();
}
