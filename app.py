from fastapi import FastAPI
from pydantic import BaseModel
from validator.api import run_static_from_dir, run_triad_from_dir

app = FastAPI()

class DirPayload(BaseModel):
    dir_path: str

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/v1/postchecks/static/from-dir")
def static_from_dir(payload: DirPayload):
    return run_static_from_dir(payload.dir_path)

@app.post("/v1/jobs/from-dir")
def jobs_from_dir(payload: DirPayload, wait: bool = True):
    # wait is accepted for compatibility; execution is synchronous in local mode
    return run_triad_from_dir(payload.dir_path)
