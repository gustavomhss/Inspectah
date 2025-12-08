#!/usr/bin/env python3
"""
Gera JWT RS256 para uso nos gates SF3.

Usage:
  API_AUD=inspectah-api ACTOR=admin-user ROLE=admin python bin/sf3_jwt_gen.py
"""
import os
import uuid
import time
import json
import sys
import jwt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_KEY_PATH = ROOT / "config" / "dev_jwt_private.pem"

issuer = os.environ.get("ISS", "inspectah-idp")
aud = os.environ.get("AUD", "inspectah-api")
actor = os.environ.get("ACTOR", "admin-user")
role = os.environ.get("ROLE", "admin")
op_id = os.environ.get("OP_ID") or str(uuid.uuid4())
request_id = os.environ.get("REQUEST_ID") or str(uuid.uuid4())
ttl_seconds = int(os.environ.get("TTL_SECONDS", "900"))

now = int(time.time())
payload = {
    "iss": issuer,
    "aud": aud,
    "iat": now,
    "nbf": now,
    "exp": now + ttl_seconds,
    "sub": actor,
    "role": role,
    "op_id": op_id,
    "request_id": request_id,
}

key = PRIVATE_KEY_PATH.read_text()
token = jwt.encode(payload, key, algorithm="RS256", headers={"kid": "sf3-dev"})
print(token)
