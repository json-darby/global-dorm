from pydantic import BaseModel


class VerifyUserResponse(BaseModel):
    status: str
    message: str
