import { Widget } from "./base.js";
import { DataState, fetchAppListData, FetchDirection } from '../fetching.js';

export class AppList extends Widget {
    constructor(rootNode) {
        super(rootNode);

        this.prevBatchTriggerObserver = null;
        this.nextBatchTriggerObserver = null;

        this.isBatchLoading = false;
    }

    update() {
        const compmatrixData = this.states['compmatrix-data'].getValue();
        const appListState = this.states['app-list'];
        let appListData = appListState.getValue();

        appListState.lockPropagation();

        // Clear out the app list if the selected cell is null and we still
        // have displayed apps up.
        if (
            compmatrixData['selected-cell'] === null &&
            appListData['displayed-apps'].length > 0
        ) {
            appListState.resetToInitialState();
        }

        // Reset scroll bar if there is a new selected cell.
        if (
            appListData['state'] === DataState.LOADING &&
            !appListData['is-loading-new-batch']
        ) {
            this.rootNode.scrollTo({
                top: 0,
                left: 0,
                behavior: 'instant'
            });
        }

        super.update();

        // Refresh appListData.
        appListData = appListState.getValue();
        if (appListData['state'] === DataState.LOADED) {
            const observerOptions = {
                root: this.rootNode,
            };
    
            if (appListData['need-prev-batch-trigger']) {
                const callback = (entries, observer) => {
                    for (let i = 0; i < entries.length; i++) {
                        const e = entries[i];
                        // Guard check to make sure we don't keep on loading a
                        // batch of apps when we already previously initiated
                        // this trigger and we're already loading things. Not
                        // exactly an ideal solution, since this will also
                        // block the other trigger from calling its callback
                        // (which also helps make sure we don't screw up the
                        // app list if we already exceeded the maximum number
                        // of apps allowed to be loaded in). However, it should
                        // work for the time being. This might end up being
                        // enough, but we might have to change if need be
                        // depending on feedback.
                        if (e && e.isIntersecting && !this.isBatchLoading) {
                            this.#runBatchTriggerEvent(
                                appListData['start-cursor'],
                                FetchDirection.PREVIOUS
                            );
                        }
                    }
                };
                this.prevBatchTriggerObserver = new IntersectionObserver(
                    callback,
                    observerOptions
                );
                const triggerID = 'app-prev-batch-trigger';
                const trigger = document.getElementById(triggerID);
                this.prevBatchTriggerObserver.observe(trigger);
            }
    
            if (appListData['need-next-batch-trigger']) {
                const callback = (entries, observer) => {
                    for (let i = 0; i < entries.length; i++) {
                        const e = entries[i];
                        // Guard check to make sure we don't keep on loading a
                        // batch of apps when we already previously initiated
                        // this trigger and we're already loading things. Not
                        // exactly an ideal solution, since this will also
                        // block the other trigger from calling its callback
                        // (which also helps make sure we don't screw up the
                        // app list if we already exceeded the maximum number
                        // of apps allowed to be loaded in). However, it should
                        // work for the time being. This might end up being
                        // enough, but we might have to change if need be
                        // depending on feedback.
                        if (e && e.isIntersecting && !this.isBatchLoading) {
                            this.#runBatchTriggerEvent(
                                appListData['end-cursor'],
                                FetchDirection.NEXT
                            );
                        }
                    }
                };
                this.nextBatchTriggerObserver = new IntersectionObserver(
                    callback,
                    observerOptions
                );
                const triggerID = 'app-next-batch-trigger';
                const trigger = document.getElementById(triggerID);
                this.nextBatchTriggerObserver.observe(trigger);
            }
        }

        appListState.unlockPropagation(false);
    }

    createHTML() {
        const appList = this.states['app-list'].getValue();

        let html = '';

        if (
            appList['state'] === DataState.LOADED ||
            (
                appList['state'] === DataState.LOADING &&
                appList['is-loading-new-batch']
            )
        ) {
            html += '<ol id="apps-list-items">';

            if (appList['need-prev-batch-trigger']) {
                html += `
                    <li id="app-prev-batch-trigger" class="batch-trigger">
                        <span class="fas fa-circle-notch fa-spin"></span>
                    </li>
                `;
            }

            for (let i = 0; i < appList['displayed-apps'].length; i++) {
                const app = appList['displayed-apps'][i];
                html += `
                    <li class="app-card">
                        <div class="app-card-icon">
                            <img src=${app['artwork_large_url']}/>
                        </div>
                        <div class="app-card-info">
                            <h1>${app['name']}</h1>
                            <p class="app-card-info-company">
                                <a href=${app['company_url']}">
                                ${app['seller_name']}
                                </a>
                            </p>
                            <p>
                                <span class="fa-solid fa-star app-rating-icon">
                                </span>
                                ${app['rating'].toFixed(2)}
                            </p>
                        </div>
                    </li>
                `
            }

            if (appList['need-next-batch-trigger']) {
                html += `
                    <li id="app-next-batch-trigger" class="batch-trigger">
                        <span class="fas fa-circle-notch fa-spin"></span>
                    </li>
                `;
            }
            
            html += '</ol>';
        } else if (appList['state'] === DataState.LOADING) {
            html += `
                <div id="app-list-loader-icon">
                    <span class="fas fa-circle-notch fa-spin"></span>
                </div>
            `;
        }

        return html;
    }

    async #runBatchTriggerEvent(cursor, fetchDirection) {
        this.isBatchLoading = true;

        const appList = this.states['app-list'].getValue();

        await fetchAppListData(
            this.states['app-list'],
            this.states['compmatrix-data'],
            this.states['from-sdks'],
            this.states['to-sdks'],
            cursor,
            fetchDirection
        );

        const recentBatchSize = appList['recent-batch-size'];

        // If we pruned our current displayed apps, then we need to scroll up
        // or down to where our view was before we loaded in a new batch of
        // apps. Note that, prior to scrolling, we're at the either ends of
        // the app list, before we initially scrolled towards the triggers.
        if (appList['pruned'] && recentBatchSize !== 0) {
            // To compute the amount of scrolling needed, we just need to get
            // the total height of occupied by the new batch of apps in the app
            // list.
            const list = document.getElementById('apps-list-items');
            const loadedApps = [...list.children];
            const newApps = (
                fetchDirection == FetchDirection.PREVIOUS
                ? loadedApps.slice(0, recentBatchSize + 1)
                : loadedApps.slice(-recentBatchSize - 1)
            );
            const listStyle = window.getComputedStyle(list);
            
            let scrollHeight = 0;

            // Get the total height occupied by just the app cards first.
            if (newApps.length > 0) {
                // We should only be adding in the height of each row that only
                // contains the new apps (note that some rows might include
                // apps that are not part of the new batch) since they make
                // new rows, and not by each card.
                //
                // NOTE: At the moment, we won't be considering margins and
                //       paddings in the computations since the app cards
                //       don't set those yet. Maybe at a later time, we might
                //       have to include them. However, for now, YAGNI.
                const listBounds = list.getBoundingClientRect();
                const rowStartXPos = listBounds['x'];
                
                let numRows = 0;

                for (let i = 0; i < newApps.length; i++) {
                    const cardBounds = newApps[i].getBoundingClientRect();
                    if (cardBounds['x'] == rowStartXPos) {
                        // This indicates that a new row has started.
                        scrollHeight += cardBounds['height'];
                        numRows++;
                    }
                }

                // And let's add in the heights occupied by the row gaps of the
                // new batch of apps. This does not include the gap between
                // the app cards and triggers.
                const rowGap = listStyle.getPropertyValue('row-gap');
                const rowGapSize = parseInt(rowGap);
                scrollHeight += rowGapSize * (numRows - 1);

                // Let's reduce the offset just a bit more. This handles the
                // case where the first pruning may result in the former
                // topmost or bottommost row in the app list from being
                // partially covered after scrolling. This is a temporary hack,
                // and the ideal fix may involve computing the original scroll
                // position. However, in the interest of time, we'll use this
                // hack for now.
                scrollHeight -= rowGapSize * 3.5;
            }

            // We have to negate the scroll height since we have to scroll up
            // if we loaded in a new batch of apps at the end of the list.
            if (fetchDirection === FetchDirection.NEXT) {
                scrollHeight = -scrollHeight;
            }

            // We're using scrollBy() instead of scrollTo() (which would also
            // change our scroll computations) because the latter resets the
            // scrollbar to the top before scrolling down to the location we
            // want to scroll to, which wrongfully triggers the topmost batch
            // trigger. Using the former is not exactly ideal and is arguably
            // less precise, but it does not result in the aforementioned
            // issues and the effect are still within acceptable thresholds.
            //
            // (September 29, 2024 2:30 AM)
            // TODO: We can change this to scrollTo since I just found out
            //       about the "instant" behaviour of scrollTo. scrollTo will
            //       allow us to set the scroll bar more accurately.
            this.rootNode.scrollBy(0, scrollHeight);
        }

        this.isBatchLoading = false;
    }
}
