class CustomException(Exception):
    status_code: int
    detail: str

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class InvalidRequestException(CustomException):
    status_code = 400

    def __init__(self, detail):
        super().__init__(detail)


class UnauthorizedException(CustomException):
    status_code = 401

    def __init__(self, detail):
        super().__init__(detail)


class ForbiddenException(CustomException):
    status_code = 403

    def __init__(self, detail):
        super().__init__(detail)


class ResourceNotFoundException(CustomException):
    status_code = 404

    def __init__(self, detail):
        super().__init__(detail)


class ResourceAlreadyExistException(CustomException):
    status_code = 409

    def __init__(self, detail):
        super().__init__(detail)
