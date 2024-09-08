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
        this.value = initialValue;
        this.subscriptions = [];
    }

    getValue() {
        return this.value;
    }

    setValue(v) {
        if (typeof v === 'function') {
            v(this.value);
        } else {
            this.value = v;
        }

        for (const f of this.subscriptions) {
            f(this.value);
        }
    }

    addReactor(f, runOnAdd = true) {
        this.subscriptions.push(f);

        if (runOnAdd) {
            f(this.value);
        }
    }
}
