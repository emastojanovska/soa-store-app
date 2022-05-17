import os

from dependency_injector import providers
from dotenv import load_dotenv

from integration.integrations import UserService, PaymentService, NotificationService, 

env_path = '../.env.local'
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = "soa-store-app"
    PROJECT_VERSION: str = "1.0.0"

    DATABASE_URL = os.getenv("POSTGRES_URL_LOCAL", "postgresql://store-app:store-app@localhost:5432/store-app")
    USER_ENDPOINT = os.getenv("USER_APP_URL", "http://localhost:8000/")
    SERVICES_ENDPOINT = os.getenv("SERVICES_APP_URL", "http://localhost:8004/")
    PAYMENT_ENDPOINT = os.getenv("PAYMENT_APP_URL", "http://localhost:8005/")
    NOTIFICATION_ENDPOINT = os.getenv("NOTIFICATIONS_APP_URL", "http://localhost:8006/")
    SHELTER_ENDPOINT = os.getenv("SHELTER_APP_URL", "http://localhost:8003/")
    RESOURCES_ENDPOINT = os.getenv("RESOURCES_APP_URL", "http://localhost:8001/")

    userService = providers.Factory(UserService, USER_ENDPOINT)
    paymentService = providers.Factory(PaymentService, PAYMENT_ENDPOINT)
    notificationService = providers.Factory(NotificationService, NOTIFICATION_ENDPOINT)
    


settings = Settings()
