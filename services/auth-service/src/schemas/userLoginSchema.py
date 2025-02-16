from pydantic import BaseModel, StrictStr, field_validator, model_validator

class UserLoginSchema(BaseModel):
    email: StrictStr
    password: StrictStr

    @field_validator("email", mode="before")
    @classmethod
    def emailValidator(cls, value: str) -> str:
        import re
        pattern = r"^[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*@gmail\.com$"
        if not re.match(pattern, value):
            raise ValueError("Invalid Email Id format")
        return value

    @field_validator("password", mode="before")
    @classmethod
    def passwordValidator(cls, value: str) -> str:
        import re
        if len(value) < 8:
            raise ValueError("Password length must be at least 8")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[@$!%*?&]", value):
            raise ValueError("Password must contain at least one special character.")
        return value

    class Config:
        from_attributes = True