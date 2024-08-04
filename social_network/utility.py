from rest_framework.response import Response


def response_with_status(status_code, message, data=None):
    response_data = {"status_code": status_code, "message": message}
    if data is not None:
        response_data["data"] = data
    return Response(response_data, status=status_code)
