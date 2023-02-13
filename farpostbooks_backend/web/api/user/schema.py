from pydantic import BaseModel


class IsUserExist(BaseModel):
    """IsUserExist model."""

    status: bool
