from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class User(BaseModel):
    id: Optional[int]
    email: Optional[str]

    class Config:
        orm_mode = True


class Category(BaseModel):
    id: Optional[int]
    name: Optional[str]

    class Config:
        orm_mode = True


class Course(BaseModel):
    id: Optional[int]
    name: Optional[str]
    category: Optional[Category]
    
    class Config:
        orm_mode = True


class CourseToDb(BaseModel):
    id: Optional[int]
    name: Optional[str]
    category_id: Optional[int]

    class Config:
        orm_mode = True


class Session(BaseModel):
    id: Optional[int]
    user_id: Optional[int]
    opened_on: Optional[datetime]
    is_active: Optional[bool]

    class Config:
        orm_mode = True


class BaseSubscription(BaseModel):
    course_id: Optional[int]
    user_id: Optional[int]
    subscribed_on: Optional[date]
    conclusion_on: Optional[date]

    class Config:
        orm_mode = True


class Subscription(BaseModel):
    course: Optional[Course]
    user: Optional[User]
    subscribed_on: Optional[date]
    conclusion_on: Optional[date]

    class Config:
        orm_mode = True


class BaseSession(BaseModel):
    id: Optional[int]
    user: Optional[User]
    opened_on: Optional[datetime]
    is_active: Optional[bool]

    class Config:
        orm_mode = True