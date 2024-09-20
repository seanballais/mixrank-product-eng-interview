export class DataState {
    static #_EMPTY = 0;   // Data was just initialized.
    static #_LOADING = 1;
    static #_ERRORED = 2;
    static #_LOADED = 3;

    static get EMPTY() { return this.#_EMPTY; }
    static get LOADING() { return this.#_LOADING; }
    static get ERRORED() { return this.#_ERRORED; }
    static get LOADED() { return this.#_LOADED; }
}