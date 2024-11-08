from fastapi import APIRouter

import os
from typing import Optional, List

from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response
from pydantic import ConfigDict, BaseModel, Field
from pydantic.functional_validators import BeforeValidator

from typing_extensions import Annotated

from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument

from MONGODB_URL import MONGODB_URL

router = APIRouter()


client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
PyObjectId = Annotated[str, BeforeValidator(str)]

db = client.get_database("main")
user_collection = db.get_collection("analytics")


class todo(BaseModel):
    """
    Container for a single user record.
    """
    id: Optional[PyObjectId] = Field(alias="id", default=None)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                
            }
        },
    )

class Updatetodo(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                
            }
        },
    )

class todoCollections(BaseModel):
    """
    A container holding a list of `UserModel` instances.

    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """

    users: List[todo]

