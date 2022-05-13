
from fastapi import APIRouter,status,HTTPException
from typing import Optional, List
from db.database import SessionLocal
from db.models import  ProductDTO, Product
from fastapi import APIRouter, Depends, Query

router = APIRouter(prefix="/shelter", tags=["Shelter"])

@app.get('/productss', response_model=List[ProductDTO], status_code=200)
def get_all_items():
    items=db.query(Product).all()
    return items

@app.get('/products/{product_id}',response_model=ProductDTO,status_code=status.HTTP_200_OK)
def get_an_iem(product_id:int):
    item=db.query(Product).filter(Product.id==product.name).first()
    return item

@app.post('items',response_model=ProductDTO, status_code=status.HTTP_201_CREATED)
def create_an_item(item:ProductDTO):
    db_item=db.query(Product).filter(Product.name==item.name).first()
    if db_item is not None :
        raise HTTPException(status_code=400,detail="ProductDTO already exists")

    new_item=Product(
        name=item.name,
        price=item.price,
        description=item.description,
        on_offer=item.on_offer
    )
    db.add(new_item)
    db.commit()

    return new_item

@app.delete('/products/{product_id}')
def delete_item(product_id:int):
    item_to_delete=db.query(Product).filter(Product.id==product_id).first()
    if item_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resource not found")
    db.delete(item_to_delete)
    db.commit()
    return item_to_delete

@app.put('/products/{product_id}',response_model=ProductDTO,status_code=status.HTTP_200_OK)
def update_item(product_id:int,item:ProductDTO):
    item_to_update=db.query(Product).filter(Product.id==product.name).first()
    item_to_update.name=item.name
    item_to_update.price=item.price
    item_to_update.description=item.description
    item_to_update.on_offer=item.on_offer

    db.commit()
    return item_to_update