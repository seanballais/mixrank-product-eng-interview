export class State {
    // Note: We're not using the get and set property syntax since the usage
    //       will be awkward when passing a function to the setter (which we
    //       allow so that modification of the internal value can be modified
    //       more easily). For example:
    //
    //         s.value = (v) => { v.push('Come inside of my heart'); };
    //
    //       feels like I'm setting the value of state `s` to a function.
    //       On the contrary:
    //
    //         s.setValue((v) => { v.push('If you\'re looking for answers'); }
    //
    //       feels more natural.
    constructor(initialValue) {
        this.value = structuredClone(initialValue);
        this.initialValue = structuredClone(initialValue);
        this.subscriptions = [];

        this.isPropagationLocked = false;
    }

    getValue() {
        // This may have to be called again to ensure that the user code gets
        // the latest values.
        return this.value;
    }

    setValue(v) {
        if (typeof v === 'function') {
            v(this.value);
        } else {
            this.value = v;
        }

        if (!this.isPropagationLocked) {
            this.#propagateChanges();
        }
    }

    resetToInitialState() {
        this.setValue(structuredClone(this.initialValue));
    }

    addReactor(f, runOnAdd = true, prioritize = false) {
        // Setting prioritize to true makes the passed function more likely
        // to be called first when this state changes.
        if (prioritize) {
            this.subscriptions.unshift(f);
        } else {
            this.subscriptions.push(f);
        }

        if (runOnAdd) {
            f(this.value);
        }
    }

    lockPropagation() {
        // Prevents propagation of changes to subscribers. Helps with batch
        // updating.
        this.isPropagationLocked = true;
    }

    unlockPropagation(propagateChanges = true) {
        this.isPropagationLocked = false;

        if (propagateChanges) {
            this.#propagateChanges();
        }
    }

    #propagateChanges() {
        for (const f of this.subscriptions) {
            f();
        }
    }
}
