"""Revit Parameters data models"""

from pydantic import Field, computed_field
from typing import List, Optional
from enum import Enum
from ctc.data_models.common import LocalBaseModel


# Class Definitions
class Parameter(LocalBaseModel):
    """Revit Parameter model"""

    Id: int = Field(alias="id")
    Name: str = Field(alias="name")
    HasValue: bool = Field(
        alias="hasValue",
        # exclude=True,
    )
    IsShared: bool = Field(
        alias="isShared",
        # exclude=True,
    )
    IsReadOnly: bool = Field(
        alias="isReadOnly",
        # exclude=True,
    )
    StorageType: str = Field(
        alias="storageType",
        # exclude=True,
    )
    ValueAsString: Optional[str] = Field(
        default=None,
        alias="valueAsString",
    )
    ValueAsElementId: Optional[int] = Field(
        default=None,
        alias="valueAsElementId",
        # exclude=True,
    )
    ValueAsInteger: Optional[int] = Field(
        default=None,
        alias="valueAsInt",
        # exclude=True,
    )
    ValueAsDouble: Optional[float] = Field(
        default=None,
        alias="valueAsDouble",
        # exclude=True,
    )


class StorageLocation(Enum):
    """Revit Parameter storage location"""

    Family: str = "Family"
    Type: str = "Type"
    Instance: str = "Instance"


class ParameterSimple(LocalBaseModel):
    """Revit Parameter model"""

    Id: int
    Name: str
    StoredIn: str
    # StoredIn: StorageLocation


class Parameters(LocalBaseModel):
    """Revit Parameters model"""

    Parameters: List[Parameter] = []

    @computed_field
    @property
    def Count(self) -> int:
        return len(self.Parameters)


# Prevent running from this file
if __name__ == "__main__":
    pass
