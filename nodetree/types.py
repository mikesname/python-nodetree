"""
Nodetree types.
"""

from __future__ import absolute_import

from . import registry


class TypeType(type):
    """Meta class for types.  Automatically registers
    the type with the type registry."""

    def __new__(cls, name, bases, attrs):
        new = super(TypeType, cls).__new__
         # Abstract class: abstract attribute should not be inherited.
        if attrs.pop("abstract", None) or not attrs.get("autoregister", True):
            return new(cls, name, bases, attrs)

        if name not in registry.types:
            typecls = new(cls, name, bases, attrs)
            typecls.name = name
            registry.types.register(typecls)
        return registry.types[name]

    def __repr__(cls):
        return "<class Type %s>" % cls.__name__
            


class AnyType(object):
    """Type object.  Data type which knows how to
    serialize and unserialise itself."""

    __metaclass__ = TypeType
    ext = ".pickle"

    @property
    def file_name(cls):
        return "%s%s" % (cls.name, cls.ext)

    @classmethod
    def reader(cls, handle):
        """Read a cache from a given dir."""
        return pickle.load(handle)

    @classmethod
    def writer(cls, handle, data):
        """Write a cache from a given dir."""
        pickle.dump(data, handle)

