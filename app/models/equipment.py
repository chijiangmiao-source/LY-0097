from peewee import CharField, ForeignKeyField, TextField
from .base import BaseModel
from .equipment_room import EquipmentRoom
from .equipment_category import EquipmentCategory


class Equipment(BaseModel):
    equipment_no = CharField(max_length=50, unique=True)
    name = CharField(max_length=100)
    category = ForeignKeyField(EquipmentCategory, backref='equipment')
    room = ForeignKeyField(EquipmentRoom, backref='equipment')
    condition = CharField(max_length=20, default='good')
    status = CharField(max_length=20, default='available')
    specification = CharField(max_length=200, null=True)
    brand = CharField(max_length=50, null=True)
    remark = TextField(null=True)

    class Meta:
        table_name = 'equipment'
