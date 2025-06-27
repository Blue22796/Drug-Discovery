import uvicorn
from fastapi import FastAPI
from Backend.Controllers.priors_controller import router as priors_router
from Backend.Controllers.runs_controller import router as runs_router
from Backend.Controllers.scorers_controller import router as scorers_router

app = FastAPI(
    title="Drug Discovery API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(priors_router)
app.include_router(runs_router)
app.include_router(scorers_router)
app.include_router(run_ops_router)

@app.get("/")
def read_root():
    return {"message": "Welcome"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
