from peewee import CharField, TextField
from .base import BaseModel


class EquipmentCategory(BaseModel):
    name = CharField(max_length=50, unique=True)
    code = CharField(max_length=20, unique=True)
    description = TextField(null=True)

    class Meta:
        table_name = 'equipment_categories'
