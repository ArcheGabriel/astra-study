from app.schemas.response import ApiResponse


def success_response(
    *,
    message: str,
    data=None,
):
    return ApiResponse(
        message=message,
        data=data,
    )