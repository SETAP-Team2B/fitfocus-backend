from rest_framework.response import Response
from utils.validator import Status, Messages

def api_success(value):
    """ A successful API response value.

    :param value: The data to be included in the output.
    :type value: Any valid JSON data type.
    :return: A Response object with status code 200, and data being a **dict**, containing "data": **value**
    :rtype: rest_framework.response.Response
    """
    return Response(data={"data": value}, status=Status.SUCCESS, )


def api_error(msg: str):
    """A Response object containing error information when an HTTP error occurs.

    :param msg: The message to be output by the API.
    :type msg: str
    :return: A Response object with data being a **dict**, containing "code": 400, and "message": **msg**
    :rtype: rest_framework.response.Response
    """

    return Response(status=Status.INVALID_REQUEST, data= {
        "code": Status.INVALID_REQUEST,
        "message": msg if msg else Messages.generic_error()
    })
