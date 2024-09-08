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
            this.#moveSDKFromComboBoxToList(
                this.fromSDKComboBox,
                this.selectableFromSDKs,
                this.activeFromSDKs
            );
        });
        this.selectedFromSDKRemoveBtn.setOnClick(() => {
            this.#moveSDKFromListToComboBox(
                this.fromSDKComboBox,
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
            this.#moveSDKFromComboBoxToList(
                this.toSDKComboBox,
                this.selectableToSDKs,
                this.activeToSDKs
            )
        });
        this.selectedToSDKRemoveBtn.setOnClick(() => {
            this.#moveSDKFromListToComboBox(
                this.toSDKComboBox,
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

    #moveSDKFromComboBoxToList(comboBox, selectableSDKs, activeSDKs) {
        const selectedIndex = comboBox.selectedIndex;
        activeSDKs.setValue((v) => {
            v.push(selectableSDKs.getValue()[selectedIndex]);
        });
        selectableSDKs.setValue((v) => { v.splice(selectedIndex, 1); });

        const newSelectedIndex = Math.min(
            selectedIndex,
            comboBox.options.length - 1
        );
        comboBox.selectedIndex = newSelectedIndex;
    }

    #moveSDKFromListToComboBox(comboBox, selectableSDKs, activeSDKsList) {
        const activeSelectedIndex = activeSDKsList.selectedIndex;
        const comboBoxSelectedIndex = comboBox.selectedIndex;

        let comboBoxIndexOffset = 0;
        const comboBoxSDKName = selectableSDKs
                                    .getValue()[comboBoxSelectedIndex]
                                    .name;
        const activeSDKName = activeSDKsList
                                    .getValue()[activeSelectedIndex]
                                    .name;
        if (
            comboBoxSDKName.toLowerCase() >= activeSDKName.toLowerCase()
            && comboBoxSDKName > activeSDKName
        ) {
            // The SDK removed from the active list of From SDKs will be
            // placed behind the currently selected SDK in the From SDK
            // combo box. So, we need to offset the new combo box index
            // by 1. Second condition handles the edge case where two SDKs
            // have the same names in lowercase, but are technically
            // different when their original cases.
            comboBoxIndexOffset = 1;
        }
        
        selectableSDKs.setValue((v) => {
            v.push(activeSDKsList.getValue()[activeSelectedIndex]);
            v.sort((a, b) => {
                if (a.name.toLowerCase() < b.name.toLowerCase()) {
                    return -1;
                } else if (a.name.toLowerCase() > b.name.toLowerCase()) {
                    return 1;
                } else {
                    return 0;
                }
            })
        });
        activeSDKsList.setValue((v) => {
            v.splice(activeSelectedIndex, 1);
        });

        const newCBSelIndex = comboBoxSelectedIndex + comboBoxIndexOffset;
        comboBox.selectedIndex = newCBSelIndex;

        const newListSelectedIndex = Math.min(
            activeSelectedIndex,
            activeSDKsList.options.length - 1
        );
        activeSDKsList.selectedIndex = newListSelectedIndex;
    }
}

function onDocumentLoad() {
    const app = new App();
    app.init();
}
