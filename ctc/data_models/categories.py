"""Revit Categories data model"""

from pydantic import BaseModel, Field, computed_field, AliasChoices
from typing import List, Optional

from ctc.data_models.common import LocalBaseModel
from ctc.data_models.families import RevitFamily
# Class Definitions


class RevitCategory(BaseModel):
    """Revit session model"""

    Id: str = Field(alias="ID")
    Name: str = Field(alias="DisplayName")
    IsFamilyInstanceCreatable: bool = Field(exclude=True)
    IsAnnotation: bool = Field(exclude=True)
    IsFamilyFileCreatable: bool = Field(exclude=True)
    IsVirtual: bool = Field(exclude=True)
    Families: Optional[List[RevitFamily]] = Field(default=[])

    @computed_field
    @property
    def FamilyCount(self) -> int:
        return len(self.Families)


class RevitCategories(LocalBaseModel):
    """Revit sessions model"""

    # Count_: int = Field(default=0, repr=False)
    Categories: List[RevitCategory] = []

    @computed_field
    @property
    def Count(self) -> int:
        return len(self.Categories)


# Prevent running from this file
if __name__ == "__main__":
    pass
