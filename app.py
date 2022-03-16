from calendar import c
import click
import pandas as pd
from tabulate import tabulate
from datetime import datetime, date, timedelta

from database.crud import CrudCategory, CrudCourse, CrudSession, CrudUser
from database.handler import DbHandler
from schema import schema


@click.group()
def main():
    pass


def createCategory(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return

    category = click.prompt("Category", type=str)
    crud = CrudCategory()
    with DbHandler() as db:
        dbCategory = crud.readCategoryByName(db, category)
        if dbCategory:
            click.secho("category already exists", fg="red")
            ctx.abort()   
    
    payload = schema.Category(name=category)
    with DbHandler() as db:
        crud.createCategory(db, payload)
        click.secho("New category created", fg="green")
        dbCategory = crud.readCategoryByName(db, category)
        click.secho("Name: ", fg="blue", bold=True, nl=None)
        click.echo(f"{dbCategory.name.title()}")
    ctx.exit()


def deleteCategory(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return
    
    category = click.prompt("Category", type=str)
    crud = CrudCategory()
    with DbHandler() as db:
        dbCategory = crud.readCategoryByName(db, category)
        if not dbCategory:
            click.secho("Category not found", fg="red")
            ctx.abort()
        categoryID = dbCategory.id
        dbCourses = crud.readCoursesByCategory(db, categoryID)
        if dbCourses:
            click.secho("Course assigned to course", fg="red")
            ctx.abort()
        if click.confirm('Are you sure?', abort=True):
            crud.deleteCategory(db, dbCategory)
            click.secho("Category deleted", fg="green")
        ctx.exit()


@main.command()
@click.option("--new", is_flag=True, callback=createCategory, 
                expose_value=False)
@click.option("--delete", is_flag=True, callback=deleteCategory, 
                expose_value=False)
def category():
    crud = CrudCategory()
    with DbHandler() as db:
        dbCategories = crud.readCategories(db)
        listCategories = []
        for category in dbCategories:
          listCategories.append(schema.Category.from_orm(category).dict())   

    if len(listCategories) == 0:
        click.secho("Categories not found", fg="red")
        exit()

    df = pd.json_normalize(listCategories)
    df.name = df.name.apply(lambda x: x.title())
    df.rename(str.title, axis="columns", inplace=True)
    click.echo(tabulate(df, headers="keys", showindex=False
                        ,tablefmt="simple"))



def createCourse(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return

    course = click.prompt("Course", type=str)
    crud = CrudCourse()
    with DbHandler() as db:
        dbCourse = crud.readCourseByName(db, course)
        if dbCourse:
            click.secho("Course already exists", fg="red")
            ctx.abort()
    
    category = click.prompt("Category", type=str)
    crud = CrudCategory()
    with DbHandler() as db:
        dbCategory = crud.readCategoryByName(db, category)
        if not dbCategory:
            click.secho("Category not found", fg="red")
            ctx.abort()
        categoryID = dbCategory.id
    
    payload = schema.CourseToDb(
        name = course,
        category_id = categoryID,
    )
    crud = CrudCourse()
    with DbHandler() as db:
        crud.createCourse(db, payload)
        click.secho("New course created", fg="green")
        dbCourse = crud.readCourseByName(db, course)
        courseID = dbCourse.id
        click.secho("Name: ", fg="blue", bold=True, nl=None)
        click.echo(f"{dbCourse.name.title()}")

    if click.confirm("Do you want to subscribe?"):
        subscribed = click.prompt("Subscribed on", default=date.today())
        conclusion = click.prompt("Conclusion on",
                                    default=date.today() + timedelta(weeks=24))
        crud = CrudSession()
        with DbHandler() as db:
            dbUser = crud.readActiveSession(db)
            userID = dbUser.user_id
        payload = schema.BaseSubscription(
            course_id = courseID,
            user_id = userID,
            subscribed_on = subscribed,
            conclusion_on = conclusion
        )
        crud = CrudCourse()
        with DbHandler() as db:
            crud.createSubscription(db, payload)
            click.secho("User subscribed", fg="green")
    ctx.exit()


def deleteCourse(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return

    course = click.prompt("Course", type=str)
    crud = CrudCourse()
    with DbHandler() as db:
        dbCourse = crud.readCourseByName(db, course)
        if not dbCourse:
            click.secho("Course not found", fg="red")
            ctx.abort()
        courseID = dbCourse.id
        dbSubscriptions = crud.readCourseSubscription(db, courseID)
        if dbSubscriptions:
            click.secho("Course has users subscribed", fg="red")
            ctx.abort()
        if click.confirm('Are you sure?', abort=True):
            crud.deleteCourse(db, dbCourse)
            click.secho("Course delete", fg="green")
    ctx.exit()

@main.command()
@click.option("--new", is_flag=True, callback=createCourse, 
                expose_value=False)
@click.option("--delete", is_flag=True, callback=deleteCourse, 
                expose_value=False)
def course():
    crud = CrudCourse()
    with DbHandler() as db:
        dbCourses = crud.readCourses(db)
        listCourses = []
        for course in dbCourses:
            listCourses.append(schema.Course.from_orm(course).dict()) 
    
    if len(listCourses) == 0:
        click.secho("Courses not found", fg="red")
        exit()

    df = pd.json_normalize(listCourses)
    df.rename(columns={"category.name": "category"}, inplace=True)
    df.category = df.category.apply(lambda x: x.title())
    df.name = df.name.apply(lambda x: x.title())
    df = df.reindex(columns=["id", "name", "category"])
    df.rename(str.title, axis="columns", inplace=True)    
    click.echo(tabulate(df, headers="keys", showindex=False ,tablefmt="simple"))
    



def createSubscription(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return

    course = click.prompt("Course", type=str)
    crud = CrudCourse()
    with DbHandler() as db:
        dbCourse = crud.readCourseByName(db, course)
        if not dbCourse:
            click.secho("Course not found", fg="red")
            ctx.abort()
        courseID = dbCourse.id
    subscribed = click.prompt("Subscribed on", default=date.today())
    conclusion = click.prompt("Conclusion on",
                                default=date.today() + timedelta(weeks=24))
    crud = CrudSession()
    with DbHandler() as db:
        dbUser = crud.readActiveSession(db)
        userID = dbUser.user_id
    payload = schema.BaseSubscription(
        course_id = courseID,
        user_id = userID,
        subscribed_on = subscribed,
        conclusion_on = conclusion
    )
    crud = CrudCourse()
    with DbHandler() as db:
        crud.createSubscription(db, payload)
        click.secho("User subscribed", fg="green")
    ctx.exit()


def deleteSubscription(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return
    
    course = click.prompt("Course", type=str)
    crud = CrudCourse()
    with DbHandler() as db:
        dbCourse = crud.readCourseByName(db, course)
        if not dbCourse:
            click.secho("Course not found", fg="red")
            ctx.abort()
        courseID = dbCourse.id
    
    crud = CrudSession()
    with DbHandler() as db:
        dbSession = crud.readActiveSession(db)
        if not dbSession:
            click.secho("User not active", fg="red")
            ctx.abort()
        userID = dbSession.user_id
    
    if click.confirm('Are you sure?', abort=True):
        crud = CrudCourse()
        with DbHandler() as db:
            dbSubscription = crud.readSubscriptionByCourse(db, userID, courseID)
            if not dbSubscription:
                click.secho("User not subscribed in this course", fg="red")
                ctx.abort()
            crud.deleteSubscription(db, dbSubscription)
            click.secho("Subscription deleted", fg="green")
    ctx.exit()


@main.command()
@click.option("--new", is_flag=True, callback=createSubscription, 
                expose_value=False)
@click.option("--delete", is_flag=True, callback=deleteSubscription, 
                expose_value=False)
def subscription():
    crud = CrudSession()
    with DbHandler() as db:
        dbSession = crud.readActiveSession(db)
        userID = dbSession.user_id

    crud = CrudCourse()
    with DbHandler() as db:
        dbCourses = crud.readSubscriptions(db, userID)
        listCourses = []
        for course in dbCourses:
            listCourses.append(schema.Subscription.from_orm(course).dict()) 
    
    if len(listCourses) == 0:
        click.secho("No courses subscribed", fg="red")
        exit()

    df = pd.json_normalize(listCourses)
    df.rename(columns={"course.category.name": "category",
            "user.email": "user", "course.name": "course"}, inplace=True)
    df.course = df.course.apply(lambda x: x.title())
    df.category = df.category.apply(lambda x: x.title())
    df.user = df.user.apply(lambda x: x.lower())
    df.rename(str.title, axis="columns", inplace=True)
    df = df.reindex(columns=["User", "Course", "Category", "Subscribed_On",
                            "Conclusion_On"])
    click.echo(tabulate(df, headers="keys", showindex=False, tablefmt="simple"))
    


def createUser(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return
    
    user = click.prompt("User", type=str)
    crud = CrudUser()
    with DbHandler() as db:
        dbUser = crud.readUserByName(db, user)
        if dbUser:
            click.secho("User already created")
            ctx.abort()
        payload = schema.User(
            email = user.upper()
        )            
        crud.createUser(db, payload)
        click.secho("New user created", fg="green")
    ctx.exit()



def deleteUser(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return
    
    user = click.prompt("User", type=str)
    crud = CrudSession()
    with DbHandler() as db:
        dbSession = crud.readActiveSession(db)
        try:
            userCurrentSession = dbSession.user_id
        except AttributeError:
            userCurrentSession = 0
    crud = CrudUser()
    with DbHandler() as db:
        dbUser = crud.readUserByName(db, user)
        if not dbUser:
            click.secho("User not found", fg="red")
            ctx.abort()
        userID = dbUser.id
        if userID == userCurrentSession:
            click.secho("User has an active session", fg="red")
            ctx.abort()
        dbSubscriptions = crud.readCoursesByUser(db, userID)
        if dbSubscriptions:
            click.secho("User has courses subscribed", fg="red")
            ctx.abort()
        if click.confirm('Are you sure?', abort=True):
            crud.deleteUser(db, dbUser)
            click.secho("User deleted", fg="green")
        ctx.exit()


@main.command()
@click.option("--new", is_flag=True, callback=createUser,
                expose_value=False)
@click.option("--delete", is_flag=True, callback=deleteUser,
                expose_value=False)
def user():
    crud = CrudUser()
    with DbHandler() as db:
        dbUsers = crud.readUsers(db)
        listUsers = []
        for user in dbUsers:
          listUsers.append(schema.User.from_orm(user).dict())   

    if len(listUsers) == 0:
        click.secho("Users not found", fg="red")
        exit()

    df = pd.json_normalize(listUsers)
    df.rename(str.title, axis="columns", inplace=True)
    df.Email = df.Email.apply(lambda x: x.lower())
    click.echo(tabulate(df, headers="keys", showindex=False
                        ,tablefmt="simple"))
    

def login(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return

    crud = CrudUser()
    user = click.prompt("User", type=str)
    with DbHandler() as db:
        dbUser = crud.readUserByName(db, user)
        if not dbUser:
            click.secho("user not found, please check or create a new one",
                        fg="red")
            ctx.exit()
        else:
            userID = dbUser.id

    crud = CrudSession()
    with DbHandler() as db:    
        dbSession = crud.readActiveSession(db)
        if dbSession:
            if dbSession.user_id == userID:
                click.secho("session already opened", fg="green")
                ctx.exit()
            else: 
                click.secho("another user has an opened session, please logoff",
                            fg="red")
                ctx.exit()     
        session = schema.Session(
            user_id = dbUser.id,
            opened_on = datetime.today(),
            is_active = True
        )                    
        dbSession = crud.openSession(db, session)
        click.secho("user logged on", fg="green")
    ctx.exit()


def logoff(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return
    
    crud = CrudSession()
    with DbHandler() as db:
        dbSession = crud.readActiveSession(db)
        if not dbSession:
            click.secho("no session actived, please login", fg="red")
            exit()
        crud.closeSession(db, dbSession)
        click.secho("session closed", fg="green")
    ctx.exit()


@main.command()
@click.option("--login", is_flag=True, callback=login, expose_value=False)
@click.option("--logoff", is_flag=True, callback=logoff, expose_value=False)
def session():
    crud = CrudSession()
    with DbHandler() as db:
        dbSession = crud.readActiveSession(db)
        if not dbSession:
            click.secho("no active session", fg="red")
            exit()

        session = schema.BaseSession.from_orm(dbSession).dict()
        df = pd.json_normalize(session)
        df.drop(["user.id",], inplace=True, axis=1)
        df.rename(columns={"user.email": "user"}, inplace=True)
        df.user = df.user.apply(lambda x: x.lower())
        df.rename(str.title, axis="columns", inplace=True)
        df = df.reindex(columns=["Id", "User", "Opened_On", "Is_Active"])
        click.echo(tabulate(df, headers="keys", showindex=False
                        ,tablefmt="simple"))


if __name__ == "__main__":
    main()