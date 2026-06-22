from datetime import datetime
from peewee import ForeignKeyField, CharField, TextField, DateTimeField, BooleanField
from .base import BaseModel
from .inspection_record import InspectionRecord
from .grade_class import GradeClass
from .user import User


class LiabilityJudgment(BaseModel):
    inspection_record = ForeignKeyField(InspectionRecord, backref='liability_judgments', unique=True)
    grade_class = ForeignKeyField(GradeClass, backref='liability_judgments')
    judgment_time = DateTimeField(default=datetime.now)
    judge = ForeignKeyField(User, backref='liability_judgments')
    liability_type = CharField(max_length=20)
    liable_person = CharField(max_length=100)
    judgment_result = TextField()
    is_confirmed = BooleanField(default=False)
    confirmed_time = DateTimeField(null=True)
    confirmer = ForeignKeyField(User, backref='confirmed_judgments', null=True)
    remark = TextField(null=True)

    class Meta:
        table_name = 'liability_judgments'
