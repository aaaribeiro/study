import click
import pandas as pd
import json
from tabulate import tabulate
from datetime import datetime, date

from database.crud import CrudCategory, CrudCourse, CrudSession, CrudUser
from database.handler import DbHandler
from schema import schema


def getUser():
    try:
        settings = click.open_file(".config/settings.config", "r")
    except FileNotFoundError:
        click.secho("user not set, please run config command first", fg="red")
        exit()
    currentUser = json.loads(settings.read())
    return int(currentUser["id"]), currentUser["email"] 


def checkUser(ctx, param, value):
    crud = CrudUser()
    with DbHandler() as db:
        dbUser = crud.readUserByName(db, value)
        if not dbUser:
            payload = schema.User(
                email = value.upper()
            )            
            crud.createUser(db, payload)
            click.secho("new user created", fg="green")
    return value


def checkCategory(ctx, param, value):
    crud = CrudCategory()
    with DbHandler() as db:
        dbCategory = crud.readCategoryByName(db, value)
        if dbCategory:
            raise click.BadParameter("category already exists")   
    return value


def checkNotCategory(ctx, param, value):
    crud = CrudCategory()
    with DbHandler() as db:
        dbCategory = crud.readCategoryByName(db, value)
        if not dbCategory:
            raise click.BadParameter("category not found")  
    return value


def checkCourse(ctx, param, value):
    crud = CrudCourse()
    with DbHandler() as db:
        dbCourse = crud.readCourseByName(db, value)
        if dbCourse:
            raise click.BadParameter("course already exists")    
    return value


def checkNotCourse(ctx, param, value):
    crud = CrudCourse()
    with DbHandler() as db:
        dbCourse = crud.readCourseByName(db, value)
        if not dbCourse:
            raise click.BadParameter("course not found")
    return value


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
            ctx.exit()   
    
    payload = schema.Category(name=category)
    with DbHandler() as db:
        crud.createCategory(db, payload)
        click.secho("New category created", fg="green")
        dbCategory = crud.readCategoryByName(db, category)
        click.secho("Name: ", fg="blue", bold=True, nl=None)
        click.echo(f"{dbCategory.name.title()}")
    ctx.exit()


@main.command()
@click.option("--new", "-n", is_flag=True, callback=createCategory)
def category():
    pass
#     crud = CrudCategory()
#     payload = schema.Category(name=name)
#     with DbHandler() as db:
#         crud.createCategory(db, payload)
#         click.secho("New category created", fg="green")
#         dbCategory = crud.readCategoryByName(db, name)
#         click.secho("Name: ", fg="blue", bold=True, nl=None)
#         click.echo(f"{dbCategory.name.title()}")


# @main.command()
# @click.option("--name", prompt=True, type=str, is_eager=True,
#                 callback=checkCourse)
# @click.option("--category", prompt=True, type=str, 
#                 callback=checkNotCategory)
# @click.option("--subscribed", prompt=True, default=date.today)
# @click.option("--conclusion", prompt=True)
# def course(name, category, subscribed, conclusion) :

#     userID, userEmail = getUser()
#     crud = CrudUser()
#     with DbHandler() as db:
#         dbUser = crud.readUserByID(db, userID)
#         if not dbUser:
#             click.secho("user not found, please run config command first",
#                         fg="red")
#             exit()

#     crud = CrudCategory()
#     with DbHandler() as db:
#         dbCategory = crud.readCategoryByName(db, category)
#     categoryID = dbCategory.id

#     crud = CrudCourse()
#     course = schema.CourseToDb(
#         name = name,
#         category_id = categoryID,
#         user_id = userID,
#         subscribed_on = subscribed,
#         conclusion_on = conclusion,
#     )
#     with DbHandler() as db:
#         crud.createCourse(db, course)    
#         click.secho("New course created", fg="green")
#         dbCourse = crud.readCourseByName(db, name)
#         click.secho("Name: ", fg="blue", bold=True, nl=None)
#         click.echo(f"{dbCourse.name.title()}")
#         click.secho("Category: ", fg="blue", bold=True, nl=None)
#         click.echo(f"{dbCourse.category.name.title()}")
#         click.secho("User: ", fg="blue", bold=True, nl=None)
#         click.echo(f"{userEmail.lower()}")
#         click.secho("Subscribed on: ", fg="blue", bold=True, nl=None)
#         click.echo(f"{dbCourse.subscribed_on}")
#         click.secho("Conclusion on: ", fg="blue", bold=True, nl=None)
#         click.echo(f"{dbCourse.conclusion_on}")


# @main.command()
# def subscribed():
#     userID = getUser()[0]
#     crud = CrudCourse()
#     with DbHandler() as db:
#         dbCourses = crud.readCourses(db, userID)
#         listCourses = []
#         for course in dbCourses:
#             listCourses.append(schema.Course.from_orm(course).dict()) 
    
#     if len(listCourses) == 0:
#         click.secho("no courses subscribed", fg="red")
#         exit()

#     df = pd.json_normalize(listCourses)
#     df.rename(columns={"category.name": "category",
#                         "user.id": "user"}, inplace=True)
#     df.rename(str.title, axis="columns", inplace=True)
#     df.drop("Category.Id", inplace=True, axis=1)
#     df.Category = df.Category.apply(lambda x: x.title())
#     df.Name = df.Name.apply(lambda x: x.title())
#     df = df.reindex(columns=["Id", "Name", "Category", "Subscribed_On",
#                             "Conclusion_On"])
#     click.echo(tabulate(df, headers="keys", showindex=False
#                         ,tablefmt="simple"))
    


def deleteUser(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return
    
    user = click.prompt("User", type=str)
    crud = CrudUser()
    with DbHandler() as db:
        dbUser = crud.readUserByName(db, user)
        if not dbUser:
            click.secho("user not found", fg="red")
            ctx.exit()
        if click.confirm('are you sure?', abort=True):
            crud.deleteUser(db, dbUser)
            click.secho("user deleted", fg="green")
        ctx.exit()


def createUser(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return
    
    user = click.prompt("User", type=str)
    crud = CrudUser()
    with DbHandler() as db:
        dbUser = crud.readUserByName(db, user)
        if dbUser:
            click.secho("user already created")
            ctx.exit()
        payload = schema.User(
            email = user.upper()
        )            
        crud.createUser(db, payload)
        click.secho("new user created", fg="green")
    ctx.exit()


@main.command()
@click.option("--new", "-n", is_flag=True, callback=createUser,
                expose_value=False)
@click.option("--delete", "-d", is_flag=True, callback=deleteUser,
                expose_value=False)
def user():
    crud = CrudUser()
    with DbHandler() as db:
        dbUsers = crud.readUsers(db)
        listUsers = []
        for user in dbUsers:
          listUsers.append(schema.User.from_orm(user).dict())   

    if len(listUsers) == 0:
        click.secho("users not found", fg="red")
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