from datetime import datetime
from peewee import CharField, ForeignKeyField, DateTimeField, TextField
from .base import BaseModel
from .grade_class import GradeClass
from .user import User


class BorrowOrder(BaseModel):
    order_no = CharField(max_length=30, unique=True)
    grade_class = ForeignKeyField(GradeClass, backref='borrow_orders')
    teacher = CharField(max_length=50)
    borrow_time = DateTimeField(default=datetime.now)
    return_time = DateTimeField(null=True)
    return_status = CharField(max_length=20, default='pending')
    liability_status = CharField(max_length=20, default='pending')
    purpose = CharField(max_length=200, null=True)
    operator = ForeignKeyField(User, backref='borrow_orders')
    remark = TextField(null=True)

    class Meta:
        table_name = 'borrow_orders'
