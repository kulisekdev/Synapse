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

def updateVar(collection: Collection,userID: int, operation: str, var_name: str, new_value: str):
    """
    Adds XP to the user in my MongoDB Database.

    Variables: \n
    userID: integer | user identification, discord user ID. \n
    amount: integer | amount of XP to add.

    """
    User = collection.find_one({"_id": userID})
    MongoDB_Operator = str()
    if operation == "set":
        MongoDB_Operator == "$set"
    elif operation == "add":
        MongoDB_Operator == "$inc"
    elif operation == "ded":
        MongoDB_Operator == "$inc"
        new_value = -new_value

    if User:
        if isinstance(User["xp"], int):
            try:
                UsersDB.update_one(
                    {"_id": userID},
                    {f"${MongoDB_Operator}": {
                        var_name: new_value
                        }
                    }
                )
                return {"error": False, "msg": "Success!"}
            except PyMongoError as exc:
                return {"error": True, "msg": f"{str(exc)}"}
        else:
            return {"error": True, "msg": f"variable xp is {type(User["xp"])}, supposed to be int"}
    else:
        return {"error": True, "msg": f"<@{userID}> isn't in my database yet."}

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
