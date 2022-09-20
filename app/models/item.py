from .db import Base
from sqlalchemy import Column, String, Enum, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship, backref
from app.schems import SystemItemType
from typing import List


class Items(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True)
    url = Column(String, nullable=True)
    date = Column(DateTime, nullable=False)
    parent_id = Column(String, ForeignKey("items.id", ondelete="CASCADE"), nullable=True)
    type = Column(Enum(SystemItemType), nullable=False)
    size = Column(Integer, nullable=True, default=0)
    children: List["Items"] = relationship("Items", backref=backref("parent", remote_side=[id]),
                                           cascade="all, delete-orphan")

    def __str__(self):
        return f"Item {self.id = }  {self.url = }  {self.type = } {self.size = }  {self.date = }"
