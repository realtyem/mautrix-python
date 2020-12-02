# Copyright (c) 2020 Tulir Asokan
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from typing import Generic, TypeVar, Any
from abc import ABC, abstractmethod
from enum import Enum
import json

from ..primitive import JSON

T = TypeVar("T")


class Serializable:
    """Serializable is the base class for types with custom JSON serializers."""

    def serialize(self) -> JSON:
        """Convert this object into objects directly serializable with `json`."""
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, raw: JSON) -> Any:
        """Convert the given data parsed from JSON into an object of this type."""
        raise NotImplementedError()


class SerializerError(Exception):
    """
    SerializerErrors are raised if something goes wrong during serialization or deserialization.
    """
    pass


class GenericSerializable(ABC, Generic[T], Serializable):
    """
    An abstract Serializable that adds ``@abstractmethod`` decorators and a `Generic[T]` base class.
    """
    @classmethod
    @abstractmethod
    def deserialize(cls, raw: JSON) -> T:
        pass

    @abstractmethod
    def serialize(self) -> JSON:
        pass

    def json(self) -> str:
        """Serialize this object and dump the output as JSON."""
        return json.dumps(self.serialize())

    @classmethod
    def parse_json(cls, data: str) -> T:
        """Parse the given string as JSON and deserialize the result into this type."""
        return cls.deserialize(json.loads(data))


SerializableEnumChild = TypeVar("SerializableEnumChild", bound='SerializableEnum')


class SerializableEnum(Serializable, Enum):
    """
    A simple Serializable implementation for Enums.

    Examples:
        >>> class MyEnum(SerializableEnum):
        ...     FOO = "foo value"
        ...     BAR = "hmm"
        >>> MyEnum.FOO.serialize()
        "foo value"
        >>> MyEnum.BAR.json()
        '"hmm"'
    """

    def __init__(self, _) -> None:
        """
        A fake ``__init__`` to stop the type checker from complaining.
        Enum's ``__new__`` overrides this.
        """
        super().__init__()

    def serialize(self) -> str:
        """
        Convert this object into objects directly serializable with `json`, i.e. return the value
        set to this enum value.
        """
        return self.value

    @classmethod
    def deserialize(cls, raw: str) -> SerializableEnumChild:
        """
        Convert the given data parsed from JSON into an object of this type, i.e. find the enum
        value for the given string using ``cls(raw)``.
        """
        try:
            return cls(raw)
        except ValueError as e:
            raise SerializerError() from e

    def json(self) -> str:
        return json.dumps(self.serialize())

    @classmethod
    def parse_json(cls, data: str) -> SerializableEnumChild:
        return cls.deserialize(json.loads(data))

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"
