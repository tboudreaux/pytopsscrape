"""
**Author:** Thomas M. Boudreaux\n
**Created:** September 2021\n
**Last Modified:** September 2022

Functions for parsing raw output from TOPS webform

Examples
--------
Say you have some raw output from the TOPS webform saved to a file called
"rawOutputTest.dat", then you may parse that with

>>> rho, LogT, RMO = load_tops("rawOutputTest.dat")

"""
from typing import Tuple
import re
import numpy as np

import os

def load_tops(
        TOPSTable: str,
        n: int=100
        ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Given the path to a file queried from the TOPS webform put it into a
    computer usable form of 3 arrays. One array of mass density, one of
    LogT and one of log Rossland Mean Opacity

    Parameters
    ----------
        TOPSTable : string
            Path to file queried from TOPS webform

        n : int, default=100
            The size of density grid used in TOPS query form.

    Returns
    -------
        rho : np.ndarray(shape=n)
            Array of mass densities (in cgs) parsed from TOPS table.
        LogT: np.ndarray(shape=m)
            Array of temperatures (in Kelvin) parsed from TOPS table.
        OPALTableInit : np.ndarray(shape=(m,n))
            Array of Rossland Mean Opacities parsed from TOPS table.
    """
    with open(TOPSTable) as f:
        # TOPS returns a table with non breaking spaces (\u00A0). These break
        #  pythons regex so replace all of these with tabs at read in time
        contents = f.read().replace("\u00A0", "\t")

    # This regular expression locates n tables in the TOPS return file. If 
    #  the header format of those tables chanegs this regex will also have
    #  to change.
    tgroups = re.findall(r"(Rosseland\s+and\s+Planck\s+opacities\s+and\s+"
                         r"free\s+electrons\s+Density\s+Ross\s+opa\s+Planck\s+"
                         r"opa\s+No\.\s+Free\s+Av\s+Sq\s+Free\s+(T=\s+\d+\.?\d+"
                         r"E[-|+]\d+)\s+((\d\.\d+E[-|+]\d+"
                         r"(\s+)?){{5}}\n?){{{}}})".format(n), contents)

    # convert from keV in TOPS to K in DSEP
    temperatures = np.array([float(x[1].split()[1])*11604525.0061657
                            for x in tgroups])
    # extract all of the RMO data from the TOPS files
    # this is done by iterating through the first element of every tgroup.
    #   on each of these elements a number following some amount of white space
    #   is matched (white space is a nonmatching group) with a regex. Then,
    #   those matches are all cast to floats. The first element per tgroup is
    #   actually the temperature in kev, so this is stripped as we already
    #   have those. Then the returned values for the tgroup is reshaped to
    #   100,5 (rho, RMO, PO, number free, avg sq free) with 100 densities. 
    #   At this point this is an in indexable equivilent to how the data is
    #   stored in the TOPS file. 
    subTables = np.array([np.array([float(y)
                                     for y in
                                     re.findall(r"(?:\s+)?(\d\.\d+E[-|+]\d{2})",
                                                x[0])
                                   ]
                                  )[1:].reshape(100, 5)
                          for x in
                          tgroups])

    rho = subTables[0, :, 0]
    RMO = subTables[:, :, 1]

    LogT = np.log10(temperatures)
    logRMO = np.log10(RMO)

    OPALTableInit = np.zeros(shape=(rho.shape[0], LogT.shape[0]))

    # This transposes the table basically
    for i, _ in enumerate(LogT):
        OPALTableInit[:, i] = logRMO[i]
    return rho, LogT, OPALTableInit

def extract_composition_path(
        path: str
        ) -> Tuple[float, float, float]:
    """
    Given the name of a TOPS return file (named in the format OP:n_X_Y_Z.dat)
    extract X, Y, and Z

    Parameters
    ----------
        path : string
            path to TOPS return file

    Returns
    -------
        X : float
            Hydrogen mass fraction
        Y : float
            Helium mass fraction
        Z : Metal mass fraction
    """
    filename = os.path.basename(path)
    filename = filename.strip('.dat')
    filenameParts = filename.split('_')
    X = float(filenameParts[1])
    Y = float(filenameParts[2])
    Z = float(filenameParts[3])
    return X, Y, Z
