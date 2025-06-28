from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.models.base import Base

class Agent(Base):
    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    prior_id = Column(Integer, ForeignKey('priors.id'), nullable=False)
    takes_file = Column(Boolean, default=True)
    epochs = Column(Integer, default=0)
    agent_path = Column(String, nullable=True)

    prior = relationship("Prior", back_populates="agents")

# Backref for Prior
from backend.models.prior import Prior
Prior.agents = relationship("Agent", order_by=Agent.id, back_populates="prior")