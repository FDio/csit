#!/usr/bin/env python3
"""
FastAPI Server for CSIT Data.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dashboard import mcp_app, settings

# Assemble the application
app = FastAPI(title="CSIT FastAPI server", lifespan=mcp_app.lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_allow_origins),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=[
        "mcp-protocol-version",
        "mcp-session-id",
        "Authorization",
        "Content-Type",
    ],
    expose_headers=["mcp-session-id"],
)

app.mount("", app=mcp_app)

__all__ = ["app"]
