import codecs

def to_json(python_object):
    """Converting bytes value on object to json

    Args:
        python_object (dict): A dict that contain bytes types on value

    Raises:
        TypeError: If json is not serializable

    Returns:
        dict: Returns decoded bytes value 
    """
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    """Converting and encode bytes value from json object

    Args:
        json_object (dict): json dictionary

    Returns:
        dict: json_object
    """
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object