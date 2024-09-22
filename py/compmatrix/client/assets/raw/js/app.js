import { DataState } from './fetching.js';
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

const BASE_API_ENDPOINT = '/api/v1';

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
            'selected-cell': {
                'from-sdk': null,
                'to-sdk': null
            }
        });

        this.appListData = new State({
            'apps': [],
            'sdks': {
                'from-sdk': null,
                'to-sdk': null
            },
            'start-cursor': null,
            'end-cursor': null
        });

        this.matrixTable = new CompMatrix('compmatrix');
        this.matrixTable.batchSubscribe([
            {'refName': 'data', 'state': this.compmatrixData},
            {'refName': 'from-sdks', 'state': this.activeFromSDKs},
            {'refName': 'to-sdks', 'state': this.activeToSDKs}
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
        this.appList.subscribeTo('appList', this.appListData);

        this.appListDesc = new AppListDesc('app-list-desc');
        this.appListDesc.subscribeTo('appList', this.appListData);

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

        this.compmatrixData.addReactor(() => {
            this.#fetchNewAppList();
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
        this.#fetchNewAppList();
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

    async #fetchNewAppList() {
        const url = `${BASE_API_ENDPOINT}/sdk-compmatrix/apps`;

        const compmatrixData = this.compmatrixData.getValue();
        const fromSDK = compmatrixData['selected-cell']['from-sdk'];
        const toSDK = compmatrixData['selected-cell']['to-sdk'];

        const activeFromSDKs = this.activeFromSDKs.getValue();
        const activeToSDKs = this.activeToSDKs.getValue();

        const otherFromSDKIDs = activeFromSDKs.filter((s) => {
            if (fromSDK !== null) {
                return s.id != fromSDK['id'];
            }

            return true;
        });
        const otherToSDKIDs = activeToSDKs.filter((s) => {
            if (toSDK !== null) {
                return s.id != toSDK['id'];
            }

            return true;
        });

        let rawParamPairs = [];
        if (fromSDK !== null) {
            rawParamPairs.push(['from_sdk', fromSDK['id']]);
        } else if (otherFromSDKIDs.length !== 0) {
            // We can only specify `other_from_sdks` if `from_sdk` is
            // unspecified.
            rawParamPairs.push(
                ...otherFromSDKIDs.map((s) => ['other_from_sdks', s['id']])
            );
        }

        if (toSDK !== null) {
            rawParamPairs.push(['to_sdk', toSDK['id']]);
        } else if (otherToSDKIDs.length !== 0) {
            // We can only specify `other_to_sdks` if `to_sdk` is unspecified.
            rawParamPairs.push(
                ...otherToSDKIDs.map((s) => ['other_to_sdks', s['id']])
            );
        }

        rawParamPairs.push(['count', 50]);

        const params = new URLSearchParams(rawParamPairs);
        const paramString = params.toString();
        let appsJSON;
        try {
            const response = await fetch(`${url}?${paramString}`);
            appsJSON = await response.json();
        } catch (error) {
            console.error(error.message);
        }

        this.appListData.setValue((v) => {
            // TODO: - Figure out a way to know whether we should clear the
            //         app list or just prepend/append it.
            //       - Use Intersection Observer to load more apps. Use a div
            //         as a trigger. However, if we reached the max number of
            //         apps, we don't load the trigger. If we reached a certain
            //         threshold of apps, we put a div trigger at the start of
            //         the list after removing excess apps.
            v['apps'] = [];

            for (let i = 0; i < appsJSON['data']['apps'].length; i++) {
                const app = appsJSON['data']['apps'][i];

                let companyURL = null;
                if (app['company_url'] != '') {
                    companyURL = app['company_url'];
                }

                let totalRatings = app['five_star_ratings'];
                totalRatings += app['four_star_ratings'];
                totalRatings += app['three_star_ratings'];
                totalRatings += app['two_star_ratings'];
                totalRatings += app['one_star_ratings'];

                let rating = 0;
                rating += (app['five_star_ratings'] * 5);
                rating += (app['four_star_ratings'] * 4);
                rating += (app['three_star_ratings'] * 3);
                rating += (app['two_star_ratings'] * 2);
                rating += (app['one_star_ratings'] * 1);
                rating /= totalRatings;

                v['apps'].push({
                    'name': app['name'],
                    'seller_name': app['seller_name'],
                    'company_url': companyURL,
                    'artwork_large_url': app['artwork_large_url'],
                    'rating': rating
                })
            }

            v['sdks']['from-sdk'] = fromSDK;
            v['sdks']['to-sdk'] = toSDK;
            v['start-cursor'] = appsJSON['data']['start_cursor'];
            v['end-cursor'] = appsJSON['data']['end_cursor'];
        });
    }
}

function onDocumentLoad() {
    const app = new App();
    app.init();
}
