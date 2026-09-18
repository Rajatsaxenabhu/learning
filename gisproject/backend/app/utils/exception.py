from fastapi import status
from fastapi.exceptions import HTTPException
from app.api.exception.exceptions import EmailAlreadyExistsException,CustomException
from asyncpg.exceptions import NotNullViolationError, UniqueViolationError

from functools import wraps
from sqlalchemy.exc import IntegrityError
def validate(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return  await func(*args, **kwargs)
        
            # first i make for db handling
        except IntegrityError as e:
            cause = getattr(e.orig, "__cause__", None)

            if isinstance(cause, UniqueViolationError):
                raise EmailAlreadyExistsException()

            if isinstance(cause, NotNullViolationError):
                raise HTTPException(
                    status_code=400,
                    detail="Required field is db missing"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
            
        except EmailAlreadyExistsException as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except CustomException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=str(e)
            )
        except Exception as e:
            print("error is here",e)
            if "No clusters found" in str(e):
                raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,detail=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    return wrapper