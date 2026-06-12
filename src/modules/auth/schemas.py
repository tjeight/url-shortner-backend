from pydantic import BaseModel, EmailStr, Field


# Class to handle the User Post Request
class UserRegisterPostRequestModel(BaseModel):
    user_email: EmailStr = Field(..., description="First Name")
    first_name: str = Field(..., description="Last Name")
    last_name: str = Field(..., description="Last Name")
    password: str = Field(..., description="Password")


# Class to handle the User Login
class UserLoginPostRequestModel(BaseModel):
    user_email: EmailStr = Field(..., description="User Email")
    password: str = Field(..., description="Password for the email")
