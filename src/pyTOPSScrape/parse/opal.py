from pyTOPSScrape.misc.utils import get_target_log_R
from pyTOPSScrape.misc.utils import get_target_log_T

import numpy as np
import re
import os

from typing import Tuple

def parse_OPAL_opacity_table(path : str) -> np.ndarray:
    """
    Parse the 126 tables out of a properly formated opacity table which dsep
    can understand. This idetifies all lines starting with Table # after the
    summary section and uses those to index where the tables begin. Given that
    dsep opacity tables are not square and that numpy can only handel
    rectangular data all rows are padded to the length of the longest row with
    np.nan. Therefore, nan(s) should be interprited as locations where the
    opacity table was undefined.

    Parameters
    ----------
        path : str
            path to opacity table

    Returns
    -------
        p : np.ndarray
            array of shape (126, 70, 19) where the first axis is the
            composition axis for the 126 compositions which dsep expects, the
            second is the temperature axis, and the third is the R axis.
    """
    with open(path) as f:
        contents = f.read().split('\n')
    sIndex = contents.index('************************************ Tables ************************************')
    ident = re.compile(r"TABLE\s+#(?:\s+)?\d+\s+\d+\s+X=\d\.\d+\s+Y=\d\.\d+\s+Z=\d\.\d+(?:\s+)?dX1=\d\.\d+\s+dX2=\d\.\d+")
    I = filter(lambda x: bool(re.match(ident, x[1])) and x[0] > sIndex+1, enumerate(contents))
    I = list(I)
    parsedTables = list(map(lambda x: [[float(z) for z in y.split()[1:]] for y in x], map(lambda x: contents[x[0]+6:x[0]+76], I)))

    paddedParsed = [list(map(lambda x: np.pad(x, (0, 19-len(x)), mode='constant', constant_values=(1,np.nan)), j)) for j in parsedTables]
    p = np.array(paddedParsed)

    return p

def load_opal(path : str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load both the opacity table as well as the LogR and LogT for each table.
    LogT and LogR are not actually taken from the table; rather, they are
    assumed to be the correct LogT and LogR and are simply constructed from the
    general LogR and LogT constuctors already present in pysep.

    Parameters
    ----------
        path : str
            path to opacity table to load.

    Returns
    -------
        LogT : np.ndarray(dtype='float64')
            Numpy array of shape (70,) with each required LogT value in it.
        LogR : np.ndarray(dtype='float64')
            Numpy array of shape (19,) wich each required LogR value in it.
        p : np.ndarray(dtype='float64')
            array of shape (126, 70, 19) where the first axis is the
            composition axis for the 126 compositions which dsep expects, the
            second is the temperature axis, and the third is the R axis.
    """
    if not os.path.exists(path):
        raise OSError(f"Error!, Opacity file at {path} does not exist")
    p = parse_OPAL_opacity_table(path)
    LogT = get_target_log_T()
    LogR = get_target_log_R()
    return LogT, LogR, p
