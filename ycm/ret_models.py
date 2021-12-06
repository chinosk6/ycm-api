

def return_status(code: int, message: str, **kwargs):
    ret = {
        "code": code,
        "message": message
    }
    for k in kwargs:
        ret[k] = kwargs[k]
    return ret

def return_car(car_id, room_id, description, data_from, creator_id, more_info, add_time):
    ret = {
        "id": int(car_id),
        "room_id": str(room_id),
        "description": str(description),
        "data_from": str(data_from),
        "creator_id": str(creator_id),
        "more_info": str(more_info),
        "add_time": int(add_time)
    }
    return ret
