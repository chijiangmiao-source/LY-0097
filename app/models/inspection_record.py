from datetime import datetime
from peewee import ForeignKeyField, CharField, TextField, DateTimeField, BooleanField
from .base import BaseModel
from .borrow_order import BorrowOrder
from .borrow_item import BorrowItem
from .equipment import Equipment
from .user import User


class InspectionRecord(BaseModel):
    borrow_order = ForeignKeyField(BorrowOrder, backref='inspections')
    borrow_item = ForeignKeyField(BorrowItem, backref='inspections', null=True)
    equipment = ForeignKeyField(Equipment, backref='inspections')
    inspection_time = DateTimeField(default=datetime.now)
    inspector = ForeignKeyField(User, backref='inspections')
    problem_type = CharField(max_length=20)
    problem_description = TextField(null=True)
    handling_path = CharField(max_length=20, null=True)
    is_deletable = BooleanField(default=True)
    status = CharField(max_length=20, default='pending')
    remark = TextField(null=True)

    class Meta:
        table_name = 'inspection_records'
