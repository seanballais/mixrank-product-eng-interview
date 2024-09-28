import {
    DataState,
    fetchSDKs,
    fetchCompMatrixValues,
    refetchAppListIfNeeded
} from './fetching.js';
import * as interactivity from './interactivity.js';
import { State } from './state.js';
import {
    AppList,
    AppListDesc,
    Button,
    CompMatrix,
    CompMatrixDataToggler,
    SDKSelect
} from './widgets/widgets.js';

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
            'is-loading-new-batch': false,
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
    
                refetchAppListIfNeeded(
                    this.appListData,
                    this.compmatrixData,
                    this.activeFromSDKs,
                    this.activeToSDKs
                );
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
    
                refetchAppListIfNeeded(
                    this.appListData,
                    this.compmatrixData,
                    this.activeFromSDKs,
                    this.activeToSDKs
                );
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
            fetchCompMatrixValues(
                this.compmatrixData,
                this.activeFromSDKs,
                this.activeToSDKs
            );
        }, true, true);

        this.activeToSDKs.addReactor(() => {
            fetchCompMatrixValues(
                this.compmatrixData,
                this.activeFromSDKs,
                this.activeToSDKs
            );
        }, true, true);
    }

    async init() {
        fetchSDKs(this.selectableFromSDKs, this.selectableToSDKs);
    }
}

function onDocumentLoad() {
    const app = new App();
    app.init();
}
