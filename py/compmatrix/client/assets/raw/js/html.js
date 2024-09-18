/**
 * Based on: https://stackoverflow.com/a/35385518/1116098
 */
export function htmlToNodes(html) {
    const template = document.createElement('template');
    template.innerHTML = html;
    return template.content.childNodes;
}
