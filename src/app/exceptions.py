from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    def __init__(self, description: str):
        detail = description or (
            'The requested URL was not found on the server. If you entered'
            ' the URL manually please check your spelling and try again.'
        )
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnprocessableEntityException(HTTPException):
    def __init__(self, description: str):
        detail = description or 'The request was well-formed but was unable to be followed due to semantic errors.'
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
