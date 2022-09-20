from pydantic import BaseModel, validator
from datetime import datetime
from enum import Enum
from typing import List


class SystemItemType(str, Enum):
    FILE = "FILE"
    FOLDER = "FOLDER"


class ItemData(BaseModel):
    id: str
    url: str | None = None
    date: datetime | None
    parent_id: str | None
    type: SystemItemType
    size: int | None = 0

    class Config:
        orm_mode = True


class ItemResponseData(ItemData):
    children: List | None = []

    @validator("children")
    def replace_empty(cls, val):
        return val or None

    def get_child(self, index):
        if len(self.children) > index:
            return self.children[index]
        return None


class ItemRequestData(BaseModel):
    items : List[ItemData]
    updateDate : datetime

    class Config:
        orm_mode = True


class Error(BaseModel):
    code: int
    message: str

    class Config:
        orm_mode = True
