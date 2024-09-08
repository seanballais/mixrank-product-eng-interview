export function moveSDKFromComboBoxToList(
    comboBox,
    selectableSDKs,
    activeSDKs
) {
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

export function moveSDKFromListToComboBox(
    comboBox,
    activeSDKsList,
    selectableSDKs,
    activeSDKs
) {
    const activeSelectedIndex = activeSDKsList.selectedIndex;
    const comboBoxSelectedIndex = comboBox.selectedIndex;
    let comboBoxIndexOffset = 0;
    const comboBoxSDKName = selectableSDKs
                                .getValue()[comboBoxSelectedIndex]
                                .name;
    const activeSDKName = activeSDKs.getValue()[activeSelectedIndex].name;
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

    const newCBSelIndex = comboBoxSelectedIndex + comboBoxIndexOffset;
    comboBox.selectedIndex = newCBSelIndex;

    const newListSelectedIndex = Math.min(
        activeSelectedIndex,
        activeSDKsList.options.length - 1
    );
    activeSDKsList.selectedIndex = newListSelectedIndex;
}