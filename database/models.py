# from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Boolean, DateTime
from sqlalchemy.orm import relationship
from database.db import Base


class Sessions(Base):
    __tablename__ = "session"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    user_id = Column(Integer, ForeignKey("user.id"))
    opened_on = Column(DateTime)
    is_active = Column(Boolean)
    user = relationship("Users", back_populates="sessions") 


class Subscriptions(Base):
    __tablename__ = "subscription"
    course_id = Column(ForeignKey('course.id'))
    user_id = Column(ForeignKey('user.id'))
    subscribed_on = Column(Date)
    conclusion_on = Column(Date)
    course = relationship("Courses", back_populates="users")
    user = relationship("Users", back_populates="courses")


class Courses(Base):
    __tablename__ = "course"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship("Categories", back_populates="courses")
    users = relationship("Subscriptions", back_populates="course")


class Categories(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    courses = relationship("Courses", back_populates="category")


class Users(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String)
    courses = relationship("Subscriptions", back_populates="user")
    sessions = relationship("Sessions", back_populates="user")