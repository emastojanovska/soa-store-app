from enum import Enum
 
class Status(Enum):
    NEW = 1
    PROCESSING = 2
    SEND_TO_DELIVER = 3
    DELIVERED = 4

class Category(Enum):
    TOYS = 1
    MEDICINE = 2
    FOOD = 3
    CLOTHES = 4
    ACCESSORIES = 5
    EQUIPMENT = 6
