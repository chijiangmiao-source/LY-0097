from peewee import CharField, TextField
from .base import BaseModel


class EquipmentRoom(BaseModel):
    name = CharField(max_length=100, unique=True)
    location = CharField(max_length=200, null=True)
    manager = CharField(max_length=50, null=True)
    description = TextField(null=True)

    class Meta:
        table_name = 'equipment_rooms'
