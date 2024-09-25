export const APP_LIST_BATCH_SIZE = 50;
export const MAX_APP_LIST_SIZE = 150;
export const BASE_API_ENDPOINT = '/api/v1';

// We should make sure that batch size is larger than the maximum size.
console.assert(APP_LIST_BATCH_SIZE <= MAX_APP_LIST_SIZE);
