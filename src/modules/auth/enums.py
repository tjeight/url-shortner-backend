from enum import StrEnum


# Class to handle the Roles
class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


# Class to handle the enums for the token tyoe
class TokenType(StrEnum):
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
