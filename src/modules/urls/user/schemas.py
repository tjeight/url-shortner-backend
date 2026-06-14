from uuid import UUID

from pydantic import BaseModel, Field, AnyHttpUrl


# Class to handle the User URL POST
class UserURLPostRequestModel(BaseModel):
    long_url: AnyHttpUrl = Field(..., description="Long URL")


# Class to handle the User URL Delete
class UserURLDeleteRequestModel(BaseModel):
    link_url_id: UUID = Field(..., description="Required the Link Unique URL")


# Class to handle the User URL Refresh
class UserURLRefreshRequestModel(BaseModel):
    link_url_id: UUID = Field(..., description="Required the Link Unique URL")
