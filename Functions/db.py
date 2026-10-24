from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.collection import Collection
import pymongo
from os import getenv
from dotenv import load_dotenv
import traceback
load_dotenv()

DB_Client = MongoClient(getenv("mongodb"))
SynapseDB = DB_Client["Synapse"]
UsersDB = SynapseDB["users"]

def updateVar(collection: Collection, _id: int, operation: str, var_name: str, value):
    """
    Updates a user and its variable with new value \n
    collection: Collection (MongoDB Collection) | Collection definition \n
    userID: integer | user identification, discord user ID. \n
    operation: str (set, add, ded) (set, add, deduct) | type of oepration in database. \n
    var_name: str | variable name inside the document of the user in database. \n
    value: str | new value for variable var_name inside the database. \n

    """
    User = collection.find_one({"_id": _id})
    MongoDB_Operator = str()
    if operation == "set":
        MongoDB_Operator = "$set"
    elif operation == "add":
        MongoDB_Operator = "$inc"
    elif operation == "ded":
        MongoDB_Operator = "$inc"
        value = -value
        if User: 
            if type(value) == type(collection.find_one({"_id": _id})):
                try:
                    print(MongoDB_Operator)
                    UsersDB.update_one(
                        {"_id": _id},
                        {MongoDB_Operator: {
                            var_name: value
                            }
                        }
                    )
                    return {"error": False, "msg": "Success!"}
                except PyMongoError as exc:
                    return {"error": True, "msg": f"{str(exc)}"}
            else:
                return {"error": True, "msg": f"variable xp is {type(User['xp'])}, supposed to be int"}
        else:
            return {"error": True, "msg": f"isn't in database."}

def AddUser(userID: int,username: str):
    """
    Adds an user to my MongoDB Database.

    Variables: \n
    userID: integer | user identification, discord user ID.
    """
    User = UsersDB.find_one({"_id": userID})

    if not User:
        try:
            UsersDB.insert_one({
                "_id": userID,
                "level": 1,
                "CanReceiveXP": True,
                "warnings": 0,
            }
            )
            return {"error": False, "msg": "Success!"}
        except PyMongoError as exc:
            return {"error": True, "msg": f"{str(exc)}"}
    else:
        return {"error": True, "msg": "user is already in my database."}

def DelUser(userID: int,):
    """
    Adds an user to my MongoDB Database.

    Variables: \n
    userID: integer | user identification, discord user ID.
    """
    User = UsersDB.find_one({"_id": userID})

    if User:
        try:
            UsersDB.delete_one({ "_id": userID})
            return {"error": False, "msg": "Success!"}
        except PyMongoError as exc:
            return {"error": True, "msg": f"{str(exc)}"}
    else:
        return {"error": True, "msg": "user is not in my database."}

def GetUser(userID: int):
    try:
        return UsersDB.find_one({"_id": userID})
    except Exception as exc:
        return {"error": False, "msg":f"{str(exc)}"}