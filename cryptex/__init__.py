"""
Cryptex - Enhanced Random Password Generator
A production-ready CLI tool for generating secure passwords with advanced features.
"""

__version__ = "1.0.2"
__author__ = "Tarek CHEIKH"
__email__ = "tarek@tocconsulting.fr"
__description__ = "Enhanced random password generator with advanced security features"

from .cli import main

__all__ = ["main"]