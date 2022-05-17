from fastapi import FastAPI,status,HTTPException, Depends, Header
from dependency_injector.wiring import Provide
from typing import Optional, List
from db.database import SessionLocal
from db.models import  ProductDTO, Product, UserDTO, User, ShoppingCart, ProductInShoppingCart, Order, OrderDTO
from fastapi_pagination import Page, PaginationParams
from fastapi_pagination.ext.sqlalchemy import paginate 
from db.enumerations.enum import Status, Category
from sqlalchemy.orm import sessionmaker, Session
from config import settings 
from integration.integrations import UserService, PaymentService, NotificationService
from enum import Enum

db=SessionLocal()

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

#User 
#Todo: Create an api that register a user with username, password and role 
#Call the api from user service for registering an user (employee/customer)
#If it has the role of a cusomer create him an empty shopping cart
#Set its username and role
#Save it to OUR database
@app.post('/register/customer', response_model=UserDTO, status_code=202)
def register_customer(username:str, password:str, 
                      userService: UserService = Depends(Provide[settings.userService])):
    register_status = userService.register_customer(username, password)
    if(register_status == 401): 
        raise HTTPException(401)
    new_shopping_cart = ShoppingCart(username)
    db.add(new_shopping_cart)
    new_user = User(username = username, password = password, role = 'customer', shopping_cart = new_shopping_cart)
    db.add(new_user)
    return UserDTO(username = username, is_active=True, role="customer")

@app.post('/register/employee', response_model=UserDTO, status_code=202)
def register_customer(username:str, password:str, role:str, Authorization:Optional[str] = Header(None),
                      userService: UserService = Depends(Provide[settings.userService])):
    if (Authorization == None):
        raise HTTPException(status_code=401, detail="You need to authenticate first")
    register_status = userService.register_employee(username, password, role, Authorization)
    if(register_status == 401): 
        raise HTTPException(401)
    new_shopping_cart = ShoppingCart(username)
    db.add(new_shopping_cart)
    new_user = User(username = username, password = password, role = 'customer', shopping_cart = new_shopping_cart)
    db.add(new_user)
    return UserDTO(username = username, is_active=True, role="employee")


#Products
@app.get('/products', response_model=List[Product], status_code=200)
def get_all_products():
    items=db.query(Product).all()
    return items

@app.get('/products/{product_id}',response_model=Product,status_code=status.HTTP_200_OK)
def get_product_details(product_id:int):
    item=db.query(Product).filter(Product.id==product_id).first()
    return item

@app.get('/products/{product_name}',response_model=Product,status_code=status.HTTP_200_OK)
def get_product_details_name(product_name:str):
    item=db.query(Product).filter(Product.name==product_name).first()
    return item


@app.get('/products-pageable', response_model=Page[Product])
def get_products_pageable(db: Session = Depends(get_db), params: PaginationParams = Depends()):
    return paginate(db.query(Product), params)

@app.post('/products',response_model=Product, status_code=status.HTTP_201_CREATED)
def create_an_item(product:ProductDTO, Authorization:Optional[str] = Header(None),
                    userService: UserService = Depends(Provide[settings.userService])):
    #Todo: get the logged in user and check if it has the role of employee
    if (Authorization == None):
        raise HTTPException(status_code=401, detail="You need to authenticate first")

    if (
            not userService.user_contains_role(Authorization, "employee") or
            not userService.user_contains_role(Authorization, "admin")
    ):
        raise HTTPException(status_code=401, detail="Forbidden access to this endpoint")

    db_item=db.query(Product).filter(Product.name==product.name).first()
    if db_item is not None :
        raise HTTPException(status_code=400,detail="ProductDTO already exists")

    new_item=Product(
        name=product.name,
        price=product.price,
        category=product.category,
        description=product.description,
        on_offer=product.on_offer
    )
    db.add(new_item)
    db.commit()

    return new_item

@app.delete('/products/{product_id}')
def delete_item(product_id:int, Authorization:Optional[str] = Header(None),
                userService: UserService = Depends(Provide[settings.userService])):
    #Todo: get the logged in user and check if it has the role of employee
    if (Authorization == None):
        raise HTTPException(status_code=401, detail="You need to authenticate first")

    if (
            not userService.user_contains_role(Authorization, "employee") or
            not userService.user_contains_role(Authorization, "admin")
    ):
        raise HTTPException(status_code=401, detail="Forbidden access to this endpoint")
    item_to_delete=db.query(Product).filter(Product.id==product_id).first()
    if item_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resource not found")
    db.delete(item_to_delete)
    db.commit()
    return item_to_delete

@app.put('/products/{product_name}',response_model=Product,status_code=status.HTTP_200_OK)
def update_item(product_name, product:ProductDTO, Authorization:Optional[str] = Header(None),
                userService: UserService = Depends(Provide[settings.userService])):
    #Todo: get the logged in user and check if it has the role of employee
    if (Authorization == None):
        raise HTTPException(status_code=401, detail="You need to authenticate first")

    if (
            not userService.user_contains_role(Authorization, "employee") or
            not userService.user_contains_role(Authorization, "admin")
    ):
        raise HTTPException(status_code=401, detail="Forbidden access to this endpoint")
    item_to_update=db.query(Product).filter(Product.name==product.name).first()
    item_to_update.name=product.name
    item_to_update.price=product.price
    item_to_update.description=product.description
    item_to_update.on_offer=product.on_offer

    db.commit()
    return item_to_update

@app.get('/filter-products',response_model=List[Product],status_code=status.HTTP_200_OK)
def filter_products(product:ProductDTO):
    items_filtered=db.query(Product).filter(Product.name == product.name || Product.price == product.price || Product.description == product.description ||Product.on_offer == product.on_offer).list()
    return items_filtered

