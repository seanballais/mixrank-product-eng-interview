import {
    APP_LIST_BATCH_SIZE,
    BASE_API_ENDPOINT,
    MAX_APP_LIST_SIZE
} from "./constants";

export class DataState {
    static #_EMPTY = 0;   // Data was just initialized.
    static #_LOADING = 1;
    static #_ERRORED = 2;
    static #_LOADED = 3;

    static get EMPTY() { return this.#_EMPTY; }
    static get LOADING() { return this.#_LOADING; }
    static get ERRORED() { return this.#_ERRORED; }
    static get LOADED() { return this.#_LOADED; }
};

export class FetchDirection {
    static get PREVIOUS() { return 'previous'; }
    static get NEXT() { return 'next'; }
};

export async function fetchSDKs(fromSDKs, toSDKs) {
    const url = `${BASE_API_ENDPOINT}/sdks`
    try {
        const response = await fetch(url);
        const sdks_json = await response.json();
        const sdks_data = sdks_json.data.sdks;
        let sdks = [];
        for (let i = 0; i < sdks_data.length; i++) {
            sdks.push({
                'id': sdks_data[i].id,
                'name': sdks_data[i].name
            })
        }

        fromSDKs.setValue(structuredClone(sdks));
        toSDKs.setValue(structuredClone(sdks));
    } catch (error) {
        console.error(error.message);
    }
}

export async function fetchCompMatrixValues(
    compmatrixData,
    activeFromSDKs,
    activeToSDKs
) {
    const url = `${BASE_API_ENDPOINT}/sdk-compmatrix/numbers`;
    const fromSDKs = activeFromSDKs.getValue().map((s) => s.id);
    const toSDKs = activeToSDKs.getValue().map((s) => s.id);

    let rawParamPairs = [];
    if (fromSDKs.length !== 0) {
        rawParamPairs.push(...fromSDKs.map((s) => ['from_sdks', s]));
    } else {
        rawParamPairs.push(['from_sdks', '']);
    }

    if (toSDKs.length !== 0) {
        rawParamPairs.push(...toSDKs.map((s) => ['to_sdks', s]));
    } else {
        rawParamPairs.push(['to_sdks', '']);
    }

    const params = new URLSearchParams(rawParamPairs);
    const paramString = params.toString();
    let numbersJSON;
    try {
        compmatrixData.setValue((v) => {
            v['state'] = DataState.LOADING;
        });
        const response = await fetch(`${url}?${paramString}`);
        numbersJSON = await response.json();
    } catch (error) {
        console.error(error.message);
        compmatrixData.setValue((v) => {
            v['state'] = DataState.ERRORED;
        });
    }

    const rawValues = numbersJSON.data.numbers;
    let normalizedValues = [];
    for (let i = 0; i < numbersJSON.data.numbers.length; i++) {
        let row = numbersJSON.data.numbers[i];
        const sum = row.reduce((partialSum, n) => partialSum + n, 0);

        let normalized = []
        for (let j = 0; j < row.length; j++) {
            normalized.push(row[j] / sum);
        }

        normalizedValues.push(normalized);
    }
    
    compmatrixData.setValue((v) => {
        v['data']['raw'] = rawValues;
        v['data']['normalized'] = normalizedValues;
        v['state'] = DataState.LOADED;
    });
}

export async function fetchAppListData(
    appListDataState,
    compmatrixDataState,
    activeFromSDKsState,
    activeToSDKsState,
    cursor = null,
    direction = null
) {
    const url = `${BASE_API_ENDPOINT}/sdk-compmatrix/apps`;

    const compmatrixData = compmatrixDataState.getValue();
    const fromSDK = compmatrixData['selected-cell']['from-sdk'];
    const toSDK = compmatrixData['selected-cell']['to-sdk'];

    const activeFromSDKs = activeFromSDKsState.getValue();
    const activeToSDKs = activeToSDKsState.getValue();

    const otherFromSDKIDs = activeFromSDKs.filter((s) => {
        if (fromSDK !== null) {
            return s.id != fromSDK['id'];
        }

        return true;
    });
    const otherToSDKIDs = activeToSDKs.filter((s) => {
        if (toSDK !== null) {
            return s.id != toSDK['id'];
        }

        return true;
    });

    let rawParamPairs = [];
    if (fromSDK !== null && fromSDK['id'] !== null) {
        rawParamPairs.push(['from_sdk', fromSDK['id']]);
    } else if (otherFromSDKIDs.length !== 0) {
        // We can only specify `other_from_sdks` if `from_sdk` is
        // unspecified.
        rawParamPairs.push(
            ...otherFromSDKIDs.map((s) => ['other_from_sdks', s['id']])
        );
    }

    if (toSDK !== null && toSDK['id'] !== null) {
        rawParamPairs.push(['to_sdk', toSDK['id']]);
    } else if (otherToSDKIDs.length !== 0) {
        // We can only specify `other_to_sdks` if `to_sdk` is unspecified.
        rawParamPairs.push(
            ...otherToSDKIDs.map((s) => ['other_to_sdks', s['id']])
        );
    }

    rawParamPairs.push(['count', APP_LIST_BATCH_SIZE]);

    if (cursor !== null) {
        rawParamPairs.push(['cursor', cursor]);
        rawParamPairs.push(['direction', direction]);
    }

    const params = new URLSearchParams(rawParamPairs);
    const paramString = params.toString();
    let appsJSON;
    try {
        appListDataState.setValue((v) => {
            v['state'] = DataState.LOADING;

            if (cursor !== null) {
                // Direction is already expected to be defined whenever cursor
                // is defined.
                v['is-loading-new-batch'] = true;
            }
        });

        const response = await fetch(`${url}?${paramString}`);
        appsJSON = await response.json();
    } catch (error) {
        console.error(error.message);
    }

    appListDataState.setValue((v) => {
        v['state'] = DataState.LOADED;
        v['is-loading-new-batch'] = false; // Reset back to default value.

        const numApps = appsJSON['data']['apps'].length;
        const totalCount = appsJSON['data']['total_count'];

        v['total-app-count'] = totalCount;

        if (cursor === null) {
            // We're just getting an initial batch. So, we can reset the
            // currently displayed apps.
            v['displayed-apps'] = [];
        }

        for (let i = 0; i < numApps; i++) {
            const app = appsJSON['data']['apps'][i];

            let companyURL = null;
            if (app['company_url'] != '') {
                companyURL = app['company_url'];
            }

            let totalRatings = app['five_star_ratings'];
            totalRatings += app['four_star_ratings'];
            totalRatings += app['three_star_ratings'];
            totalRatings += app['two_star_ratings'];
            totalRatings += app['one_star_ratings'];

            let rating = 0;
            rating += (app['five_star_ratings'] * 5);
            rating += (app['four_star_ratings'] * 4);
            rating += (app['three_star_ratings'] * 3);
            rating += (app['two_star_ratings'] * 2);
            rating += (app['one_star_ratings'] * 1);
            rating /= totalRatings;

            const newApp = {
                'name': app['name'],
                'seller_name': app['seller_name'],
                'company_url': companyURL,
                'artwork_large_url': app['artwork_large_url'],
                'rating': rating
            };

            if (cursor !== null && direction === FetchDirection.PREVIOUS) {
                v['displayed-apps'].splice(i, 0, newApp);
            } else {
                v['displayed-apps'].push(newApp);
            }
        }

        if (cursor === null) {
            // We're getting the initial batch, so we can set the cursors to
            // the ones we receive from the API.
            v['start-cursor'] = appsJSON['data']['start_cursor'];
            v['end-cursor'] = appsJSON['data']['end_cursor'];
        } else {
            // Only update one cursor depending on the fetch direction.
            // The other cursor would not be the correct cursor for the entire
            // app.
            if (direction === FetchDirection.PREVIOUS) {
                v['start-cursor'] = appsJSON['data']['start_cursor'];
            } else {
                v['end-cursor'] = appsJSON['data']['end_cursor'];
            }
        }

        // Prune apps here if we go over the maximum size limit.
        let wasLeftPruned = false;
        let wasRightPruned = false;
        const numDisplayedApps = v['displayed-apps'].length;
        if (numDisplayedApps > MAX_APP_LIST_SIZE) {
            const numExtraApps = numDisplayedApps - MAX_APP_LIST_SIZE;

            // The cursor should have been specified at this point.
            if (direction === FetchDirection.PREVIOUS) {
                // Prune out the apps at the end to make space for the new apps
                // added at the start of the list of displayed apps.
                v['displayed-apps'].splice(-numExtraApps);

                const numDisplayedApps = v['displayed-apps'].length;
                const endApp = v['displayed-apps'][numDisplayedApps - 1];
                v['end-cursor'] = createCursorFromDisplayedApp(endApp);

                wasRightPruned = true;
                v['pruned'] = true;
            } else {
                // Prune out the apps at the start to make space for the new
                // apps added at the end of the list of displayed apps.
                v['displayed-apps'].splice(0, numExtraApps);

                const startApp = v['displayed-apps'][0];
                v['start-cursor'] = createCursorFromDisplayedApp(startApp);

                wasLeftPruned = true;
                v['pruned'] = true;
            }
        }

        v['recent-batch-size'] = numApps;

        if (numApps == totalCount) {
            v['need-prev-batch-trigger'] = false;
            v['need-next-batch-trigger'] = false;
        } else if (numApps == 0) {
            // This will happen when we try to load in more apps but there are
            // no more additional apps. We need to try to load in more apps
            // to figure out if there are more apps to be loaded in, since our
            // API uses cursor-based pagination without providing indexing,
            // which would have been great for this app's use case (which we
            // are not yet supporting data insertion), to easily figure out if
            // we have more apps to load. This would be fine though once we
            // start scaling and adding more features to the app.
            if (direction === FetchDirection.PREVIOUS) {
                v['need-prev-batch-trigger'] = false;
            } else {
                v['need-next-batch-trigger'] = false;
            }
        } else {
            // NOTE: Ideally, numApps will never be greater than totalCount.
            //       ^ Words before disaster.
            if (direction === FetchDirection.PREVIOUS) {
                v['need-prev-batch-trigger'] = true;
            } else {
                v['need-next-batch-trigger'] = true;
            }
        }

        // If we the displayed apps was pruned, then definitely, we need to
        // add triggers.
        if (wasLeftPruned) {
            v['need-prev-batch-trigger'] = true;
        } else if (wasRightPruned) {
            v['need-next-batch-trigger'] = true;
        }
    });
}

export function refetchAppListIfNeeded(
    appListData,
    compmatrixData,
    activeFromSDKs,
    activeToSDKs
) {
    const matrixData = compmatrixData.getValue();
    const selectedCell = matrixData['selected-cell'];
    if (selectedCell) {
        const fromSDK = selectedCell['from-sdk'];
        const toSDK = selectedCell['to-sdk'];
        if (fromSDK['id'] === null || toSDK['id'] === null) {
            // Refetch app list in case the newly-added SDK causes a
            // change in numbers to the cell. This only happens in
            // cells with a (none) SDK.
            fetchAppListData(
                appListData,
                compmatrixData,
                activeFromSDKs,
                activeToSDKs
            );
        }
    }
}

function createCursorFromDisplayedApp(app) {
    return `${app['name']};${app['seller_name']}`;
}
