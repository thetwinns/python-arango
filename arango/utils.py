__all__ = [
    "suppress_warning",
    "get_col_name",
    "get_doc_id",
    "is_none_or_int",
    "is_none_or_str",
]

import json
import logging
from contextlib import contextmanager
from typing import Any, Iterator, Sequence, Union

from arango.exceptions import DocumentParseError
from arango.typings import Json


@contextmanager
def suppress_warning(logger_name: str) -> Iterator[None]:
    """Suppress logger messages.

    :param logger_name: Full name of the logger.
    :type logger_name: str
    """
    logger = logging.getLogger(logger_name)
    original_log_level = logger.getEffectiveLevel()
    logger.setLevel(logging.CRITICAL)
    yield
    logger.setLevel(original_log_level)


def get_col_name(doc: Union[str, Json]) -> str:
    """Return the collection name from input.

    :param doc: Document ID or body with "_id" field.
    :type doc: str | dict
    :return: Collection name.
    :rtype: str
    :raise arango.exceptions.DocumentParseError: If document ID is missing.
    """
    try:
        doc_id: str = doc["_id"] if isinstance(doc, dict) else doc
    except KeyError:
        raise DocumentParseError('field "_id" required')
    else:
        return doc_id.split("/", 1)[0]


def get_doc_id(doc: Union[str, Json]) -> str:
    """Return the document ID from input.

    :param doc: Document ID or body with "_id" field.
    :type doc: str | dict
    :return: Document ID.
    :rtype: str
    :raise arango.exceptions.DocumentParseError: If document ID is missing.
    """
    try:
        doc_id: str = doc["_id"] if isinstance(doc, dict) else doc
    except KeyError:
        raise DocumentParseError('field "_id" required')
    else:
        return doc_id


def is_none_or_int(obj: Any) -> bool:
    """Check if obj is None or an integer.

    :param obj: Object to check.
    :type obj: Any
    :return: True if object is None or an integer.
    :rtype: bool
    """
    return obj is None or (isinstance(obj, int) and obj >= 0)


def is_none_or_str(obj: Any) -> bool:
    """Check if obj is None or a string.

    :param obj: Object to check.
    :type obj: Any
    :return: True if object is None or a string.
    :rtype: bool
    """
    return obj is None or isinstance(obj, str)


def is_none_or_bool(obj: Any) -> bool:
    """Check if obj is None or a bool.

    :param obj: Object to check.
    :type obj: Any
    :return: True if object is None or a bool.
    :rtype: bool
    """
    return obj is None or isinstance(obj, bool)


def get_batches(elements: Sequence[Json], batch_size: int) -> Iterator[Sequence[Json]]:
    """Generator to split a list in batches
        of (maximum) **batch_size** elements each.

    :param elements: The list of elements.
    :type elements: Sequence[Json]
    :param batch_size: Max number of elements per batch.
    :type batch_size: int
    """
    for index in range(0, len(elements), batch_size):
        yield elements[index : index + batch_size]


def build_filter_conditions(filters: Json) -> str:
    """Build a filter condition for an AQL query.

    :param filters: Document filters.
    :type filters: Dict[str, Any]
    :return: The complete AQL filter condition.
    :rtype: str
    """
    if not filters:
        return ""

    conditions = [f"doc.`{k}` == {json.dumps(v)}" for k, v in filters.items()]
    return "FILTER " + " AND ".join(conditions)
