#create database connection
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

#create mariadb engine with secret configuration
def engine():
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD","")
    DB_HOST = os.getenv("DB_HOST")

    sqlengine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4")
    #below is the uri to create SQL database engine
    #engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

    return sqlengine
