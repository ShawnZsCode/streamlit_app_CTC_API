"""Revit Elements sata models"""

from pydantic import Field
from typing import List, Optional


from ctc.data_models.common import LocalBaseModel
from ctc.data_models.parameters import Parameter


# Class Definitions
class RevitElement(LocalBaseModel):
    Id: int = Field(alias="id")
    Name: str = Field(alias="name")
    Parameters: Optional[List[Parameter]] = Field(default=[], alias="parameters")


# Prevent running from this file
if __name__ == "__main__":
    pass