#Shopping Cart
@app.post('/shopping_cart/{new_product_id}')
def add_to_shopping_cart(new_product_id:int, Authorization:Optional[str] = Header(None),
                         userService: UserService = Depends(Provide[settings.userService])):
    # Todo: get the logged in user ==> User.username
    if (Authorization == None):
        raise HTTPException(status_code=401, detail="You need to authenticate first")

    if (
            not userService.user_contains_role(Authorization, "customer") or
            not userService.user_contains_role(Authorization, "employee") or
            not userService.user_contains_role(Authorization, "admin")
    ):
        raise HTTPException(status_code=401, detail="Forbidden access to this endpoint")
    username = userService.current_user_info(Authorization)
    user = db.query(User).filter(User.username==username).first()
    shopping_cart_user = db.query(ShoppingCart).filter(ShoppingCart.username == username).first()
    item_to_add=db.query(Product).filter(Product.id==new_product_id).first()
    if item_to_add is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resource not found")
    product_to_add = db.query(ProductInShoppingCart).filter(ProductInShoppingCart.shopping_cart_id == shopping_cart_user.id 
                                                            and ProductInShoppingCart.product_id==new_product_id).first()
      
    if(product_to_add is None):
        product_in_shopping_cart = ProductInShoppingCart()
        product_in_shopping_cart.shopping_cart_id=shopping_cart_user.id
        product_in_shopping_cart.quantity = 0
        db.add(product_in_shopping_cart)
    else:
        product_to_add.quantity += 1
    db.commit()

@app.delete('/shopping_cart/{product_id_delete}')
def remove_from_shopping_cart(product_id_delete:int, Authorization:Optional[str] = Header(None),
                         userService: UserService = Depends(Provide[settings.userService])):
    # Todo: get the logged in user ==> User.username
    if (Authorization == None):
        raise HTTPException(status_code=401, detail="You need to authenticate first")

    if (
            not userService.user_contains_role(Authorization, "customer") or
            not userService.user_contains_role(Authorization, "employee") or
            not userService.user_contains_role(Authorization, "admin")
    ):
        raise HTTPException(status_code=401, detail="Forbidden access to this endpoint")
    username = userService.current_user_info(Authorization)
    shopping_cart_user = db.query(ShoppingCart).filter(ShoppingCart.username == username).first()
    item_to_delete=db.query(Product).filter(Product.id==product_id_delete).first()
    if item_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resource not found")
    product_to_delete = db.query(ProductInShoppingCart).filter(ProductInShoppingCart.shopping_cart_id == shopping_cart_user.id
                                                                and ProductInShoppingCart.product_id==product_id_delete).first()
      
    if(product_to_delete.quantity == 1):
        db.delete(product_to_delete)
    else:
        product_to_delete.quantity -= 1
    db.commit()

@app.get('/clear_shopping_cart/{shopping_cart_id}', response_model=ShoppingCart,status_code=status.HTTP_200_OK)
def clear_shopping_cart(shopping_cart_id:int):
    products_to_delete = db.query(ProductInShoppingCart).filter(ProductInShoppingCart.shopping_cart_id==shopping_cart_id).list()
    for p in products_to_delete:
        db.delete(p)
    db.commit()

@app.post('/orders',response_model=Order, status_code=status.HTTP_201_CREATED)
def make_an_order(Authorization:Optional[str] = Header(None),
                    userService: UserService = Depends(Provide[settings.userService]),
                    paymentService: PaymentService = Depends(Provide[settings.paymentService])):
    #Todo: get the logged in user 
    #shopping_cart_id = user.shopping_cart_id
    if (Authorization == None):
        raise HTTPException(status_code=401, detail="You need to authenticate first")

    if (
            not userService.user_contains_role(Authorization, "customer") or
            not userService.user_contains_role(Authorization, "employee") or
            not userService.user_contains_role(Authorization, "admin")
    ):
        raise HTTPException(status_code=401, detail="Forbidden access to this endpoint")
    username = userService.current_user_info(Authorization)
    shopping_cart_user = db.query(ShoppingCart).filter(ShoppingCart.username == username).first()
    new_order = Order()
    new_order.status = Enum(Status.NEW)
    products_to_order = db.query(ProductInShoppingCart).filter(ProductInShoppingCart.shopping_cart_id = shopping_cart_user.id).list()
    total = 0.0
    for product in products_to_order:
        total += product.price * product.quantity
    new_order.total_price = total
    db.add(new_order)
    db.commit()
    #Todo: Сервис за наплата
    txObject = OrderDTO(
        username = username,
        order_status = new_order.status,
        date = new_order.date_created,
        total_price = new_order.total_price,
    )
    paymentService.make_payment(txObject, Authorization)
    #Todo: Нотификациски сервис success/error
    return new_order

 
@app.get('/orders', response_model=List[Order], status_code=200)
def get_all_orders():
    items=db.query(Order).all()
    return items

@app.get('/orders/{order_id}',response_model=Order,status_code=status.HTTP_200_OK)
def get_order_details(order_id:int):
    item=db.query(Order).filter(Order.id==order_id).first()
    return item

@app.get('/orders/{customer_username}',response_model=List[Order],status_code=status.HTTP_200_OK)
def get_orders_by_customer(customer_username:str):
    user = db.query(User).filter(User.username = customer_username).first()
    orders = db.query(Order).filter(Order.user_id == user.id)
    return orders

@app.get('/filter-orders',response_model=List[Order],status_code=status.HTTP_200_OK)
def filter_order(order:OrderDTO):
    items_filtered=db.query(Order).filter(Order.date_created == order.date_created || Order.status == order.status || Order.user_id == order.user_id).list()
    return items_filtered


 