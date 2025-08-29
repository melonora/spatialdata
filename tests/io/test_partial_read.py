from __future__ import annotations

import json
import os
import re
import tempfile
from collections.abc import Generator, Iterable
from contextlib import contextmanager
from dataclasses import dataclass
from json import JSONDecodeError
from pathlib import Path
from typing import TYPE_CHECKING

import py
import pytest
import zarr
from pyarrow import ArrowInvalid
from zarr.errors import ArrayNotFoundError

from spatialdata import SpatialData, read_zarr
from spatialdata.datasets import blobs

if TYPE_CHECKING:
    import _pytest.fixtures


@contextmanager
def pytest_warns_multiple(
    expected_warning: type[Warning] | tuple[type[Warning], ...] = Warning, matches: Iterable[str] = ()
) -> Generator[None, None, None]:
    """
    Assert that code raises a warnings matching particular patterns.

    Like `pytest.warns`, but with multiple patterns which each must match a warning.

    Parameters
    ----------
    expected_warning
        A warning class or a tuple of warning classes for which at least one matching warning must be found
    matches
        Regular expression patterns that of which each must be found in at least one warning message.
    """
    if not matches:
        yield
    else:
        with (
            pytest.warns(expected_warning, match=matches[0]),
            pytest_warns_multiple(expected_warning, matches=matches[1:]),
        ):
            yield


@pytest.fixture(scope="module")
def test_case(request: _pytest.fixtures.SubRequest):
    """
    Fixture that helps to use fixtures as arguments in parametrize.

    The fixture `test_case` takes up values from other fixture functions used as parameters.
    """
    fixture_function = request.param
    fixture_name = fixture_function.__name__
    return request.getfixturevalue(fixture_name)


@dataclass
class PartialReadTestCase:
    path: Path
    expected_elements: list[str]
    expected_exceptions: type[Exception] | tuple[type[Exception] | IOError, ...]
    warnings_patterns: list[str]


@pytest.fixture(scope="session")
def session_tmp_path(request: _pytest.fixtures.SubRequest) -> Path:
    """
    Create a temporary directory as a fixture with session scope and deletes it afterward.

    The default tmp_path fixture has function scope and cannot be used as input to session-scoped
    fixtures.
    """
    directory = py.path.local(tempfile.mkdtemp())
    request.addfinalizer(lambda: directory.remove(rec=1))
    return Path(directory)


@pytest.fixture(scope="module")
def sdata_with_corrupted_zarr_json(session_tmp_path: Path) -> PartialReadTestCase:
    # zarr.json is a zero-byte file, aborted during write, or contains invalid JSON syntax
    sdata = blobs()
    sdata_path = session_tmp_path / "sdata_with_corrupted_zarr_json.zarr"
    sdata.write(sdata_path)

    corrupted_elements = ["blobs_image", "blobs_labels", "blobs_points", "blobs_polygons", "table"]
    warnings_patterns = []
    for corrupted_element in corrupted_elements:
        elem_path = sdata.locate_element(sdata[corrupted_element])[0]
        (sdata_path / elem_path / "zarr.json").write_bytes(b"")
        warnings_patterns.append(f"{elem_path}: JSONDecodeError")
    not_corrupted = [name for _, name, _ in sdata.gen_elements() if name not in corrupted_elements]

    return PartialReadTestCase(
        path=sdata_path,
        expected_elements=not_corrupted,
        expected_exceptions=(JSONDecodeError, OSError),
        warnings_patterns=warnings_patterns,
    )


@pytest.fixture(scope="module")
def sdata_with_corrupted_image_chunks(session_tmp_path: Path) -> PartialReadTestCase:
    # images/blobs_image/0 is a zero-byte file or aborted during write
    sdata = blobs()
    sdata_path = session_tmp_path / "sdata_with_corrupted_image_chunks.zarr"
    sdata.write(sdata_path)

    corrupted = "blobs_image"
    os.unlink(sdata_path / "images" / corrupted / "0" / "zarr.json")  # it will hide the "0" array from the Zarr reader
    os.rename(sdata_path / "images" / corrupted / "0", sdata_path / "images" / corrupted / "0_corrupted")
    (sdata_path / "images" / corrupted / "0").touch()

    not_corrupted = [name for _, name, _ in sdata.gen_elements() if name != corrupted]

    return PartialReadTestCase(
        path=sdata_path,
        expected_elements=not_corrupted,
        expected_exceptions=(
            ArrayNotFoundError,
            TypeError,  # instead of ArrayNotFoundError, with dask>=2024.10.0 zarr<=2.18.3
        ),
        warnings_patterns=[rf"images/{corrupted}: (TypeError)"],
        # warnings_patterns=[rf"images/{corrupted}: (ArrayNotFoundError|TypeError)"],
    )


