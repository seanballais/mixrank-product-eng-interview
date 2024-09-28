import { Widget } from "./base.js";
import { DataState, fetchAppListData } from '../fetching.js';

export class CompMatrix extends Widget {
    constructor(rootNode) {
        super(rootNode);

        this.cellToSDKs = {};
        this.selectedCellID = null;
    }

    clearSelectedCell() {
        this.selectedCellID = null;
        this.states['data'].setValue((v) => {
            v['selected-cell'] = null;
        });
    }

    update() {
        // Reset. An update may result in some cells being removed.
        this.cellToSDKs = {};

        super.update();

        const data = this.states['data'].getValue();
        const dataState = data['state'];

        if (dataState == DataState.LOADED) {
            for (const [key, sdks] of Object.entries(this.cellToSDKs)) {
                const cell = document.getElementById(key);
                cell.addEventListener('click', () => {
                    if (key == this.selectedCellID) {
                        // Deselect this cell.
                        this.states['data'].setValue((v) => {
                            v['selected-cell'] = null;
                        });

                        this.selectedCellID = null;
                    } else {
                        // Select this cell.
                        this.states['data'].setValue((v) => {
                            v['selected-cell'] = {
                                'from-sdk': sdks['from-sdk'],
                                'to-sdk': sdks['to-sdk']
                            };
                        });

                        // We're setting this here to make sure that
                        // compmatrix data has been set already.
                        this.selectedCellID = this.#getSelectedCellID();

                        fetchAppListData(
                            this.states['app-list'],
                            this.states['data'],
                            this.states['from-sdks'],
                            this.states['to-sdks']
                        );
                    }
                });
            }

            this.#manageSelectedCell();
            if (!this.selectedCellID) {
                const dataState = this.states['data'];

                // Prevents an infinite loop caused by propagating the changes
                // to observers.
                dataState.lockPropagation();

                this.states['data'].setValue((v) => {
                    v['selected-cell'] = null;
                });
                dataState.unlockPropagation(false);
            }
        }
    }

    createHTML() {
        const data = this.states['data'].getValue();
        const dataState = data['state'];

        const sdkHeaders = this.#getSDKHeaders();
        const fromSDKHeaders = sdkHeaders['from-sdks'];
        const toSDKHeaders = sdkHeaders['to-sdks'];

        const numFromSDKsHeaders = fromSDKHeaders.length;
        const numToSDKsHeaders = toSDKHeaders.length;

        let html = '';
        html += '<tr>';
        html += '<th></th>';
        html += `<th colspan="${numToSDKsHeaders + 1}">To SDK</th>`;
        html += '</tr>';
        html += '<tr>';
        html += `<th rowspan="${numFromSDKsHeaders + 2}">`;
        html += '<span>From SDK</span>';
        html += '</th>';
        html += '</tr>';

        if (dataState == DataState.LOADED) {
            html += '<tr>';
            html += '<th></th>';
            for (let i = 0; i < numToSDKsHeaders; i++) {
                html += `<th>${toSDKHeaders[i]['name']}</th>`;
            }
            html += '</tr>';

            const activeData = data['active-data'];
            const presentedData = data['data'][activeData];
            const percentageData = data['data']['normalized']
            for (let i = 0; i < presentedData.length; i++) {
                const rowData = presentedData[i];
                html += '<tr>';
                html += `<th>${fromSDKHeaders[i]['name']}</th>`;
                for (let j = 0; j < rowData.length; j++) {
                    let cellData = rowData[j];
                    if (activeData == 'normalized') {
                        cellData = `${(cellData * 100).toFixed(0)}%`;
                    }

                    const opacity = percentageData[i][j];

                    const id = this.#createCellID(i, j);
                    const colour = `hsla(0, 80%, 55%, ${opacity * 100}%)`
                    const style = `background-color: ${colour}`;

                    html += `
                        <td id="${id}" style="${style}">${cellData}</td>
                    `;

                    this.cellToSDKs[id] = {
                        'from-sdk': fromSDKHeaders[i],
                        'to-sdk': toSDKHeaders[j]
                    };
                }
                html += '</tr>';
            }
        } else if (dataState == DataState.LOADING) {
            html += '<tr>';
            html += '<td>';
            html += '<span class="fas fa-circle-notch fa-spin"></span>'
            html += '</td>';
            html += '</tr>';
        }

        return html;
    }

    #manageSelectedCell() {
        const selectedCellID = this.#getSelectedCellID();
        if (selectedCellID) {
            const cellElem = document.getElementById(selectedCellID);
            // Guard check to make sure that the element already exists before
            // we add a new class to the element.
            if (cellElem) {
                cellElem.classList.add('selected-cell');
            }
            
            this.selectedCellID = selectedCellID;
        } else {
            this.selectedCellID = null;
        }
    }

    #getSelectedCellID() {
        const data = this.states['data'].getValue();
        const sdkHeaders = this.#getSDKHeaders();

        const selectedCell = data['selected-cell'];
        if (selectedCell) {
            const selectedFromSDK = selectedCell['from-sdk'];
            const selectedToSDK = selectedCell['to-sdk'];

            let rowIndex = null;
            const fromSDKHeaders = sdkHeaders['from-sdks'];
            for (let i = 0; i < fromSDKHeaders.length; i++) {
                if (fromSDKHeaders[i]['id'] == selectedFromSDK['id']) {
                    rowIndex = i;
                }
            }

            let colIndex = null;
            const toSDKHeaders = sdkHeaders['to-sdks'];
            for (let i = 0; i < toSDKHeaders.length; i++) {
                if (toSDKHeaders[i]['id'] == selectedToSDK['id']) {
                    colIndex = i;
                }
            }

            if (rowIndex !== null && colIndex !== null) {
                return this.#createCellID(rowIndex, colIndex);
            }
        }

        return null;
    }

    #getSDKHeaders() {
        const fromSDKData = this.states['from-sdks'].getValue();
        const toSDKData = this.states['to-sdks'].getValue();

        const fromSDKHeaders = [...fromSDKData];
        const toSDKHeaders = [...toSDKData];

        fromSDKHeaders.push({'id': null, 'name': '(none)'});
        toSDKHeaders.push({'id': null, 'name': '(none)'});

        return {
            'from-sdks': fromSDKHeaders,
            'to-sdks': toSDKHeaders
        };
    }

    #createCellID(rowIndex, colIndex) {
        return `cmc-${rowIndex}${colIndex}`;
    }
}
