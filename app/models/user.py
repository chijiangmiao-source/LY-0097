import bcrypt
from peewee import CharField, BooleanField
from .base import BaseModel


class User(BaseModel):
    username = CharField(max_length=50, unique=True)
    password_hash = CharField(max_length=255)
    full_name = CharField(max_length=100)
    role = CharField(max_length=20, default='staff')
    is_active = BooleanField(default=True)

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    class Meta:
        table_name = 'users'
