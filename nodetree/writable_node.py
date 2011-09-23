"""
WritableNode 
"""

import os
import pickle

import node

class WritableNodeMixin(object):
    """
    Mixin for a class of node which knows how to read and write
    itself to the filesystem via reader and writer
    functions.
    """
    extension = ".pickle"

    @classmethod
    def get_file_name(cls):
        return "%s%s" % (cls.name, cls.extension)

    @classmethod
    def reader(cls, handle):
        """Read a cache from a given dir."""
        return pickle.load(handle)

    @classmethod
    def writer(cls, handle, data):
        """Write a cache from a given dir."""
        pickle.dump(data, handle)
