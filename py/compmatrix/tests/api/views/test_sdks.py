from compmatrix.tests.api.fixtures import sdk_records

from compmatrix.tests.fixtures import app, client

SDKS_ENDPOINT = '/api/v1/sdks'


def test_sdks_endpoint(client, sdk_records):
    resp = client.get(SDKS_ENDPOINT)

    # We're expecting the endpoint to respond with a sorted list of SDKs. It's
    # best we sort here, instead of making `sdk_records` sorted in the first
    # place, so that we can properly communicate that we're expecting a sorted
    # response. Additionally, `sdk_records` might be used in its original
    # unsorted version in a different test.
    sorted_sdk_records = sorted(sdk_records, key=lambda s: s.name)
    for resp_sdk, test_sdk in zip(resp.json['sdks'], sorted_sdk_records):
        assert test_sdk.name == resp_sdk['name']
        assert test_sdk.slug == resp_sdk['slug']
        assert test_sdk.url == resp_sdk['url']
        assert test_sdk.description == resp_sdk['description']
