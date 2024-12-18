# Auto generated from cell_types.yaml by pythongen.py version: 0.0.1
# Generation date: 2024-12-17T17:27:49
# Schema: CellTypeSummarySchema
#
# id: cell_type_summary_schema
# description: A schema for summarizing cell type annotation information from an AnnData table.
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import re
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union
)

from jsonasobj2 import (
    JsonObj,
    as_dict
)
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions
)
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import (
    camelcase,
    sfx,
    underscore
)
from linkml_runtime.utils.metamodelcore import (
    bnode,
    empty_dict,
    empty_list
)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str
)
from rdflib import (
    Namespace,
    URIRef
)

from linkml_runtime.linkml_model.types import Float, Integer, String

metamodel_version = "1.7.0"
version = None

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
EFO = CurieNamespace('EFO', 'http://identifiers.org/efo/')
EXAMPLE = CurieNamespace('example', 'http://www.example.org/rdf#')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = EXAMPLE


# Types

# Class references



@dataclass(repr=False)
class CellTypeAnnotationSummary(YAMLRoot):
    """
    Represents the summarized information extracted from a table.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = EXAMPLE["CellTypeAnnotationSummary"]
    class_class_curie: ClassVar[str] = "example:CellTypeAnnotationSummary"
    class_name: ClassVar[str] = "CellTypeAnnotationSummary"
    class_model_uri: ClassVar[URIRef] = EXAMPLE.CellTypeAnnotationSummary

    cell_type_statistics: Union[Union[dict, "CellTypeStatistics"], List[Union[dict, "CellTypeStatistics"]]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.cell_type_statistics):
            self.MissingRequiredField("cell_type_statistics")
        self._normalize_inlined_as_dict(slot_name="cell_type_statistics", slot_type=CellTypeStatistics, key_name="cell_type_information", keyed=False)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class CellTypeStatistics(YAMLRoot):
    """
    Summary statistics for a specific cell type.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = EXAMPLE["CellTypeStatistics"]
    class_class_curie: ClassVar[str] = "example:CellTypeStatistics"
    class_name: ClassVar[str] = "CellTypeStatistics"
    class_model_uri: ClassVar[URIRef] = EXAMPLE.CellTypeStatistics

    cell_type_information: Union[dict, "CellType"] = None
    total_cells: int = None
    relative_abundance: Optional[float] = None
    marker_statistics: Optional[Union[Union[dict, "MarkerStatistics"], List[Union[dict, "MarkerStatistics"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.cell_type_information):
            self.MissingRequiredField("cell_type_information")
        if not isinstance(self.cell_type_information, CellType):
            self.cell_type_information = CellType(**as_dict(self.cell_type_information))

        if self._is_empty(self.total_cells):
            self.MissingRequiredField("total_cells")
        if not isinstance(self.total_cells, int):
            self.total_cells = int(self.total_cells)

        if self.relative_abundance is not None and not isinstance(self.relative_abundance, float):
            self.relative_abundance = float(self.relative_abundance)

        if not isinstance(self.marker_statistics, list):
            self.marker_statistics = [self.marker_statistics] if self.marker_statistics is not None else []
        self.marker_statistics = [v if isinstance(v, MarkerStatistics) else MarkerStatistics(**as_dict(v)) for v in self.marker_statistics]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class CellType(YAMLRoot):
    """
    A cell type is a distinct morphological or functional form of cell. Examples are epithelial, glial etc.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = EFO["0000324"]
    class_class_curie: ClassVar[str] = "EFO:0000324"
    class_name: ClassVar[str] = "CellType"
    class_model_uri: ClassVar[URIRef] = EXAMPLE.CellType

    cell_type_name: Optional[str] = None
    marker_set: Optional[Union[str, List[str]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.cell_type_name is not None and not isinstance(self.cell_type_name, str):
            self.cell_type_name = str(self.cell_type_name)

        if not isinstance(self.marker_set, list):
            self.marker_set = [self.marker_set] if self.marker_set is not None else []
        self.marker_set = [v if isinstance(v, str) else str(v) for v in self.marker_set]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class MarkerStatistics(YAMLRoot):
    """
    Represents marker-based statistics for a cell type.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = EXAMPLE["MarkerStatistics"]
    class_class_curie: ClassVar[str] = "example:MarkerStatistics"
    class_name: ClassVar[str] = "MarkerStatistics"
    class_model_uri: ClassVar[URIRef] = EXAMPLE.MarkerStatistics

    marker_name: Optional[str] = None
    inclusive_mean_expression: Optional[float] = None
    inclusive_expression_range: Optional[Union[dict, "ExpressionRange"]] = None
    exclusive_mean_expression: Optional[float] = None
    exclusive_expression_range: Optional[Union[dict, "ExpressionRange"]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.marker_name is not None and not isinstance(self.marker_name, str):
            self.marker_name = str(self.marker_name)

        if self.inclusive_mean_expression is not None and not isinstance(self.inclusive_mean_expression, float):
            self.inclusive_mean_expression = float(self.inclusive_mean_expression)

        if self.inclusive_expression_range is not None and not isinstance(self.inclusive_expression_range, ExpressionRange):
            self.inclusive_expression_range = ExpressionRange(**as_dict(self.inclusive_expression_range))

        if self.exclusive_mean_expression is not None and not isinstance(self.exclusive_mean_expression, float):
            self.exclusive_mean_expression = float(self.exclusive_mean_expression)

        if self.exclusive_expression_range is not None and not isinstance(self.exclusive_expression_range, ExpressionRange):
            self.exclusive_expression_range = ExpressionRange(**as_dict(self.exclusive_expression_range))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ExpressionRange(YAMLRoot):
    """
    Represents the range of expression values for a marker.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = EXAMPLE["ExpressionRange"]
    class_class_curie: ClassVar[str] = "example:ExpressionRange"
    class_name: ClassVar[str] = "ExpressionRange"
    class_model_uri: ClassVar[URIRef] = EXAMPLE.ExpressionRange

    min_expression: Optional[float] = None
    max_expression: Optional[float] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.min_expression is not None and not isinstance(self.min_expression, float):
            self.min_expression = float(self.min_expression)

        if self.max_expression is not None and not isinstance(self.max_expression, float):
            self.max_expression = float(self.max_expression)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.cellTypeAnnotationSummary__cell_type_statistics = Slot(uri=EXAMPLE.cell_type_statistics, name="cellTypeAnnotationSummary__cell_type_statistics", curie=EXAMPLE.curie('cell_type_statistics'),
                   model_uri=EXAMPLE.cellTypeAnnotationSummary__cell_type_statistics, domain=None, range=Union[Union[dict, CellTypeStatistics], List[Union[dict, CellTypeStatistics]]])

slots.cellTypeStatistics__cell_type_information = Slot(uri=EXAMPLE.cell_type_information, name="cellTypeStatistics__cell_type_information", curie=EXAMPLE.curie('cell_type_information'),
                   model_uri=EXAMPLE.cellTypeStatistics__cell_type_information, domain=None, range=Union[dict, CellType])

slots.cellTypeStatistics__total_cells = Slot(uri=EXAMPLE.total_cells, name="cellTypeStatistics__total_cells", curie=EXAMPLE.curie('total_cells'),
                   model_uri=EXAMPLE.cellTypeStatistics__total_cells, domain=None, range=int)

slots.cellTypeStatistics__relative_abundance = Slot(uri=EXAMPLE.relative_abundance, name="cellTypeStatistics__relative_abundance", curie=EXAMPLE.curie('relative_abundance'),
                   model_uri=EXAMPLE.cellTypeStatistics__relative_abundance, domain=None, range=Optional[float])

slots.cellTypeStatistics__marker_statistics = Slot(uri=EXAMPLE.marker_statistics, name="cellTypeStatistics__marker_statistics", curie=EXAMPLE.curie('marker_statistics'),
                   model_uri=EXAMPLE.cellTypeStatistics__marker_statistics, domain=None, range=Optional[Union[Union[dict, MarkerStatistics], List[Union[dict, MarkerStatistics]]]])

slots.cellType__cell_type_name = Slot(uri=EXAMPLE.cell_type_name, name="cellType__cell_type_name", curie=EXAMPLE.curie('cell_type_name'),
                   model_uri=EXAMPLE.cellType__cell_type_name, domain=None, range=Optional[str])

slots.cellType__marker_set = Slot(uri=EXAMPLE.marker_set, name="cellType__marker_set", curie=EXAMPLE.curie('marker_set'),
                   model_uri=EXAMPLE.cellType__marker_set, domain=None, range=Optional[Union[str, List[str]]])

slots.markerStatistics__marker_name = Slot(uri=EXAMPLE.marker_name, name="markerStatistics__marker_name", curie=EXAMPLE.curie('marker_name'),
                   model_uri=EXAMPLE.markerStatistics__marker_name, domain=None, range=Optional[str])

slots.markerStatistics__inclusive_mean_expression = Slot(uri=EXAMPLE.inclusive_mean_expression, name="markerStatistics__inclusive_mean_expression", curie=EXAMPLE.curie('inclusive_mean_expression'),
                   model_uri=EXAMPLE.markerStatistics__inclusive_mean_expression, domain=None, range=Optional[float])

slots.markerStatistics__inclusive_expression_range = Slot(uri=EXAMPLE.inclusive_expression_range, name="markerStatistics__inclusive_expression_range", curie=EXAMPLE.curie('inclusive_expression_range'),
                   model_uri=EXAMPLE.markerStatistics__inclusive_expression_range, domain=None, range=Optional[Union[dict, ExpressionRange]])

slots.markerStatistics__exclusive_mean_expression = Slot(uri=EXAMPLE.exclusive_mean_expression, name="markerStatistics__exclusive_mean_expression", curie=EXAMPLE.curie('exclusive_mean_expression'),
                   model_uri=EXAMPLE.markerStatistics__exclusive_mean_expression, domain=None, range=Optional[float])

slots.markerStatistics__exclusive_expression_range = Slot(uri=EXAMPLE.exclusive_expression_range, name="markerStatistics__exclusive_expression_range", curie=EXAMPLE.curie('exclusive_expression_range'),
                   model_uri=EXAMPLE.markerStatistics__exclusive_expression_range, domain=None, range=Optional[Union[dict, ExpressionRange]])

slots.expressionRange__min_expression = Slot(uri=EXAMPLE.min_expression, name="expressionRange__min_expression", curie=EXAMPLE.curie('min_expression'),
                   model_uri=EXAMPLE.expressionRange__min_expression, domain=None, range=Optional[float])

slots.expressionRange__max_expression = Slot(uri=EXAMPLE.max_expression, name="expressionRange__max_expression", curie=EXAMPLE.curie('max_expression'),
                   model_uri=EXAMPLE.expressionRange__max_expression, domain=None, range=Optional[float])
