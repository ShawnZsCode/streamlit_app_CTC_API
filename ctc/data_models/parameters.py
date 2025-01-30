"""Revit Parameters data models"""

from pydantic import Field, computed_field
from typing import List
from ctc.data_models.common import LocalBaseModel


# Class Definitions
class Parameter(LocalBaseModel):
    """Revit Parameter model"""

    Id: int = Field(alias="id")
    Name: str = Field(alias="name")
    HasValue: bool = Field(alias="hasValue", exclude=True)
    IsShared: bool = Field(alias="isShared", exclude=True)
    IsReadOnly: bool = Field(alias="isReadOnly", exclude=True)
    StorageType: str = Field(alias="storageType", exclude=True)
    ValueAsString: str = Field(alias="valueAsString")
    ValueAsElementId: int = Field(alias="valueAsElementId", exclude=True)
    ValueAsInteger: int = Field(alias="valueAsInt", exclude=True)
    ValueAsDouble: float = Field(alias="valueAsDouble", exclude=True)


class Parameters(LocalBaseModel):
    """Revit Parameters model"""

    Parameters: List[Parameter] = []

    @computed_field
    @property
    def Count(self) -> int:
        return len(self.Parameters)
