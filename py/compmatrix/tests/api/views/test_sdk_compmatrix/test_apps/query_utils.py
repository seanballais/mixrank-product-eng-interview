def create_cursor_from_app_obj(app_obj):
    return f'{app_obj.name};{app_obj.seller_name}'


def create_cursor_from_app_dict(app_obj_dict):
    return f'{app_obj_dict["name"]};{app_obj_dict["seller_name"]}'
