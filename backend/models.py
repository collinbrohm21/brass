"""Module to contain models for data objects."""

from dataclasses import dataclass

@dataclass
class User:
    """Model containing user data."""
    first_name: str
    last_name: str
    email: str
    password: str # TODO: Change auth structure later. 



