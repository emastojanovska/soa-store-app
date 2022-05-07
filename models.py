from sqlalchemy import Boolean, Column, Integer, String
 
from database import Base
 
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, index=True)
    price = Column(Integer, nullable=False)
    on_offer = Column(Boolean, default=False)
 
    def __repr__(self):
        return f"<Item name={self.name} price={self.price}>"