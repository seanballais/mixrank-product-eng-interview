export function moveSDKFromComboBoxToList(
    comboBox,
    selectableSDKs,
    activeSDKs
) {
    const selectables = selectableSDKs.getValue();
    if (selectables.length > 0) {
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
}

export function moveSDKFromListToComboBox(
    comboBox,
    activeSDKsList,
    selectableSDKs,
    activeSDKs
) {
    const actives = activeSDKs.getValue();
    const selectables = selectableSDKs.getValue();
    if (actives.length > 0) {
        const activeSelectedIndex = activeSDKsList.selectedIndex;
        const comboBoxSelectedIndex = comboBox.selectedIndex;
        
        let cBoxIdxOffset = 0;

        // We need to do these now before we modify the combo box options and
        // list options.
        if (selectables.length > 0) {
            // Only makes sense to check for an offset if the combo box has
            // existing options.
            const cBoxSDKName = selectableSDKs
                                        .getValue()[comboBoxSelectedIndex]
                                        .name
                                        .toLowerCase();
            const activeSDKName = activeSDKs
                                    .getValue()[activeSelectedIndex]
                                    .name
                                    .toLowerCase();
            if (cBoxSDKName >= activeSDKName && cBoxSDKName > activeSDKName) {
                // The SDK removed from the active list of From SDKs will be
                // placed behind the currently selected SDK in the From SDK
                // combo box. So, we need to offset the new combo box index
                // by 1. Second condition handles the edge case where two SDKs
                // have the same names in lowercase, but are technically
                // different when their original cases.
                cBoxIdxOffset = 1;
            }
        }
        
        // Modify the combo box and list, which will update the HTML.
        selectableSDKs.setValue((v) => {
            v.push(activeSDKs.getValue()[activeSelectedIndex]);
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
        activeSDKs.setValue((v) => {
            v.splice(activeSelectedIndex, 1);
        });

        // And then set the new selected options.
        if (selectables.length > 0) {
            // We might need an offset if the combo box has existing options.
            comboBox.selectedIndex = comboBoxSelectedIndex + cBoxIdxOffset;
        } else {
            // But it doesn't make sense to compute the offset if there are no
            // elements. Just set the selected index to the first one. At this
            // point, `comboBoxSelectedIndex` would be undefined.
            comboBox.selectedIndex = 0;
        }

        const newListSelectedIndex = Math.min(
            activeSelectedIndex,
            activeSDKsList.options.length - 1
        );
        activeSDKsList.selectedIndex = newListSelectedIndex;
    }
}