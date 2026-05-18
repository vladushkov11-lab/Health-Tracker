from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Optional
class SUserCreate(BaseModel):
    user_id: str = Field(..., description="The unique identifier of the user")
    email: EmailStr = Field(..., description="The email address of the user")
    first_name: str = Field(..., description="The first name of the user")
    last_name: str = Field(..., description="The last name of the user")
    
class SProfileCreate(BaseModel):
    birth_date: date|None = Field(None, description="The birth date of the user")
    height: float|None = Field(None, description="The height of the user in meters")
    weight: float|None = Field(None, description="The weight of the user in kilograms")
    gender: str|None = Field(None, description="The gender of the user")
    target_weight: float|None = Field(None, description="The target weight of the user")
    daily_step_goal: int|None = Field(None, description="The daily step goal of the user")

class SMetricsCreate(BaseModel):
    date_of_metrics: str = Field(..., description="The date of the metrics", examples=["2024-01-01"])
    steps: int = Field(..., description="The number of steps taken")
    calories: int = Field(..., description="The number of calories burned")
    distance: float = Field(..., description="The distance travelled")
    sleep_hours: int = Field(..., description="The number of hours of sleep")
    sleep_score: int = Field(..., description="The sleep quality score")
    calories_intake: int = Field(..., description="The number of calories intake")
    water_ml: int = Field(..., description="The number of milliliters of water consumed")
    mood: int = Field(..., description="The mood level")
    stress_level: int = Field(..., description="The stress level")