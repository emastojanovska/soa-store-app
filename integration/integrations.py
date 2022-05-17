from fastapi import HTTPException, Header
import requests
from typing import Optional, List
from db.models import OrderDTO


class UserService:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def user_contains_role(self, jwttoken: str, roleName: str):
        try:
            response = requests.get(self.endpoint + "role/userContains", data={"roleName": roleName},
                                    headers={"accessToken": jwttoken})
        except:
            raise HTTPException(408, "Cannot reach " + self.endpoint)
        has_access = response.json()
        return has_access

    def current_user_info(self, jwttoken: str):
        try:
            response = requests.get(self.endpoint + "user/info",
                                    headers={"accessToken": jwttoken})
        except:
            raise HTTPException(408, "Cannot reach " + self.endpoint)
        username = response.json()['preferred-username']
        return username
       
    def register_customer(self, username: str, password: str):
        try:
            response = requests.post(self.endpoint + "user/register/customer", data={"username": username, "password": password})
        except:
            raise HTTPException(response.status_code)
        return response.status_code

    def register_employee(self, username:str, password:str, jwttoken:str):
        try:
            response = requests.post(self.endpoint + "user/register/employee", data={"username": username, "password": password}, headers={"accessToken": jwttoken})
        except:
            raise HTTPException(response.status_code)
        return response.status_code



class PaymentService:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def make_payment(self, store_order: OrderDTO, jwttoken: str):
        try:
            response = requests.post(self.endpoint + "api/v1/pay", data={"txStore": store_order}, headers={"accessToken": jwttoken})
        except:
            raise HTTPException(408, "Cannot reach " + self.endpoint)
        return response.json()


class NotificationService:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def notify(self):
        try:
            response = requests.get(self.endpoint + "notify")
        except:
            raise HTTPException(408, "Cannot reach " + self.endpoint)
        return response.json()


