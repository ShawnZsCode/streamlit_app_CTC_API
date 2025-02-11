"""Revit Categories data model"""

from pydantic import BaseModel, Field, computed_field, AliasChoices
from typing import List, Optional

from ctc.data_models.common import LocalBaseModel
from ctc.data_models.families import RevitFamily
from ctc.data_models.family_types import RevitFamilyType
from ctc.data_models.parameters import ParameterSimple, StorageLocation
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

    # Method to return a simple parameter list
    @computed_field
    @property
    def ParameterList(self) -> List[ParameterSimple]:
        parameters = []
        for family in self.Families:
            for parameter in family.Parameters:
                if not self.has_parameter(parameters, parameter):
                    simple_parameter = ParameterSimple(
                        Id=parameter.Id, Name=parameter.Name, StoredIn="Family"
                    )
                    parameters.append(simple_parameter)
            for type in family.Types:
                for parameter in type.Parameters:
                    if not self.has_parameter(parameters, parameter):
                        simple_parameter = ParameterSimple(
                            Id=parameter.Id,
                            Name=parameter.Name,
                            StoredIn="Type",
                        )
                        parameters.append(simple_parameter)
                for element in type.Instances:
                    for parameter in element.Parameters:
                        if not self.has_parameter(parameters, parameter):
                            simple_parameter = ParameterSimple(
                                Id=parameter.Id,
                                Name=parameter.Name,
                                StoredIn="Instance",
                            )
                            parameters.append(simple_parameter)
        return parameters

    # Check to see if the parameter exists in the parameters list
    def has_parameter(
        self,
        param_list: List[ParameterSimple],
        parameter: ParameterSimple,
    ) -> bool:
        for param in param_list:
            if param == parameter:
                return True
        return False

    # Get the parameter by name
    def get_parameter_by_name(self, name: str) -> ParameterSimple:
        for parameter in self.ParameterList:
            if parameter.Name.lower() == name.lower():
                return parameter
        return None

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

    # Get Category by Name
    def get_category_by_name(self, name: str) -> RevitCategory:
        for category in self.Categories:
            if category.Name.lower() == name.lower():
                return category
        return None


# Prevent running from this file
if __name__ == "__main__":
    pass
