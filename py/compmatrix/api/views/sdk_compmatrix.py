def numbers():
    # SQ: Query to base things off of.
    # SELECT app_id
    # FROM app_sdk
    # WHERE
    #   (sdk_id = 33 AND installed = false) OR
    #   (sdk_id = 875 AND installed = true)
    # GROUP BY app_id
    # HAVING COUNT(sdk_id) = 2
    # ORDER BY app_id
    #
    #             ID
    # ---------------
    # PayPal   |   33
    # Stripe   |  875
    # Braintree| 2081
    # TODO: This is not final. Lol. Need to implement this properly.
    return {
        'numbers': [
            [4, 3, 3],
            [2, 5, 3],
            [3, 3, 4]
        ]
    }


def apps():
    pass
