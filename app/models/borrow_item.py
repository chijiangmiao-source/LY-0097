from peewee import ForeignKeyField, CharField, TextField
from .base import BaseModel
from .borrow_order import BorrowOrder
from .equipment import Equipment


class BorrowItem(BaseModel):
    borrow_order = ForeignKeyField(BorrowOrder, backref='items')
    equipment = ForeignKeyField(Equipment, backref='borrow_items')
    borrow_condition = CharField(max_length=20, default='good')
    return_condition = CharField(max_length=20, null=True)
    return_status = CharField(max_length=20, default='pending')
    remark = TextField(null=True)

    class Meta:
        table_name = 'borrow_items'
        indexes = (
            (('borrow_order', 'equipment'), True),
        )
