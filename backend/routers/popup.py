import sys
import os
from . import model
from fastapi import APIRouter, HTTPException, Body, Query

from pydantic import BaseModel

class DialogQuery(BaseModel):
    prompt: str

model_ai = model.Model()
router = APIRouter()


@router.get("/prompt/{user_id}")
async def get_prompt(user_id: int, dialog_query: DialogQuery):
    # Extract the prompt from the DialogQuery model
    prompt = dialog_query.prompt
    response = model_ai.get_full_answer(prompt, int(user_id))
    return response


