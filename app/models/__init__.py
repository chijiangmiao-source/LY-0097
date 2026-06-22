from .base import BaseModel
from .user import User
from .grade_class import GradeClass
from .equipment_room import EquipmentRoom
from .equipment_category import EquipmentCategory
from .equipment import Equipment
from .borrow_order import BorrowOrder
from .borrow_item import BorrowItem
from .inspection_record import InspectionRecord
from .liability_judgment import LiabilityJudgment

__all__ = [
    'BaseModel',
    'User',
    'GradeClass',
    'EquipmentRoom',
    'EquipmentCategory',
    'Equipment',
    'BorrowOrder',
    'BorrowItem',
    'InspectionRecord',
    'LiabilityJudgment',
]

ALL_MODELS = [
    User,
    GradeClass,
    EquipmentRoom,
    EquipmentCategory,
    Equipment,
    BorrowOrder,
    BorrowItem,
    InspectionRecord,
    LiabilityJudgment,
]
