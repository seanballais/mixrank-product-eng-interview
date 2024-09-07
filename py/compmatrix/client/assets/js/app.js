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

        this.fromSDKComboBox = new SDKSelect('from-sdk-selectables');
        this.activeFromSDKsList = new SDKSelect('from-sdk-selected');
        this.selectableFromSDKs.addWidgetSubscriber(this.fromSDKComboBox);
        this.activeFromSDKs.addWidgetSubscriber(this.activeFromSDKsList);

        this.toSDKComboBox = new SDKSelect('to-sdk-selectables');
        this.activeToSDKsList = new SDKSelect('to-sdk-selected');
        this.selectableToSDKs.addWidgetSubscriber(this.toSDKComboBox);
        this.activeToSDKs.addWidgetSubscriber(this.activeToSDKsList);

        this.fromSDKAddBtn = new Button('from-sdk-config-list-add-btn');
        this.selectedFromSDKUpBtn = new Button(
            'from-sdk-selected-move-up-btn'
        );
        this.selectedFromSDKDownBtn = new Button(
            'from-sdk-selected-move-down-btn'
        );
        this.selectedFromSDKRemoveBtn = new Button(
            'from-sdk-selected-remove-btn'
        );

        this.toSDKAddBtn = new Button('to-sdk-config-list-add-btn');

        this.fromSDKAddBtn.setOnClick((e) => {
            const selectedIndex = this.fromSDKComboBox.selectedIndex;
            this.activeFromSDKs.setValue((v) => {
                v.push(this.selectableFromSDKs.getValue()[selectedIndex]);
            });
            this.selectableFromSDKs.setValue((v) => {
                v.splice(selectedIndex, 1);
            });

            const newSelectedIndex = Math.min(
                selectedIndex,
                this.fromSDKComboBox.options.length - 1
            );
            this.fromSDKComboBox.selectedIndex = newSelectedIndex;
        });
        this.selectedFromSDKUpBtn.setOnClick((e) => {
            const selectedID = this.activeFromSDKsList.selectedIndex;
            const newIndex = Math.max(selectedID - 1, 0);
            this.activeFromSDKs.setValue((v) => {
                [v[newIndex], v[selectedID]] = [v[selectedID], v[newIndex]];
            });
            this.activeFromSDKsList.selectedIndex = newIndex;
        });
        this.selectedFromSDKDownBtn.setOnClick((e) => {
            const selectedID = this.activeFromSDKsList.selectedIndex;
            const newIndex = Math.min(
                selectedID + 1,
                this.activeFromSDKsList.options.length - 1
            );
            this.activeFromSDKs.setValue((v) => {
                [v[newIndex], v[selectedID]] = [v[selectedID], v[newIndex]];
            });
            this.activeFromSDKsList.selectedIndex = newIndex;
        });
        this.selectedFromSDKRemoveBtn.setOnClick((e) => {
            const activeSelectedIndex = this.activeFromSDKsList.selectedIndex;
            const comboBoxSelectedIndex = this.fromSDKComboBox.selectedIndex;

            let comboBoxIndexOffset = 0;
            const comboBoxSDKName = this
                .selectableFromSDKs
                .getValue()[comboBoxSelectedIndex]
                .name;
            const activeSDKName = this
                .activeFromSDKs
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
            
            this.selectableFromSDKs.setValue((v) => {
                v.push(this.activeFromSDKs.getValue()[activeSelectedIndex]);
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
            this.activeFromSDKs.setValue((v) => {
                v.splice(activeSelectedIndex, 1);
            });

            const newCBSelIndex = comboBoxSelectedIndex + comboBoxIndexOffset;
            this.fromSDKComboBox.selectedIndex = newCBSelIndex;

            const newListSelectedIndex = Math.min(
                activeSelectedIndex,
                this.activeFromSDKsList.options.length - 1
            );
            this.activeFromSDKsList.selectedIndex = newListSelectedIndex;
        });
        
        this.toSDKAddBtn.setOnClick((e) => {
            const selectedSDKID = this.toSDKComboBox.selectedIndex;
            this.toFromSDKs.setValue((v) => {
                v.push(this.selectableToSDKs.getValue()[selectedSDKID]);
            });
            this.selectableToSDKs.setValue((v) => {
                v.splice(selectedSDKID, 1);
            });
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

            this.selectableFromSDKs.setValue(sdks);
            this.selectableToSDKs.setValue(sdks);
        } catch (error) {
            console.error(error.message);
        }
    }
}

function onDocumentLoad() {
    const app = new App();
    app.init();
}