@pytest.fixture(scope="module")
def sdata_with_corrupted_parquet(session_tmp_path: Path) -> PartialReadTestCase:
    # points/blobs_points/0 is a zero-byte file or aborted during write
    sdata = blobs()
    sdata_path = session_tmp_path / "sdata_with_corrupted_parquet.zarr"
    sdata.write(sdata_path)

    corrupted = "blobs_points"
    os.rename(
        sdata_path / "points" / corrupted / "points.parquet",
        sdata_path / "points" / corrupted / "points_corrupted.parquet",
    )
    (sdata_path / "points" / corrupted / "points.parquet").touch()

    not_corrupted = [name for _, name, _ in sdata.gen_elements() if name != corrupted]

    return PartialReadTestCase(
        path=sdata_path,
        expected_elements=not_corrupted,
        expected_exceptions=ArrowInvalid,
        warnings_patterns=[rf"points/{corrupted}: ArrowInvalid"],
    )


@pytest.fixture(scope="module")
def sdata_with_missing_zarr_json(session_tmp_path: Path) -> PartialReadTestCase:
    # zarr.json is missing
    sdata = blobs()
    sdata_path = session_tmp_path / "sdata_with_missing_zattrs.zarr"
    sdata.write(sdata_path)

    corrupted = "blobs_image"
    (sdata_path / "images" / corrupted / "zarr.json").unlink()
    not_corrupted = [name for _, name, _ in sdata.gen_elements() if name != corrupted]

    return PartialReadTestCase(
        path=sdata_path,
        expected_elements=not_corrupted,
        expected_exceptions=OSError,
        warnings_patterns=[rf"images/{corrupted}: .* Unable to read the NGFF file"],
    )


@pytest.fixture(scope="module")
def sdata_with_invalid_zarr_json_violating_spec(session_tmp_path: Path) -> PartialReadTestCase:
    # zarr.json contains readable JSON which is not valid for SpatialData/NGFF specs
    # for example due to a missing/misspelled/renamed key
    sdata = blobs()
    sdata_path = session_tmp_path / "sdata_with_invalid_zattrs_violating_spec.zarr"
    sdata.write(sdata_path)

    corrupted = "blobs_image"
    json_dict = json.loads((sdata_path / "images" / corrupted / "zarr.json").read_text())
    del json_dict["attributes"]["ome"]["multiscales"][0]["coordinateTransformations"]
    (sdata_path / "images" / corrupted / "zarr.json").write_text(json.dumps(json_dict, indent=4))
    not_corrupted = [name for _, name, _ in sdata.gen_elements() if name != corrupted]

    return PartialReadTestCase(
        path=sdata_path,
        expected_elements=not_corrupted,
        expected_exceptions=KeyError,
        warnings_patterns=[rf"images/{corrupted}: KeyError: coordinateTransformations"],
    )


@pytest.fixture(scope="module")
def sdata_with_table_region_not_found(session_tmp_path: Path) -> PartialReadTestCase:
    # table/table/.zarr referring to a region that is not found
    # This has been emitting just a warning, but does not fail reading the table element.
    sdata = blobs()
    sdata_path = session_tmp_path / "sdata_with_invalid_zattrs_table_region_not_found.zarr"
    sdata.write(sdata_path)

    corrupted = "blobs_labels"
    # The element data is missing
    sdata.delete_element_from_disk(corrupted)
    # But the labels element is referenced as a region in a table
    regions = zarr.open_group(sdata_path / "tables" / "table" / "obs" / "region", mode="r")
    arrs = dict(regions.arrays())
    assert corrupted in arrs["categories"][arrs["codes"]]
    not_corrupted = [name for _, name, _ in sdata.gen_elements() if name != corrupted]

    return PartialReadTestCase(
        path=sdata_path,
        expected_elements=not_corrupted,
        expected_exceptions=(),
        warnings_patterns=[
            rf"The table is annotating '{re.escape(corrupted)}', which is not present in the SpatialData object"
        ],
    )


@pytest.mark.parametrize(
    "test_case",
    [
        sdata_with_corrupted_zarr_json,
        sdata_with_corrupted_image_chunks,
        sdata_with_corrupted_parquet,
        sdata_with_missing_zarr_json,
        sdata_with_invalid_zarr_json_violating_spec,
        sdata_with_table_region_not_found,
    ],
    indirect=True,
)
def test_read_zarr_with_error(test_case: PartialReadTestCase):
    if test_case.expected_exceptions:
        with pytest.raises(test_case.expected_exceptions):
            read_zarr(test_case.path, on_bad_files="error")
    else:
        read_zarr(test_case.path, on_bad_files="error")


@pytest.mark.parametrize(
    "test_case",
    [
        # sdata_with_corrupted_parquet,
        sdata_with_invalid_zarr_json_violating_spec,
        # sdata_with_table_region_not_found,
    ],
    indirect=True,
)
def test_read_zarr_with_warnings(test_case: PartialReadTestCase):
    with pytest_warns_multiple(UserWarning, matches=test_case.warnings_patterns):
        actual: SpatialData = read_zarr(test_case.path, on_bad_files="warn")

    actual_elements = {name for _, name, _ in actual.gen_elements()}
    assert set(test_case.expected_elements) == actual_elements
