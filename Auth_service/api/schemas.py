from pydantic import BaseModel, Field, EmailStr

class SCreateUser(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., description="Password of the user")
    password_check: str = Field(..., description="Password check of the user")
    first_name: str = Field(..., description="First name of the user")
    last_name: str = Field(..., description="Last name of the user")
    phone_number: str = Field(..., description="Phone number of the user")
    

class SUserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., description="Password of the user")

class SUserUpdate(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    first_name: str = Field(..., description="First name of the user")
    last_name: str = Field(..., description="Last name of the user")
    phone_number: str = Field(..., description="Phone number of the user")