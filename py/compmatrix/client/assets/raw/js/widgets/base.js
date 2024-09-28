import udomdiff from '../vendor/udomdiff.js';

export class Widget {
    constructor(rootNodeID) {
        this.rootNode = document.getElementById(rootNodeID);
        this.nodes = [];
        this.states = {}
    }

    subscribeTo(refName, state) {
        this.states[refName] = state;
        state.addReactor(() => { this.update(); });
    }

    batchSubscribe(states) {
        for (let i = 0; i < states.length; i++) {
            const state = states[i];
            this.states[state['refName']] = state['state'];
            state.state.addReactor(() => { this.update(); }, false, false);
        }

        this.update();
    }

    update() {
        this.nodes = this.#htmlToNodes(this.createHTML());
        this.render();
    }

    createHTML() {
        return '';
    }

    render() {
        udomdiff(
            this.rootNode,
            [...this.rootNode.childNodes],
            [...this.nodes],
            (o) => o
        );
    }

    #htmlToNodes(html) {
        // Based on: https://stackoverflow.com/a/35385518/1116098
        const template = document.createElement('template');
        template.innerHTML = html;

        return template.content.childNodes;
    }
}
