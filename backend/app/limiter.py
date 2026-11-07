"""
limiter.py

Shared Limiter instance from the slowapi library, used both in main.py
(for registering the exception handler) and auth/routes.py
(for applying rate limits to the login endpoint).
"""

from slowapi import Limiter
from slowapi.util import get_remote_address


limiter = Limiter(key_func=get_remote_address)