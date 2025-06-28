from pathlib import Path
from backend.database.database import SessionLocal
from backend.models.prior import Prior
from backend.models.agent import Agent

# 1) Point this to an actual .prior file on disk:
MODEL_FILE = Path.home() / "Projects" / "Drug-Discovery" / "REINVENT4" / "priors" / "reinvent.prior"
print(MODEL_FILE)

def main():
    db = SessionLocal()
    try:
        # Create a Prior record
        prior = Prior(
            name="TestPrior",
            prior_path=str(MODEL_FILE)       # ← use prior_path, not path
        )
        db.add(prior)
        db.commit()
        db.refresh(prior)

        # Create an Agent that wraps that Prior
        agent = Agent(
            name="TestAgent",
            prior_id=prior.id,
            agent_path=str(MODEL_FILE),
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)

        print(f"Seeded Prior(id={prior.id}) and Agent(id={agent.id})")
    finally:
        db.close()

if __name__ == "__main__":
    main()
