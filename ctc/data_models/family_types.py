"""Revit Family Types data models"""

from pydantic import Field, computed_field
from typing import Optional, List
from ctc.data_models.common import LocalBaseModel
from ctc.data_models.parameters import Parameter
from ctc.data_models.elements import RevitElement


# Class Definitions
class RevitFamilyType(LocalBaseModel):
    """Revit Family Type model"""

    Id: Optional[int] = Field(default=-1, alias="id")
    Name: str = Field(alias="name")
    Instances: Optional[List[RevitElement]] = Field(
        default=[],
    )
    Parameters: Optional[List[Parameter]] = Field(default=[], alias="parameters")

    @computed_field
    @property
    def ParameterCount(self) -> int:
        return len(self.Parameters)

    @computed_field
    @property
    def InstanceCount(self) -> int:
        return len(self.Instances)

    # Check to see if the element exists in the family types list
    def has_instance(self, element: RevitElement) -> bool:
        for element_self in self.Instances:
            if (element_self.Id == element.Id) and (element_self.Name == element.Name):
                return True
        return False

    # Get the index of the element in the family types list
    def get_instance_index(self, element: RevitElement) -> int:
        for i, element_self in enumerate(self.Instances):
            if (element_self.Id == element.Id) and (element_self.Name == element.Name):
                return i
        return -1


# Prevent running from this file
if __name__ == "__main__":
    pass
