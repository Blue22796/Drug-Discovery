from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.models.base import Base

class Stage(Base):
    __tablename__ = 'stages'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    scoring_type = Column(String, default='geometric_mean')
    batch_size = Column(Integer, default=64)

    agent = relationship("Agent", back_populates="stages")
    molecules = relationship("Molecule", back_populates="stage")
    scoring_plugins = relationship("ScoringPlugin", back_populates="stage")

# Backref for Agent
from backend.models.agent import Agent
Agent.stages = relationship("Stage", order_by=Stage.id, back_populates="agent")
