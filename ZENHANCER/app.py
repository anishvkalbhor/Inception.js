from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from query_enhancer import enhance_query

app = FastAPI(title="Query Enhancer (Rewrite + HyDE)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class Query(BaseModel):
    query: str

@app.post("/enhance")
def enhance(body: Query):
    try:
        return enhance_query(body.query)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")

# Serve the UI
app.mount("/", StaticFiles(directory="static", html=True), name="static")
