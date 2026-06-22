import os
from dotenv import load_dotenv
from peewee import PostgresqlDatabase

load_dotenv()

db = PostgresqlDatabase(
    os.getenv('DB_NAME', 'sports_equipment'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'postgres'),
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', '5432'))
)
