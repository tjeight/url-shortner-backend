from passlib.context import CryptContext


# Set the crypto context
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Helper function hash the password
def hash_password(password: str) -> str:
    return password_context.hash(password)


# Helper Function to verify the password
def verify_hashed_password(hashed_password, password) -> bool:
    return password_context.verify(
        secret=password,
        hash=hashed_password,
    )
