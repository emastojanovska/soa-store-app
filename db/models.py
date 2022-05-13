from sqlalchemy import Boolean, Column, Integer, String
from pydantic import BaseModel
from db.database import Base
 
class Product(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, index=True)
    price = Column(Integer, nullable=False)
    on_offer = Column(Boolean, default=False)
 
    def __repr__(self):
        return f"<Item name={self.name} price={self.price}>"

class ProductReadDTO(BaseModel): #serializer
    name:str
    description:str
    price:int
    on_offer:bool

    class Config:
        orm_mode=True

class ProductCreateDTO(BaseModel): 
    name: str
    description: str
    price: int

    class Config:
        orm_mode=True