from __future__ import annotations

import copy
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

import zarr
from anndata import AnnData
from ome_zarr.io import parse_url

from spatialdata._core.coordinate_system import CoordinateSystem, CoordSystem_t
from spatialdata._core.elements import Image, Labels, Points, Polygons
from spatialdata._core.transform import BaseTransformation, get_transformation_from_dict
from spatialdata._io.write import write_table

# def spatialdata_from_base_elements(
#     images: Optional[Dict[str, Image]] = None,
#     labels: Optional[Dict[str, Labels]] = None,
#     points: Optional[Dict[str, Points]] = None,
#     polygons: Optional[Dict[str, Polygons]] = None,
#     table: Optional[AnnData] = None,
# ) -> SpatialData:
#     # transforms
#     images_transforms = {k: t for k, t in images.items()} if images is not None else None
#     labels_transforms = {k: t for k, t in labels.items()} if labels is not None else None
#     points_transforms = {k: t for k, t in points.items()} if points is not None else None
#     polygons_transforms = {k: t for k, t in polygons.items()} if polygons is not None else None
#     # axes information
#     # TODO:
#
#     return SpatialData(
#         images=images if images is not None else {},
#         labels=labels if labels is not None else {},
#         points=points if points is not None else {},
#         polygons=polygons if polygons is not None else {},
#         table=table,
#         images_transforms=images_transforms,
#         labels_transforms=labels_transforms,
#         points_transforms=points_transforms,
#         polygons_transforms=polygons_transforms,
#     )


