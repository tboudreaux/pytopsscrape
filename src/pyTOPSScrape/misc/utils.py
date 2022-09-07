"""
**Author:** Thomas M. Boudreaux\n
**Created:** Febuary 2021\n
**Last Modified:** September 2022\n

Opacity utility functions
"""
from pyTOPSScrape.misc import dataFiles

import numpy as np
try:
    import importlib.resources as pkg
except ImportError: #For python < 3.7
    import importlib_resources as pkg

def get_target_log_R() -> np.ndarray:
    """
    Get the ndarray for the LogR values that DSEP expects

    Returns
    -------
        targetLogR : np.ndarray
            Array of LogR values expected by DSEP in opacity table

    """
    targetLogR = np.arange(-8.0, 1.5, 0.5)
    return targetLogR

def get_target_log_T() -> np.ndarray:
    """
    Get the ndarray for the LogT values that DSEP expects

    Returns
    -------
        targetLogT : np.ndarray
            Array of LogT values expected by DSEP in opacity table

    """
    # The spacing on these is non-uniform so make the 4 sections then merge
    #  them together
    targetLogT_A = np.arange(3.75, 6.0, 0.05)
    targetLogT_B = np.arange(6.0, 8.1, 0.1)
    targetLogT_C = np.arange(8.1, 8.8, 0.2)
    targetLogT = np.concatenate((
        targetLogT_A,
        targetLogT_B,
        targetLogT_C
        ), axis=None)
    return targetLogT

def load_non_rect_map() -> np.ndarray:
    """
    Load the upper non rectabtular map from numpy binary which DSEP requires
    for the high temperature opacity files.

    Returns
    -------
        upperNonRect : np.ndarray
            Upper non rectangular map which DSEP requires.
    """
    with pkg.path(dataFiles, "nonRectProfile.npy") as path:
        upperNonRect = np.load(path)
    return upperNonRect
