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


# Class to handle the User Auth
class UserAuth(BaseModel):
    user_id: str = Field(..., description="User ID")
    role: str = Field(..., description="User Role")
    session_id: str = Field(..., description="User Session ID")


# Class to handle the Verifiy forgot password
class UserForgotPasswordPostRequestModel(BaseModel):
    user_email: str = Field(..., description="User Email")


# Class to handle the Verify OTP for forgot password
class UserForgotPasswordVerifyOTPPostRequestModel(BaseModel):
    user_email: str = Field(..., description="User Email")
    otp: str = Field(..., description="OTP sent to the user for password reset")


# Class to handle the Reset Password Request
class UserResetAuth(BaseModel):
    user_id: str = Field(..., description="User ID")


# Class to handle the Reset Password Request
class UserResetPasswordPostRequestModel(BaseModel):
    new_password: str = Field(..., description="New Password for the user")
    reset_token: str = Field(..., description="Reset Token for the user")
