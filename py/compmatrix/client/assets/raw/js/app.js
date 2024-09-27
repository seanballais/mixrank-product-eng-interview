import { BASE_API_ENDPOINT } from './constants.js';
import { DataState, fetchAppListData } from './fetching.js';
import * as interactivity from './interactivity.js';
import { State } from './state.js';
import {
    AppList,
    AppListDesc,
    Button,
    CompMatrix,
    CompMatrixDataToggler,
    SDKSelect
} from './widgets.js';

document.addEventListener('DOMContentLoaded', onDocumentLoad, false);

class App {
    constructor() {
        this.selectableFromSDKs = new State([]);
        this.activeFromSDKs = new State([]);
        
        this.selectableToSDKs = new State([]);
        this.activeToSDKs = new State([]);

        this.compmatrixData = new State({
            'data': {
                'raw': [],
                'normalized': []
            },
            'state': DataState.EMPTY,
            'active-data': 'raw',
            'selected-cell': null,
        });

        this.appListData = new State({
            'displayed-apps': [],
            'total-app-count': 0,
            'recent-batch-size': 0,
            'state': DataState.EMPTY,
            'pruned': false,
            'start-cursor': null,
            'end-cursor': null,
            'need-prev-batch-trigger': false,
            'need-next-batch-trigger': false,
        });

        this.matrixTable = new CompMatrix('compmatrix');
        this.matrixTable.batchSubscribe([
            {'refName': 'data', 'state': this.compmatrixData},
            {'refName': 'from-sdks', 'state': this.activeFromSDKs},
            {'refName': 'to-sdks', 'state': this.activeToSDKs},
            {'refName': 'app-list', 'state': this.appListData}
        ]);

        this.matrixTableDataToggler = new CompMatrixDataToggler(
            'compmatrix-data-toggle'
        );
        this.matrixTableDataToggler.subscribeTo('data', this.compmatrixData);

        this.fromSDKComboBox = new SDKSelect('from-sdk-selectables');
        this.fromSDKComboBox.subscribeTo('sdks', this.selectableFromSDKs);

        this.activeFromSDKsList = new SDKSelect('from-sdk-selected');
        this.activeFromSDKsList.subscribeTo('sdks', this.activeFromSDKs);

        this.toSDKComboBox = new SDKSelect('to-sdk-selectables');
        this.toSDKComboBox.subscribeTo('sdks', this.selectableToSDKs);

        this.activeToSDKsList = new SDKSelect('to-sdk-selected');
        this.activeToSDKsList.subscribeTo('sdks', this.activeToSDKs);

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

        this.appList = new AppList('apps-list');
        this.appList.batchSubscribe([
            {'refName': 'app-list', 'state': this.appListData},
            {'refName': 'compmatrix-data', 'state': this.compmatrixData},
            {'refName': 'from-sdks', 'state': this.activeFromSDKs},
            {'refName': 'to-sdks', 'state': this.activeToSDKs}
        ]);

        this.appListDesc = new AppListDesc('app-list-desc');
        this.appListDesc.batchSubscribe([
            {'refName': 'app-list', 'state': this.appListData},
            {'refName': 'compmatrix-data', 'state': this.compmatrixData}
        ]);

        this.fromSDKAddBtn.setOnClick(() => {
            const selectableSDKs = this.selectableFromSDKs.getValue();
            if (selectableSDKs.length > 0) {
                interactivity.moveSDKFromComboBoxToList(
                    this.fromSDKComboBox,
                    this.selectableFromSDKs,
                    this.activeFromSDKsList,
                    this.activeFromSDKs
                );
    
                this.#refetchAppListIfNeeded();
            }
        });
        this.selectedFromSDKRemoveBtn.setOnClick(() => {
            interactivity.moveSDKFromListToComboBox(
                this.fromSDKComboBox,
                this.selectableFromSDKs,
                this.activeFromSDKsList,
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
            const selectableSDKs = this.selectableToSDKs.getValue();
            if (selectableSDKs.length > 0) {
                interactivity.moveSDKFromComboBoxToList(
                    this.toSDKComboBox,
                    this.selectableToSDKs,
                    this.activeToSDKsList,
                    this.activeToSDKs
                )
    
                this.#refetchAppListIfNeeded();
            }
        });
        this.selectedToSDKRemoveBtn.setOnClick(() => {
            interactivity.moveSDKFromListToComboBox(
                this.toSDKComboBox,
                this.selectableToSDKs,
                this.activeToSDKsList,
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
        }, true, true);

        this.activeToSDKs.addReactor(() => {
            this.#fetchCompMatrixValues();
        }, true, true);
    }

    async init() {
        this.#fetchSDKs();
    }

    async #fetchSDKs() {
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
            rawParamPairs.push(...fromSDKs.map((s) => ['from_sdks', s]));
        } else {
            rawParamPairs.push(['from_sdks', '']);
        }

        if (toSDKs.length !== 0) {
            rawParamPairs.push(...toSDKs.map((s) => ['to_sdks', s]));
        } else {
            rawParamPairs.push(['to_sdks', '']);
        }

        const params = new URLSearchParams(rawParamPairs);
        const paramString = params.toString();
        let numbersJSON;
        try {
            this.compmatrixData.setValue((v) => {
                v['state'] = DataState.LOADING;
            });
            const response = await fetch(`${url}?${paramString}`);
            numbersJSON = await response.json();
        } catch (error) {
            console.error(error.message);
            this.compmatrixData.setValue((v) => {
                v['state'] = DataState.ERRORED;
            });
        }

        const rawValues = numbersJSON.data.numbers;
        let normalizedValues = [];
        for (let i = 0; i < numbersJSON.data.numbers.length; i++) {
            let row = numbersJSON.data.numbers[i];
            const sum = row.reduce((partialSum, n) => partialSum + n, 0);

            let normalized = []
            for (let j = 0; j < row.length; j++) {
                normalized.push(row[j] / sum);
            }

            normalizedValues.push(normalized);
        }
        
        this.compmatrixData.setValue((v) => {
            v['data']['raw'] = rawValues;
            v['data']['normalized'] = normalizedValues;
            v['state'] = DataState.LOADED;
        });
    }

    #refetchAppListIfNeeded() {
        const compmatrixData = this.compmatrixData.getValue();
        const selectedCell = compmatrixData['selected-cell'];
        if (selectedCell) {
            const fromSDK = selectedCell['from-sdk'];
            const toSDK = selectedCell['to-sdk'];
            if (fromSDK['id'] === null || toSDK['id'] === null) {
                // Refetch app list in case the newly-added SDK causes a
                // change in numbers to the cell. This only happens in
                // cells with a (none) SDK.
                fetchAppListData(
                    this.appListData,
                    this.compmatrixData,
                    this.activeFromSDKs,
                    this.activeToSDKs
                );
            }
        }
    }
}

function onDocumentLoad() {
    const app = new App();
    app.init();
}
