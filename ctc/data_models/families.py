"""Revit Famlies data models"""

from pydantic import Field, computed_field
from typing import List, Optional
from ctc.data_models.common import LocalBaseModel
from ctc.data_models.parameters import Parameter
from ctc.data_models.family_types import RevitFamilyType


# Class Definitions
class RevitFamily(LocalBaseModel):
    """Revit Family model"""

    Id: Optional[int] = Field(default=-1, alias="id")
    Name: str = Field(alias="name")
    Types: Optional[List[RevitFamilyType]] = Field(default=[], alias="types")
    Parameters: Optional[List[Parameter]] = Field(default=[], alias="parameters")

    @computed_field
    @property
    def TypeCount(self) -> int:
        return len(self.Types)

    @computed_field
    @property
    def ParameterCount(self) -> int:
        return len(self.Parameters)

    @computed_field
    @property
    def InstanceCount(self) -> int:
        return sum([t.InstanceCount for t in self.Types])

    # Check to see if the type exists in the family types list
    def has_type(self, type: RevitFamilyType) -> bool:
        for type_self in self.Types:
            if (type_self.Id == type.Id) and (type_self.Name == type.Name):
                return True
        return False

    # Get the index of the type in the family types list
    def get_type_index(self, type: RevitFamilyType) -> int:
        for i, type_self in enumerate(self.Types):
            if (type_self.Id == type.Id) and (type_self.Name == type.Name):
                return i
        return -1


# Prevent running from this file
if __name__ == "__main__":
    pass
