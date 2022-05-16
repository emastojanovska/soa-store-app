from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import relationship 
from db.database import Base
from db.enumerations.enum import Status, Category
import datetime

class Image(BaseModel):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True, index=True)
    url: HttpUrl
    mimeType: str
    imageDataBase64: str
    imageSrc: str
    name: str
    imageData: list = []

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    shopping_cart_id = Column(Integer, ForeignKey('shopping_cart.id'), unique=True)
    shopping_cart = relationship("ShoppingCart", backref=backref("user", uselist=False))
    orders =  relationship("Order", back_populates="user")

class ShoppingCart(Base):
    __tablename__ = "shopping_cart"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    products = relationship("ProductInShoppingCart", back_populates="shopping_cart")
        
 
class ProductInShoppingCart(Base):
    __tablename__ = "product_in_shopping_cart"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer)
    product_id = Column(Integer, ForeignKey('product.id'))  
    product = relationship("Product", back_populates="products_in_shopping_cart")  
    shopping_cart_id = Column(Integer, ForeignKey('shopping_cart.id'))
    shopping_cart = relationship("ShoppingCart", back_populates="products")
 

class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, index=True)
    category = Column(Enum(Category)) 
    price = Column(Integer, nullable=False)
    on_offer = Column(Boolean, default=False) 
    products_in_shopping_cart = relationship("ProductInShoppingCart", back_populates="product")
    def __repr__(self):
        return f"<Product name={self.name} price={self.price}>"

class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, index=True)
    total_price = Column(Double)
    status = Column(Enum(Status))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="orders")

class ProductDTO(BaseModel): #serializer
    name:str
    description:str
    category:str
    price:int
    on_offer:bool

    class Config:
        orm_mode=True

class ProductCreateDTO(BaseModel): 
    name: str
    description: str
    category: str
    price: int

    class Config:
        orm_mode=True

class OrderDTO(BaseModel): #serializer
    username:str
    status:str
    date:str
    total_price:double

    class Config:
        orm_mode=True