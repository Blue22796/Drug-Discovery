from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base

engine = create_engine('sqlite:///reinvent.db', echo=True)
SessionLocal = sessionmaker(bind=engine)

# Create all tables
from models import prior, agent, stage, molecule, scoring_plugin
Base.metadata.create_all(bind=engine)

print("Database and tables created.")

#Test
from models.prior import Prior

# Create a session
session = SessionLocal()

# Query all priors
priors = session.query(Prior).all()

# Print them

print(priors)
for p in priors:
    print(p.name)