"""
Diff-Marker module for MultiClip system
Provides text comparison and visual diff capabilities
"""

from .diff_manager import DiffManager
from .diff_interface import DiffInterface
from .diff_types import DiffResult, DiffLine, DiffType

__all__ = ['DiffManager', 'DiffInterface', 'DiffResult', 'DiffLine', 'DiffType']