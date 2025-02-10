"""Revit Categories data model"""

from pydantic import BaseModel, Field, computed_field, AliasChoices
from typing import List, Optional

from ctc.data_models.common import LocalBaseModel
from ctc.data_models.families import RevitFamily
from ctc.data_models.family_types import RevitFamilyType
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

    # Check to see if the family exists in the category's families list
    def has_family(self, family: RevitFamily) -> bool:
        for family_self in self.Families:
            if (family_self.Id == family.Id) and (family_self.Name == family.Name):
                return True
        return False

    # Get the index of the family in the category's families list
    def get_family_index(self, family: RevitFamily) -> int:
        for i, family_self in enumerate(self.Families):
            if (family_self.Id == family.Id) and (family_self.Name == family.Name):
                return i
        return -1

    # Deep check for family type in the category's families list
    def has_type(self, type: RevitFamilyType) -> bool:
        for family in self.Families:
            if family.has_type(type):
                return True
        return False

    # Get the index for both family and type in the category's families list
    def get_fam_type_index(self, type: RevitFamilyType) -> (int, int):
        for i, family in enumerate(self.Families):
            if family.has_type(type):
                return i, family.get_type_index(type)
        return -1, -1


class RevitCategories(LocalBaseModel):
    """Revit sessions model"""

    # Count_: int = Field(default=0, repr=False)
    Categories: List[RevitCategory] = []

    @computed_field
    @property
    def Count(self) -> int:
        return len(self.Categories)

    # Check to see if the category exists in the categories list
    def has_category(self, category: RevitCategory) -> bool:
        for category_self in self.Categories:
            if (category_self.Id == category.Id) and (
                category_self.Name == category.Name
            ):
                return True
        return False

    # Get the index of the category in the categories list
    def get_category_index(self, category: RevitCategory) -> int:
        for i, category_self in enumerate(self.Categories):
            if (category_self.Id == category.Id) and (
                category_self.Name == category.Name
            ):
                return i
        return -1


# Prevent running from this file
if __name__ == "__main__":
    pass
