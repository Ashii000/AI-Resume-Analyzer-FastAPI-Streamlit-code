"""Minimal OAuth helpers for third-party providers.

This module provides helpers to build authorization URLs and exchange codes
for access tokens. It supports Google OAuth as an example. In production,
use a robust library (Authlib) and secure client secret storage.
"""
from __future__ import annotations

import logging
from typing import Dict, Optional
from urllib.parse import urlencode

import requests

from app.config import settings

logger = logging.getLogger(__name__)


_PROVIDERS = {
    "google": {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scope": "openid email profile",
    }
}


def build_authorization_url(provider: str, redirect_uri: str, state: Optional[str] = None) -> str:
    """Construct an authorization URL for the given provider.

    Args:
        provider: Provider key (e.g., 'google').
        redirect_uri: Redirect URI registered with the provider.
        state: Optional state value to mitigate CSRF.

    Returns:
        Full authorization URL to redirect the user to.
    """
    p = _PROVIDERS.get(provider)
    if not p:
        raise ValueError("Unsupported provider")
    client_id = getattr(settings, f"{provider.upper()}_CLIENT_ID", None)
    if not client_id:
        raise RuntimeError(f"Client ID for {provider} not configured")

    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": p["scope"],
        "redirect_uri": redirect_uri,
        "access_type": "offline",
        "include_granted_scopes": "true",
    }
    if state:
        params["state"] = state

    return f"{p['auth_url']}?{urlencode(params)}"


def exchange_code_for_token(provider: str, code: str, redirect_uri: str) -> Dict:
    """Exchange authorization code for tokens with the provider.

    Note: This function performs a server-side HTTP request; in production
    handle network errors and timeouts and keep client secrets secure.
    """
    p = _PROVIDERS.get(provider)
    if not p:
        raise ValueError("Unsupported provider")
    client_id = getattr(settings, f"{provider.upper()}_CLIENT_ID", None)
    client_secret = getattr(settings, f"{provider.upper()}_CLIENT_SECRET", None)
    if not client_id or not client_secret:
        raise RuntimeError(f"OAuth client credentials for {provider} not configured")

    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    try:
        resp = requests.post(p["token_url"], data=data, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logger.exception("OAuth token exchange failed: %s", exc)
        raise
