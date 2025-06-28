from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Molecule(Base):
    __tablename__ = 'molecules'

    id = Column(Integer, primary_key=True)
    smiles = Column(String, nullable=False)
    stage_id = Column(Integer, ForeignKey('stages.id'), nullable=True)
    score = Column(Float, nullable=True)

    stage = relationship("Stage", back_populates="molecules")