export class DataState {
    static #_EMPTY = 0;   // Data was just initialized.
    static #_LOADING = 1;
    static #_LOADED = 2;

    static get EMPTY() { return this.#_EMPTY; }
    static get LOADING() { return this.#_LOADING; }
    static get LOADED() { return this.#_LOADED; }
}