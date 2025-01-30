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
