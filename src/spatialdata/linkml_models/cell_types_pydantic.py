from __future__ import annotations 

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal 
from enum import Enum 
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator
)


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass




class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'example',
     'default_range': 'string',
     'description': 'A schema for summarizing cell type annotation information '
                    'from an AnnData table.',
     'id': 'cell_type_summary_schema',
     'imports': ['linkml:types'],
     'name': 'CellTypeSummarySchema',
     'prefixes': {'EFO': {'prefix_prefix': 'EFO',
                          'prefix_reference': 'http://identifiers.org/efo/'},
                  'example': {'prefix_prefix': 'example',
                              'prefix_reference': 'http://www.example.org/rdf#'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'linkml_specs/cell_types.yaml'} )


class CellTypeAnnotationSummary(ConfiguredBaseModel):
    """
    Represents the summarized information extracted from a table.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cell_type_summary_schema'})

    cell_type_statistics: List[CellTypeStatistics] = Field(..., description="""Summary statistics for each cell type.""", json_schema_extra = { "linkml_meta": {'alias': 'cell_type_statistics', 'domain_of': ['CellTypeAnnotationSummary']} })


class CellTypeStatistics(ConfiguredBaseModel):
    """
    Summary statistics for a specific cell type.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cell_type_summary_schema'})

    cell_type_information: CellType = Field(..., description="""Cell type name and markers used to identify the cell type""", json_schema_extra = { "linkml_meta": {'alias': 'cell_type_information', 'domain_of': ['CellTypeStatistics']} })
    total_cells: int = Field(..., description="""Total number of cells annotated with this cell type.""", json_schema_extra = { "linkml_meta": {'alias': 'total_cells', 'domain_of': ['CellTypeStatistics']} })
    relative_abundance: Optional[float] = Field(None, description="""Proportion of cells with this type relative to the total cell count.""", json_schema_extra = { "linkml_meta": {'alias': 'relative_abundance', 'domain_of': ['CellTypeStatistics']} })
    marker_statistics: Optional[List[MarkerStatistics]] = Field(None, description="""Summary of markers used to annotate this cell type.""", json_schema_extra = { "linkml_meta": {'alias': 'marker_statistics', 'domain_of': ['CellTypeStatistics']} })


class CellType(ConfiguredBaseModel):
    """
    A cell type is a distinct morphological or functional form of cell. Examples are epithelial, glial etc.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'EFO:0000324', 'from_schema': 'cell_type_summary_schema'})

    cell_type_name: Optional[str] = Field(None, description="""name of the cell type. Not to be used as identifier as it can be subject to change.""", json_schema_extra = { "linkml_meta": {'alias': 'cell_type_name', 'domain_of': ['CellType']} })
    marker_set: Optional[List[str]] = Field(None, description="""markers used by researcher to indentify cell types""", json_schema_extra = { "linkml_meta": {'alias': 'marker_set', 'domain_of': ['CellType']} })


class MarkerStatistics(ConfiguredBaseModel):
    """
    Represents marker-based statistics for a cell type.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cell_type_summary_schema'})

    marker_name: Optional[str] = Field(None, description="""Name of the marker.""", json_schema_extra = { "linkml_meta": {'alias': 'marker_name', 'domain_of': ['MarkerStatistics']} })
    inclusive_mean_expression: Optional[float] = Field(None, description="""Mean expression of the marker across all cells of type cell_type.""", json_schema_extra = { "linkml_meta": {'alias': 'inclusive_mean_expression', 'domain_of': ['MarkerStatistics']} })
    inclusive_expression_range: Optional[ExpressionRange] = Field(None, description="""Minimum and maximum expression of the marker across all cells of type cell_type.""", json_schema_extra = { "linkml_meta": {'alias': 'inclusive_expression_range', 'domain_of': ['MarkerStatistics']} })
    exclusive_mean_expression: Optional[float] = Field(None, description="""Mean expression of the marker across all cells not of type marker_name.""", json_schema_extra = { "linkml_meta": {'alias': 'exclusive_mean_expression', 'domain_of': ['MarkerStatistics']} })
    exclusive_expression_range: Optional[ExpressionRange] = Field(None, description="""Minimum and maximum expression of the marker across all cells not of type marker_name""", json_schema_extra = { "linkml_meta": {'alias': 'exclusive_expression_range', 'domain_of': ['MarkerStatistics']} })


class ExpressionRange(ConfiguredBaseModel):
    """
    Represents the range of expression values for a marker.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'cell_type_summary_schema'})

    min_expression: Optional[float] = Field(None, description="""Minimum expression value of the marker.""", json_schema_extra = { "linkml_meta": {'alias': 'min_expression', 'domain_of': ['ExpressionRange']} })
    max_expression: Optional[float] = Field(None, description="""Maximum expression value of the marker.""", json_schema_extra = { "linkml_meta": {'alias': 'max_expression', 'domain_of': ['ExpressionRange']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
CellTypeAnnotationSummary.model_rebuild()
CellTypeStatistics.model_rebuild()
CellType.model_rebuild()
MarkerStatistics.model_rebuild()
ExpressionRange.model_rebuild()

