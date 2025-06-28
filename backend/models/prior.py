from sqlalchemy import Column, Integer, String, Boolean
from models.base import Base

class Prior(Base):
    __tablename__ = 'priors'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    takes_file = Column(Boolean, default=True)
    prior_path = Column(String, nullable=True)