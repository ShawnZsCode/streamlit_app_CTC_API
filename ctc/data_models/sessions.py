"""Revit sessions data models"""

from typing import List, Optional
from pydantic import computed_field

from ctc.data_models.common import LocalBaseModel

# Class Definitions


class RevitSession(LocalBaseModel):
    """Revit session model"""

    RevitVersion: str
    Port: int
    ActiveProject: Optional[str] = ""


class RevitSessions(LocalBaseModel):
    """Revit sessions model"""

    # Count: int = 0
    Sessions: List[RevitSession] = []

    @computed_field
    @property
    def Count(self) -> int:
        return len(self.Categories)


# Prevent running from this file
if __name__ == "__main__":
    pass
