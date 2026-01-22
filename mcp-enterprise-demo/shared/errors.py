from fastapi import HTTPException


def forbidden(detail: str = "forbidden"):
    raise HTTPException(status_code=403, detail=detail)


def bad_request(detail: str = "bad request"):
    raise HTTPException(status_code=400, detail=detail)
