import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import db
from app.models import ALL_MODELS, User


def init_database():
    print("Connecting to database...")
    db.connect()

    print("Creating tables...")
    db.create_tables(ALL_MODELS, safe=True)

    print("Creating default admin user...")
    if not User.select().where(User.username == 'admin').exists():
        admin = User(
            username='admin',
            full_name='系统管理员',
            role='admin'
        )
        admin.set_password('admin123')
        admin.save()
        print("Default admin created: username=admin, password=admin123")
    else:
        print("Admin user already exists")

    db.close()
    print("Database initialization completed!")


if __name__ == '__main__':
    init_database()
