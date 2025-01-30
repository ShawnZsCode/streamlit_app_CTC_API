"""Common data Local Base Model for the CTC API."""

from pydantic import BaseModel

# from ctc.api_categories import


# Class Definitions
class LocalBaseModel(BaseModel):
    """Local Base model defines a function for easy updating of fields"""

    def update(self, **kwargs):
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
