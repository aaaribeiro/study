# from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from database.models import Courses, Categories, Sessions, Users
from schema import schema
from database.db import SessionLocal, engine, Base

Base.metadata.create_all(engine)

class CrudCourse:

    def readCourseByID(self, db: Session, id: int):
        return db.query(Courses).get(id)
        

    def readCourseByName(self, db: Session, name: str):
        return db.query(Courses).\
            filter(Courses.name==name.upper()).first()


    def readCourses(self, db: Session, user: int):
        return db.query(Courses).filter(Courses.user_id==user).all()


    def createCourse(self, db: Session, payload: schema.CourseToDb):
        dbCourse = Courses(
            name = payload.name.upper(),
            category_id = payload.category_id,
            user_id = payload.user_id,
            subscribed_on = payload.subscribed_on,
            conclusion_on = payload.conclusion_on,         
        )
        db.add(dbCourse)
        db.commit()


    def deleteCourse(self, db: Session, payload: Courses):
        db.delete(payload)
        db.commit()


class CrudCategory:

    def readCategoryByID(self, db: Session, id: int):
        return db.query(Categories).get(id)
        

    def readCategoryByName(self, db: Session, name: str):
        return db.query(Categories).\
            filter(Categories.name==name.upper()).first()


    def readCategories(self, db: Session):
        return db.query(Categories).all()


    def createCategory(self, db: Session, payload: schema.Category):
        dbCategory = Categories(
            name = payload.name.upper()
        )
        db.add(dbCategory)
        db.commit()


    def deleteCategory(self, db: Session, payload: Categories):
        db.delete(payload)
        db.commit()



class CrudUser:

    def readUserByID(self, db: Session, id: int):
        return db.query(Users).get(id)

    
    def readUserByName(self, db: Session, email: str):
        return db.query(Users).\
            filter(Users.email==email.upper()).first()


    def readUsers(self, db: Session):
        return db.query(Users).all()


    def createUser(self, db: Session, payload: schema.User):
        dbUser = Users(
            email = payload.email.upper()
        )
        db.add(dbUser)
        db.commit()


    def deleteUser(self, db: Session, payload: Users):
        db.delete(payload)
        db.commit()


class CrudSession:

    def readActiveSession(self, db: Session):
        return db.query(Sessions).\
            filter(Sessions.is_active==True).first()


    def openSession(self, db: Session, payload: schema.Session):
        dbSession = Sessions(
            user_id = payload.user_id,
            opened_on = payload.opened_on,
            is_active = True
        )
        db.add(dbSession)
        db.commit()
    

    def closeSession(self, db: Session, payload: Sessions):
        payload.is_active = False
        db.commit()