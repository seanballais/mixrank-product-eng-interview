export function moveSDKFromComboBoxToList(
    comboBox,
    selectableSDKs,
    activeSDKsList,
    activeSDKs
) {
    const selectables = selectableSDKs.getValue();
    const actives = activeSDKs.getValue();
    if (selectables.length > 0) {
        const cBoxSelectedIndex = comboBox.selectedIndex;
        const activeSelectedIndex = activeSDKsList.selectedIndex;

        activeSDKs.setValue((v) => {
            v.push(selectableSDKs.getValue()[cBoxSelectedIndex]);
        });
        selectableSDKs.setValue((v) => { v.splice(cBoxSelectedIndex, 1); });

        const newSelectedIndex = Math.min(
            cBoxSelectedIndex,
            comboBox.options.length - 1
        );
        comboBox.selectedIndex = newSelectedIndex;

        // Adding a new SDK to the active list deselects the pre-selected
        // option. So, we're just selecting it again. No need for computing
        // the index offset (unlike with moveSDKFromListToComboBox(...)) since
        // the new SDK is always pushed at the end of the list.
        if (actives.length > 0 && activeSelectedIndex !== null) {
            activeSDKsList.selectedIndex = activeSelectedIndex;
        }
    }
}

export function moveSDKFromListToComboBox(
    comboBox,
    selectableSDKs,
    activeSDKsList,
    activeSDKs
) {
    const selectables = selectableSDKs.getValue();
    const actives = activeSDKs.getValue();

    const comboBoxSelectedIndex = comboBox.selectedIndex;
    const activeSelectedIndex = activeSDKsList.selectedIndex;

    if (actives.length > 0 && activeSelectedIndex !== null) {
        let cBoxIdxOffset = 0;

        // We need to do these now before we modify the combo box options and
        // list options.
        if (selectables.length > 0) {
            // Only makes sense to check for an offset if the combo box has
            // existing options.
            const cBoxSDKName = selectableSDKs
                                    .getValue()[comboBoxSelectedIndex]
                                    .name;
            const activeSDKName = activeSDKs
                                    .getValue()[activeSelectedIndex]
                                    .name;
            if (cBoxSDKName.toLowerCase() >= activeSDKName.toLowerCase()
                && cBoxSDKName > activeSDKName) {
                // The SDK removed from the active list of SDKs will be placed
                // behind the currently selected SDK in the SDK combo box. So,
                // we need to offset the new combo box index by 1. Second
                // condition handles the edge case where two SDKs have the same
                // names in lowercase, but are technically different when their
                // original cases.
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
            // elements. Just set the selected index to the first one. Before
            // this point, `comboBoxSelectedIndex` would be undefined since
            // there are no options available yet.
            comboBox.selectedIndex = 0;
        }

        const newListSelectedIndex = Math.min(
            activeSelectedIndex,
            activeSDKsList.options.length - 1
        );
        activeSDKsList.selectedIndex = newListSelectedIndex;
    }
}