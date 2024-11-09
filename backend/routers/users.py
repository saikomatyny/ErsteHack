from fastapi import APIRouter

import os
from typing import Optional, List

from fastapi import UploadFile, File, HTTPException
import csv
from io import StringIO
from typing import List

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
koefs_collection = db.get_collection("koefs")


class User(BaseModel):
    """
    Container for a single user record.
    """
    id: Optional[PyObjectId] = Field(alias="id", default=None)
    id_product: str = Field(..., alias="id_product")
    name: str = Field(..., alias="name")
    price: float = Field(..., alias="price")
    vat_rate: float = Field(..., alias="vat_rate")
    category: str = Field(..., alias="category")
    organization_id: str = Field(..., alias="organization_id")
    created_date: str = Field(..., alias="created_date")
    last_modified_date: str = Field(..., alias="last_modified_date")
    created_by: str = Field(..., alias="created_by")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id_product": "1",
                "name": "NESTEA CITRÓN 1,5l  ",
                "price": 0.99,
                "vat_rate": 20.0,
                "category": "drinks/non-alcoholic",
                "organization_id": "1",
                "created_date": "2023-09-28 22:57:45",
                "last_modified_date": "2023-09-28 22:57:46",
                "created_by" : "1",
            }
        },
    )

class UpdateUser(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    name: Optional[str] = Field(None, alias="name")
    price: Optional[float] = Field(None, alias="price")
    vat_rate: Optional[float] = Field(None, alias="vat_rate")
    category: Optional[str] = Field(None, alias="category")
    organization_id: Optional[str] = Field(None, alias="organization_id")
    last_modified_date: Optional[str] = Field(None, alias="last_modified_date")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "NESTEA CITRÓN 1,5l  ",
                "price": 0.99,
                "vat_rate": 20.0,
                "category": "drinks/non-alcoholic",
                "organization_id": "1",
                "last_modified_date": "2023-09-28 22:57:46",
            }
        },
    )

class UserCollections(BaseModel):
    """
    A container holding a list of `UserModel` instances.

    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """

    users: List[User]

class Koef(BaseModel):
    """
    Container for a single koef record.
    """
    id: Optional[PyObjectId] = Field(alias="id", default=None)
    created_by: str = Field(..., alias="created_by")
    koef: int = Field(..., alias="koef")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "created_by": "1",
                "koef": 2,
            }
        },
    )

class UpdateKoef(BaseModel):
    """
    Update a single koef record.
    """
    koef: Optional[int] = Field(None, alias="koef")
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "created_by": "1",
                "koef": 2,
            }
        },
    )

class KoefCollections(BaseModel):
    """
    A container holding a list of `KoefModel` instances.

    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """

    koefs: List[Koef]


@router.get(
    "/users/",
    response_description="List all users",
    response_model=UserCollections,
    response_model_by_alias=False,
)
async def list_users():
    """
    List all of the users data in the database.

    The response is unpaginated and limited to 1000 results.
    """
    return UserCollections(users=await user_collection.find().to_list(1000))



@router.post(
    "/users/upload_csv",
    response_description="Add users from CSV file",
    status_code=status.HTTP_201_CREATED,
)
async def upload_csv(file: UploadFile = File(...)):
    """
    Parse and insert filtered user records from a CSV file.
    """
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="File format not supported. Please upload a CSV file.")

    contents = await file.read()
    csv_file = StringIO(contents.decode("utf-8"))
    
    reader = csv.DictReader(csv_file)
    users_to_insert = []
    koefs_to_insert = []

    for row in reader:
        # Извлекаем только нужные поля и преобразуем типы данных, если нужно
        user_data = {
            "id_product": row["id"].strip(),
            "name": row["name"].strip(),
            "price": float(row["price"]),
            "vat_rate": float(row["vat_rate"]),
            "category": row["category"].strip(),
            "organization_id": row["organization_id"].strip(),
            "created_date": row["created_date"],
            "created_by": row["created_by"],
            "last_modified_date": row["last_modified_date"],
        }
        users_to_insert.append(user_data)
        koef_data = {
            "created_by": row["created_by"].strip(),
            "koefficient": 2,
        }
        koefs_to_insert.append(koef_data)
    
    if users_to_insert:
        await user_collection.insert_many(users_to_insert)  # вставляем все записи одной операцией
    koefs_to_insert = [dict(t) for t in {tuple(d.items()) for d in koefs_to_insert}]
    if koefs_to_insert:
        await koefs_collection.insert_many(koefs_to_insert)

    return {"message": f"{len(users_to_insert)} users added successfully from CSV."}


@router.put(
    "/users/{id_product}",
    response_description="Update a product",
    response_model=User,
    response_model_by_alias=False,
)
async def update_user(id_product: str, user: UpdateUser = Body(...)):
    """
    Update individual fields of an existing product record.

    Only the provided fields will be updated.dialog.promptd.
    """
    user = {
        k: v for k, v in user.model_dump(by_alias=True).items() if v is not None
    }

    if len(user) >= 1:
        update_result = await user_collection.find_one_and_update(
            {"id_product": id_product},
            {"$set": user},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"user {id_product} not found")

    # The update is empty, but we should still return the matching document:
    if (existing_user := await user_collection.find_one({"id": id_product})) is not None:
        return existing_user

    raise HTTPException(status_code=404, detail=f"user {id_product} not found")


@router.put(
    "/users/turn_off_notif/{created_by}",
    response_description="Update a koefficient and turn off notifications",
    response_model=None,
    response_model_by_alias=False,
)
async def update_koef(created_by: str):
    """
    Find the user by organization_id and increment koef by 1.
    """
    # Выполняем обновление
    update_result = await koefs_collection.find_one_and_update(
        {"created_by": created_by},  # Поиск по created_by
        {"$inc": {"koefficient": 1}},  # Инкремент коэфициента на 1
        return_document=ReturnDocument.AFTER  # Возвращаем обновленный документ
    )

    if update_result:
        return {
            "created_by": update_result["created_by"],
            "koefficient": update_result["koefficient"]
        }
    else:
        raise HTTPException(status_code=404, detail=f"User with organization_id {created_by} not found")
    
    