SDKS_ENDPOINT = '/api/v1/sdks'


def test_sdks_endpoint(client, test_db_data):
    resp = client.get(SDKS_ENDPOINT)

    # We're expecting the endpoint to respond with a sorted list of SDKs. It's
    # best we sort here, instead of making `sdk_records` sorted in the first
    # place, so that we can properly communicate that we're expecting a sorted
    # response. Additionally, `sdk_records` might be used in its original
    # unsorted version in a different test.
    sorted_sdk_records = sorted(test_db_data['sdks'],
                                key=lambda s: s.name.casefold())
    sdks = resp.json['data']['sdks']
    for resp_sdk, test_sdk in zip(sdks, sorted_sdk_records):
        assert resp_sdk['name'] == test_sdk.name
        assert resp_sdk['slug'] == test_sdk.slug
        assert resp_sdk['url'] == test_sdk.url
        assert resp_sdk['description'] == test_sdk.description
