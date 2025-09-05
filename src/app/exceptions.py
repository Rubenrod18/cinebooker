from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    def __init__(self, description: str):
        detail = description or (
            'The requested URL was not found on the server. If you entered'
            ' the URL manually please check your spelling and try again.'
        )
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
