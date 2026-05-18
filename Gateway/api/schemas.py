from pydantic import BaseModel, Field, EmailStr
from datetime import date
class SUserRegister(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., description="Password of the user")
    password_check : str = Field(..., description="Password of the user")
    first_name : str = Field(..., description="First name of the user")
    last_name : str = Field(..., description="Last name of the user")
    phone_number : str = Field(..., description="Phone number of the user")

class SUserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., description="Password of the user")
    
class SUserUpdate(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    first_name: str = Field(..., description="First name of the user")
    last_name: str = Field(..., description="Last name of the user")
    phone_number: str = Field(..., description="Phone number of the user")
    
class SProfileCreate(BaseModel):
    birth_date: date|None = Field(None, description="The birth date of the user")
    height: float|None = Field(None, description="The height of the user in meters")
    weight: float|None = Field(None, description="The weight of the user in kilograms")
    gender: str|None = Field(None, description="The gender of the user")
    target_weight: float|None = Field(None, description="The target weight of the user")
    daily_step_goal: int|None = Field(None, description="The daily step goal of the user")

class SMetricsCreate(BaseModel):
    date_of_metrics: str = Field(description="The date of the metrics", default=date.today())
    steps: int = Field(..., description="The number of steps taken")
    calories: int = Field(..., description="The number of calories burned")
    distance: float = Field(..., description="The distance travelled")
    sleep_hours: int = Field(..., description="The number of hours of sleep")
    sleep_score: int = Field(..., description="The sleep quality score")
    calories_intake: int = Field(..., description="The number of calories intake")
    water_ml: int = Field(..., description="The number of milliliters of water consumed")
    mood: int = Field(..., description="The mood level")
    stress_level: int = Field(..., description="The stress level")