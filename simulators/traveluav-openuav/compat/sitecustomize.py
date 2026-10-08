"""Python 3.10 aliases required by legacy Tornado 4.5.3 / AirSim RPC.

This restores removed collection names only; sensor and flight APIs are unchanged.
"""
import collections
import collections.abc

for name in ("Mapping", "MutableMapping", "Sequence", "MutableSequence", "Set", "MutableSet", "Iterable", "Callable"):
    if not hasattr(collections, name):
        setattr(collections, name, getattr(collections.abc, name))
