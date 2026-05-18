from enum import Enum

class Gender(str, Enum):
    male = "Мужской"
    female = "Женский"
class Workout_type(str, Enum):
    running = "Бег"
    cycling = "Велосипед"
    swimming = "Плавание"
    skipping = "Скакалка"
    yoga = "Йога"
    strength = "Силовые"