class SpatialData:
    """Spatial data structure."""

    images: Mapping[str, Image] = MappingProxyType({})
    labels: Mapping[str, Labels] = MappingProxyType({})
    points: Mapping[str, Points] = MappingProxyType({})
    polygons: Mapping[str, Polygons] = MappingProxyType({})
    _table: Optional[AnnData] = None

    def __init__(
        self,
        # base elements
        images: Mapping[str, Any] = MappingProxyType({}),
        labels: Mapping[str, Any] = MappingProxyType({}),
        points: Mapping[str, Any] = MappingProxyType({}),
        polygons: Mapping[str, Any] = MappingProxyType({}),
        table: Optional[AnnData] = None,
        # # transforms
        # images_transforms: Optional[Mapping[str, Any]] = None,
        # labels_transforms: Optional[Mapping[str, Any]] = None,
        # points_transforms: Optional[Mapping[str, Any]] = None,
        # polygons_transforms: Optional[Mapping[str, Any]] = None,
        # axes information
        images_axes: Optional[Mapping[str, Any]] = None,
        labels_axes: Optional[Mapping[str, Any]] = None,
        # transformations and coordinate systems
        transformations: Mapping[(str, str), Union[BaseTransformation, Dict[Any]]] = MappingProxyType({}),
        coordinate_systems: Optional[List[Union[CoordSystem_t, CoordinateSystem]]] = None,
    ) -> None:
        if coordinate_systems is None:
            raise ValueError("Coordinate systems must be provided.")
        validated_coordinate_systems = _validate_coordinate_systems(coordinate_systems)

        for element_class, elements, prefix in zip(
            [Image, Labels, Points, Polygons],
            [images, labels, points, polygons],
            ["images", "labels", "points", "polygons"],
        ):
            self.__setattr__(prefix, {})
            validated_transformations = _validate_transformations(
                elements, prefix, transformations, validated_coordinate_systems
            )
            for name, data in elements.items():
                alignment_info = {
                    validated_coordinate_systems[des]: validated_transformations[name][des]
                    for des in validated_transformations[name]
                }
                obj = element_class(data, alignment_info=alignment_info)
                self.__getattribute__(prefix)[name] = obj

        if table is not None:
            self._table = table

    def write(self, file_path: str) -> None:
        """Write to Zarr file."""

        store = parse_url(file_path, mode="w").store
        root = zarr.group(store=store)

        # get union of unique ids of all elements
        elems = set().union(*[set(i) for i in [self.images, self.labels, self.points, self.polygons]])

        for el in elems:
            elem_group = root.create_group(name=el)
            if self.images is not None and el in self.images.keys():
                self.images[el].to_zarr(elem_group, name=el)
            if self.labels is not None and el in self.labels.keys():
                self.labels[el].to_zarr(elem_group, name=el)
            if self.points is not None and el in self.points.keys():
                self.points[el].to_zarr(elem_group, name=el)
            if self.polygons is not None and el in self.polygons.keys():
                self.polygons[el].to_zarr(elem_group, name=el)

        if self.table is not None:
            write_table(tables=self.table, group=root, name="table")

    @property
    def table(self) -> AnnData:
        return self._table

    @classmethod
    def read(cls, file_path: str) -> SpatialData:
        from spatialdata._io.read import read_zarr

        sdata = read_zarr(file_path)
        return sdata

    def _gen_spatial_elements(self):
        # notice that this does not return a table, so we assume that the table does not contain spatial information;
        # this needs to be checked in the future as the specification evolves
        for k in ['images', 'labels', 'points', 'polygons']:
            d = getattr(self, k)
            for name, obj in d.items():
                yield k, name, obj

    @property
    def coordinate_systems(self) -> List[CoordinateSystem]:
        ##
        all_cs = {}
        gen = self._gen_spatial_elements()
        for _, _, obj in gen:
            for name, cs in obj.coordinate_systems.items():
                if name in all_cs:
                    added = all_cs[name]
                    assert cs == added
                else:
                    all_cs[name] = cs
        ##
        return list(all_cs.values())

    def __repr__(self) -> str:
        return self._gen_repr()

    def _gen_repr(
        self,
    ) -> str:
        def rreplace(s: str, old: str, new: str, occurrence: int) -> str:
            """Reverse replace a up to a certain number of occurences."""
            li = s.rsplit(old, occurrence)
            return new.join(li)

        def h(s: str) -> str:
            return s
            # return hashlib.md5(repr(s).encode()).hexdigest()

        ##
        descr = "SpatialData object with:"
        attributes = ["images", "labels", "points", "polygons", "table"]
        for attr in attributes:
            attribute = getattr(self, attr)
            if attribute is not None and len(attribute) > 0:
                descr += f"\n{h('level0')}{attr}"
                if isinstance(attribute, AnnData):
                    descr += f"{h('empty_line')}"
                    descr_class = attribute.__class__.__name__
                    descr += f"{h('level1.0')}'{attribute}': {descr_class} {attribute.shape}"
                    descr = rreplace(descr, h("level1.0"), "    └── ", 1)
                else:
                    # descr = rreplace(descr, h("level0"), "└── ", 1)
                    for k, v in attribute.items():
                        descr += f"{h('empty_line')}"
                        descr_class = v.data.__class__.__name__
                        if attr == "points":
                            descr += f"{h(attr + 'level1.1')}'{k}': {descr_class} with osbm.spatial {v.shape}"
                        elif attr == "polygons":
                            # assuming 2d
                            descr += (
                                f"{h(attr + 'level1.1')}'{k}': {descr_class} with osb.spatial describing "
                                f"{len(v.data.obs)} 2D polygons"
                            )
                        else:
                            descr += f"{h(attr + 'level1.1')}'{k}': {descr_class} {v.shape}"
                        # descr = rreplace(descr, h("level1.0"), "    └── ", 1)
            # the following lines go from this
            #     SpatialData object with:
            #     ├── Images
            #     │     └── 'image': DataArray (200, 100)
            #     └── Points
            #     │     ├── 'points': AnnData with osbm.spatial (50, 2)
            #     │     └── 'circles': AnnData with osbm.spatial (56, 2)
            # to this
            #     SpatialData object with:
            #     ├── Images
            #     │     └── 'image': DataArray (200, 100)
            #     └── Points
            #           ├── 'points': AnnData with osbm.spatial (50, 2)
            #           └── 'circles': AnnData with osbm.spatial (56, 2)
            latest_attribute_present = [
                attr for attr in attributes if getattr(self, attr) is not None and getattr(self, attr) != {}
            ][-1]
            if attr == latest_attribute_present:
                descr = descr.replace(h("empty_line"), "\n  ")
            else:
                descr = descr.replace(h("empty_line"), "\n│ ")

        descr = rreplace(descr, h("level0"), "└── ", 1)
        descr = descr.replace(h("level0"), "├── ")

        for attr in ["images", "labels", "points", "polygons", "table"]:
            descr = rreplace(descr, h(attr + "level1.1"), "    └── ", 1)
            descr = descr.replace(h(attr + "level1.1"), "    ├── ")
        ##
        descr += ('\nwith coordinate systems:\n')
        for cs in self.coordinate_systems:
            descr += f'▸ {cs.name}\n' \
                     f'    with axes: {", ".join(cs.axes)}\n'
            gen = self._gen_spatial_elements()
            elements_in_cs = []
            for k, name, obj in gen:
                if cs.name in obj.coordinate_systems:
                    elements_in_cs.append(f'{k}/{name}')
            if len(elements_in_cs) > 0:
                descr += f'    with elements: {", ".join(elements_in_cs)}\n'
        ##
        return descr


