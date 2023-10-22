from sqlalchemy.orm import Session  
from ..Database.connect import engine

session = Session(bind=engine)