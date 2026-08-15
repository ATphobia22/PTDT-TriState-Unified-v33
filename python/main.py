"""PTDT-TriState FastAPI entry — mounts XSoft proxy and health."""
from __future__ import annotations

import sys
from pathlib import Path

# Allow backend.proxies imports when run from repo root
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.proxies.xsoft_engage_proxy import mount_xsoft_proxy

app = FastAPI(
    title="PTDT-TriState-Unified-v33 API",
    version="33.0.0",
    description="Presentation proxies only; HEC-RAS remains authoritative for hydro.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

mount_xsoft_proxy(app)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ptdt-tristate-api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("python.main:app", host="0.0.0.0", port=8000, reload=True)
