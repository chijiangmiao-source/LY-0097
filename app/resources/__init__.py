from .base import BaseResource
from .auth import LoginResource, LogoutResource
from .home import HomeResource
from .grade_class import GradeClassResource, GradeClassDetailResource
from .equipment_room import EquipmentRoomResource, EquipmentRoomDetailResource
from .equipment_category import EquipmentCategoryResource, EquipmentCategoryDetailResource
from .equipment import EquipmentResource, EquipmentDetailResource
from .borrow_order import (
    BorrowOrderResource,
    BorrowOrderDetailResource,
    BorrowOrderReturnResource,
    BorrowOrderCloseResource,
    BorrowOrderAddItemResource,
    BorrowOrderRemoveItemResource
)
from .inspection import (
    InspectionResource,
    InspectionDetailResource,
    InspectionCloseResource,
    InspectionEquipmentSearchResource
)
from .liability import (
    LiabilityJudgmentResource,
    LiabilityJudgmentDetailResource,
    LiabilityConfirmResource,
    WeeklyReportResource
)

__all__ = [
    'BaseResource',
    'LoginResource',
    'LogoutResource',
    'HomeResource',
    'GradeClassResource',
    'GradeClassDetailResource',
    'EquipmentRoomResource',
    'EquipmentRoomDetailResource',
    'EquipmentCategoryResource',
    'EquipmentCategoryDetailResource',
    'EquipmentResource',
    'EquipmentDetailResource',
    'BorrowOrderResource',
    'BorrowOrderDetailResource',
    'BorrowOrderReturnResource',
    'BorrowOrderCloseResource',
    'BorrowOrderAddItemResource',
    'BorrowOrderRemoveItemResource',
    'InspectionResource',
    'InspectionDetailResource',
    'InspectionCloseResource',
    'InspectionEquipmentSearchResource',
    'LiabilityJudgmentResource',
    'LiabilityJudgmentDetailResource',
    'LiabilityConfirmResource',
    'WeeklyReportResource',
]
