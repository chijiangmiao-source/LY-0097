from peewee import CharField, IntegerField
from .base import BaseModel


class GradeClass(BaseModel):
    grade = CharField(max_length=20)
    class_name = CharField(max_length=50)
    class_number = IntegerField()
    head_teacher = CharField(max_length=50, null=True)

    @property
    def full_name(self):
        return f"{self.grade}{self.class_name}"

    class Meta:
        table_name = 'grade_classes'
        indexes = (
            (('grade', 'class_name', 'class_number'), True),
        )
