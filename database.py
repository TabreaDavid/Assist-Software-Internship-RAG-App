from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from models import Base

load_dotenv()

class Database():
    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.engine = create_engine(self.DATABASE_URL)
        self.db_session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_db(self):
        db = self.db_session()
        try:
            yield db
        finally:
            db.close()
    
    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)