# def _iter_elems(
#     data: Mapping[str, Any], transforms: Optional[Mapping[str, Any]] = None
# ) -> Iterable[Tuple[Tuple[str, Any], Any]]:
#     # TODO: handle logic for multiple coordinate transforms and elements
#     # ...
#     return zip(
#         data.items(),
#         [transforms.get(k, None) if transforms is not None else None for k in data.keys()],
#     )


def _validate_coordinate_systems(
    coordinate_systems: Optional[List[Union[CoordSystem_t, CoordinateSystem]]]
) -> Dict[str, CoordinateSystem]:
    validated = []
    for c in coordinate_systems:
        if isinstance(c, CoordinateSystem):
            validated.append(copy.deepcopy(c))
        # TODO: add type check, maybe with typeguard: https://stackoverflow.com/questions/51171908/extracting-data-from-typing-types
        # elif type(c) == CoordSystem_t:
        else:
            v = CoordinateSystem()
            v.from_dict(c)
            validated.append(v)
        # else:
        #     raise TypeError(f"Invalid type for coordinate system: {type(c)}")
    assert len(coordinate_systems) == len(validated)
    assert len(validated) == len(set(validated))
    d = {v.name: v for v in validated}
    assert len(d) == len(validated)
    return d


# def _validate_dataset(
#     dataset: Optional[Mapping[str, Any]],
#     transformations: Mapping[(str, str), Union[BaseTransformation, Dict[Any]]],
#     coordinate_systems: List[Union[CoordSystem_t, CoordinateSystem]],
# ) -> Tuple[Dict[(str, str), BaseTransformation], List[CoordinateSystem]]:
#     validated_transformations = {}
#     if dataset is None:
#         return validated_transformations, coordinate_systems
#     elif isinstance(dataset, Mapping):
#         for name, element in dataset.items():
#             _validate_element(element, transformations)
#         # if tra is not None:
#         #     if not set(dataset).issuperset(dataset_transform):
#         #         raise ValueError(
#         #             f"Invalid `dataset_transform` keys not present in `dataset`: `{set(dataset_transform).difference(set(dataset))}`."
#         #         )
#     else:
#         raise TypeError('invalid type for "dataset"')


def _validate_transformations(
    elements: Mapping[str, Any],
    prefix: str,
    transformations: Mapping[Tuple[str, str], Union[BaseTransformation, Dict[str, Any]]],
    coordinate_systems: Dict[str, CoordinateSystem],
) -> Dict[str, Dict[str, BaseTransformation]]:
    validated: Dict[str, Dict[str, BaseTransformation]] = {}
    for name, element in elements.items():
        validated[name] = {}
    for (src, des), t in transformations.items():
        assert des in coordinate_systems.keys()
        if src.startswith(prefix):
            src_name = src[len(prefix) + 1 :]
            if src_name in elements:
                if isinstance(t, BaseTransformation):
                    v = copy.deepcopy(t)
                elif type(t) == Dict[str, Any]:
                    v = get_transformation_from_dict(t)
                else:
                    raise TypeError(f"Invalid type for transformation: {type(t)}")
                validated[src_name][des] = v
    return validated


if __name__ == "__main__":
    sdata = SpatialData.read("spatialdata-sandbox/merfish/data.zarr")
    s = sdata.polygons["anatomical"].data.obs.iloc[0]["spatial"]
    print(Polygons.string_to_tensor(s))
    print(sdata)
    print("ehi")
