from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class ScoringPlugin(Base):
    __tablename__ = 'scoring_plugins'

    id = Column(Integer, primary_key=True)
    component_name = Column(String, nullable=False)
    weight = Column(Float, default=1.0)
    stage_id = Column(Integer, ForeignKey('stages.id'), nullable=False)

    stage = relationship("Stage", back_populates="scoring_plugins")
