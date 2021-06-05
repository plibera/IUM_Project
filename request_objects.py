from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, time

class PredictionInput(BaseModel):
    client_id: int
    city_name: str
    company_id: int
    purchase_day: int
    purchase_time: time


class AdminRequest(BaseModel):
    username: str
    password: str
    first_model_path: str
    is_first_model_keras: int
    second_model_path: Optional[str]
    is_second_model_keras: Optional[int]