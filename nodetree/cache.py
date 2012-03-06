"""Classes for customising node caching."""


class BasicCacher(object):
    """Basic in-memory caching."""
    def __init__(self, logger=None):
        self._cache = {}
        self.logger = logger

    def set_cache(self, node, data):
        """Store some data on the object."""
        self._cache[node.label] = data

    def get_cache(self, node):
        """Return cached data."""
        return self._cache.get(node.label)

    def has_cache(self, node):
        """Check if a cache exists for a node."""
        return self._cache.get(node.label) is not None

    def clear_cache(self, node):
        """Clear a node's cache."""
        if self._cache.get(node.label):
            del self._cache[node.label]

    def clear(self):
        """Clear the entire cache."""
        self._cache = {}

    def __repr__(self):
        return "<%s>" % self.__class__.__name__


