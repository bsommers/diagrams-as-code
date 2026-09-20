"""Backward-compatibility facade forwarding to diagrams_as_code."""
import diagrams_as_code as _dac
from diagrams_as_code import *
from diagrams_as_code import __version__

__all__ = list(_dac.__all__)
