"""
**Author:** Thomas M. Boudreaux\n
**Created:** September 2021\n
**Last Modified:** September 2022

Main conversion code for TOPS api, responsible for takine many TOPS results and
merging them into a single OPAL formate high temperature opacity file.
"""
from pyTOPSScrape.parse import parse_abundance_map
from pyTOPSScrape.parse import load_tops
from pyTOPSScrape.parse import get_base_composition

from pyTOPSScrape.parse.tops import extract_composition_path

from pyTOPSScrape.misc.utils import get_target_log_R
from pyTOPSScrape.misc.utils import get_target_log_T
from pyTOPSScrape.misc.utils import load_non_rect_map

import os
import re
from tqdm import tqdm
from datetime import date

import numpy as np
from scipy.interpolate import interp2d

from typing import Tuple, List, Union
from collections.abc import Iterator, Iterable

# Bounds of the OPAL formated tables, format is 
# {'filler': [(row, number to be filled)]}

def comp_list_2_dict(
        compList: List[Tuple[str, float, float]]
        ) -> dict:
    """
    Take a list containing compsoition information for a star in the form of
    [('Element Symbol', massFraction, numberFraction),...] and convert that
    into a dictionary of the form:
    {'Element Symbol': (massFraction, numberFraction),..}.

    Parameters
    ----------
        compList : Iterator
            list of the form: [(ElementSymbol, massFrac, numberFrac, ZmassFrac,
            massFrac Uncertanity, numberFrac Uncertanity, ZMassFrac
            Uncertanity),...]

    Returns
    -------
        dict
            Dictionary of the form {'Element':(massFrac, numberFrac, ZmassFrac,
            massFrac Uncertanity, numberFrac Uncertanity, ZMassFrac
            Uncertanity),...}
    """
    compDict = dict()
    for element, *info in compList:
        compDict[element] = (info[0],
                             info[1],
                             info[2],
                             info[3],
                             info[4],
                             info[5])

    # Set Potassium to zero because the programs I am using do not
    #  save a potasium mass fraction but the header needs it so 
    #  I'm just setting it to zero so that there is an entry in the dict
    #  for it. 
    compDict['K'] = (0.0,0.0,0.0,0.0,0.0,0.0)
    return compDict



def format_opal_comp_table(
        LogR: np.ndarray,
        LogT: np.ndarray,
        LogRMO: np.ndarray,
        TNUM: int,
        comp: dict = None,
        upperNonRect: np.ndarray = None,
        nonRect : bool = False
        ) -> Tuple[str, str]:
    """
    Take in all the information from a given TOPS tables and format it
    to the proper format for DSEP to undersand. Leave in some placeholders
    so that in future table can be labeld as the proper number.

    Parameters
    ----------
        LogR : ndarray
            The Log R value array (horizontal axis of table)
        LogT : ndarray
            The Log Temperature value array (vertical axis)
        LogRMO : ndarray
            all of the RMO values associated with R and T
        TNUM : int
            Table number
        comp : dict, optional
            composition dictionary. If not provided placeholders are left in
            place so that it may be filled later on
        upperNonRect : ndarray, default=None
            Array describing how to fill the top of the table non rectangurally
            This array should be of the shape (nRowsPerTable * nTables, 3). So
            if you have 5 tables each with 70 rows then this array should have
            a shape of (350,3). The first column of this array correspond to
            the table that the row is a member of, the second column correspond
            to the row in that table that the row is. so the first row of the
            first table would be at upperNonRect[0,:] = [0,0,...] while the
            first row of the second table would be at upperNonRect[n,:]
            [1,0,...]. The final column desribes how many of the elements,
            counting from the left of the opacity table should be blanked out
            to 99.999 (the sentinal value DSEP uses for non entries). So a row
            of [2,55,8] would mean that for the 56th row in the 3rd table blank
            out the firts 8 opacity values (opacities for the first 8 values of
            logR).
        nonRect : bool, default = False
            Flag to control whether output tables will be rectangular or have
            their corners cut off in a way consistant which how DSEP expects
            OPAL tables.

    Returns
    -------
        metaLine : str
            header line for each table, may or may not have placeholders in it
        fullTable : str
            full table to be places in opacity file

    """
    # place holder empty string
    ph = ''
    # Lower non rectangular bounds used by DSEP. Will be used of nonRect
    # is set to True, otherwise will not be used.
    OUTOFBOUNDS = {np.nan:
                    [(57, -1), (58, -2), (59, -2), (60, -3), (61, -3), (62, -3),
                     (63, -3), (64, -4), (65, -4), (66, -4), (67, -4), (68, -4),
                     (69, -5)]}
    if not isinstance(comp, Iterable):
        metaLine = (f" TABLE #TNUMNSPACES{date.today().strftime('%Y%m%d')}0001"
                    f"TSPACESX=TARGX Y=TARGY Z=TARGZ"
                     " dX1=0.0000 dX2=0.0000")
    else:
        metaLine = (f" TABLE #TNUMNSPACES{date.today().strftime('%Y%m%d')}0001"
                    f"TSPACESX={abs(comp[0]):0.4f} Y={abs(comp[1]):0.4f}"
                    f" Z={abs(comp[2]):0.4f} dX1=0.0000 dX2=0.0000")
    logRHeader = ' '.join(["{:>6.1f}".format(round(x, 1)) for x in LogR])

    # Build the metadataline for the table, including the date this code was run
    titleLine = f"{ph:>50}log R"
    headerLine = f"logT{logRHeader}"

    dataLines = list()
    if nonRect:
        data = LogRMO.copy()
        # only make the table non rectangular if asked
        #  the reason for not always doing this is that 
        #  this function is called twice, the first time
        #  to transfer the tables from TOPS diretly
        #  those transfered tables are then used to interpolate
        #  we want rectangulat tables for that interpolation.
        # TODO: Remove introspection as it is bad practice
        if hasattr(upperNonRect, "__iter__"):
            assert upperNonRect is not None
            # cut data out from the bottom right of the table per DSEP
            for filler in OUTOFBOUNDS:
                for row in OUTOFBOUNDS[filler]:
                    start = row[1]
                    replacement = np.repeat(filler, abs(row[1]))
                    data[row[0]][start:] = replacement
            # cut data out from the top right of the table per DSEP
            subNRE = upperNonRect[upperNonRect[:, 0] == TNUM]
            for nre in subNRE:
                if nre[2] != 0.0:
                    replacement = np.repeat(9.999, int(nre[2]))
                    data[int(nre[1])][:int(nre[2])] = replacement
    else:
        data = LogRMO.copy()

    for line, temperature in zip(data, LogT):
        # Cut max value to the same as DSEP's max value (9.99) any values bigger
        #  would cause errors
        adjustedLine = line[~np.isnan(line)]
        # add opacity values in line rounded off to the nearest thousands
        joinedLine = ' '.join(["{:>6.3f}".format(round(x, 3))
                                for x in adjustedLine])
        dataLines.append(f"{temperature:0.2f} {joinedLine}")
    dataTable = '\n'.join(dataLines)
    fullTable = '\n'.join([metaLine,
                           '',
                           titleLine,
                           '',
                           headerLine,
                           '',
                           dataTable,
                           ''])
    return metaLine, fullTable

def format_OPAL_header(
        compDict: dict
        ) -> str:
    """
    Writes the header of the opacity table that DSEP expects. This is written
    to be the same length (and basically the same contents) of the header
    from the OPACITY project. Not sure if that is required; however, if so
    I am matching it.

    Parameters
    ----------
        compDict : dict
            dictionary in the form: {'Element': (massFrac, numFrac), ...} used
            to fill up the header with composition information. This is meant
            to be the "solar" compositon of whatever mix you are using so...
            [Fe/H] = 0.0, [alpha/H] = 0.0, a(He) = 10.93

    Returns
    -------
        string
            The Header to be prepended to the opacity table file

    """
    headerBaseString = f""" Updated TOPS Rosseland mean opacity tables   (date {date.today().strftime('%Y%m%d')})
 Description of modifications given in Iglesias & Rogers, ApJ464,943(1996)
 
  lines 1-60 contain brief table description
  lines 61-240 contain table summaries
  lines 241-end contain tables. Each table is 77 lines long

 NOTE: File is compatible with interpolation routines.
 
 Definitions:
 
 The logarithm of the Rosseland mean opacity [cm**2/g] as a function
 of log(T) for columns of constant log(R), where
 
    R=density[g/cm**3]/T6**3, T6=1.e-6*T[degrees]
    log(T) range: 70 values from 3.75 to 8.70
    log(R) range: 19 values from -8.0 to +1.0

 NOTE: Tables are NOT rectangular
       values=9.999 or blanks are out of table range

 Composition parameters:
   X   = Hydrogen mass fraction
   Y   = Helium mass fraction
   Z   = Metal mass fraction
   dX1 is not relevant for Type 1 tables
   dX2 is not relevant for Type 1 tables

 Abundances for {date.today().strftime('%Y%m%d')}0001     composition: GS98 mix (N.Grevesse & A.J.Sauval 1998, Space Sci. Rev. 85, 161)"""

    # Note that the num frac programs I'm using don't contain potassium so I manually set that to 0 abouve
    #  in the function which builds compDict.
    # I think I need to propery add the mass fractions into this
    #  I thught this was just a header but it seems that data is actually
    #  being read from here
    AbuncenceSummary = f""" Element   Abundance - relative metal: number fraction   mass fraction   atomic mass
   H     log(A)=                                                           1.00790
   He    log(A)=                                                           4.00260
   Li    log(A)=
   Be    log(A)=
   B     log(A)=
   C     log(A)=        -----------------  {compDict['C'][1]:0.6f}        {compDict['C'][2]:0.6f}       12.01100
   N     log(A)=        -----------------  {compDict['N'][1]:0.6f}        {compDict['N'][2]:0.6f}       14.00670
   O     log(A)=        -----------------  {compDict['O'][1]:0.6f}        {compDict['O'][2]:0.6f}       15.99940
   F     log(A)=
   Ne    log(A)=        -----------------  {compDict['Ne'][1]:0.6f}        {compDict['Ne'][2]:0.6f}       20.17900
   Na    log(A)=        -----------------  {compDict['Na'][1]:0.6f}        {compDict['Na'][2]:0.6f}       22.98977
   Mg    log(A)=        -----------------  {compDict['Mg'][1]:0.6f}        {compDict['Mg'][2]:0.6f}       24.30500
   Al    log(A)=        -----------------  {compDict['Al'][1]:0.6f}        {compDict['Al'][2]:0.6f}       26.98154
   Si    log(A)=        -----------------  {compDict['Si'][1]:0.6f}        {compDict['Si'][2]:0.6f}       28.08550
   P     log(A)=        -----------------  {compDict['P'][1]:0.6f}        {compDict['P'][2]:0.6f}       30.97376
   S     log(A)=        -----------------  {compDict['S'][1]:0.6f}        {compDict['S'][2]:0.6f}       32.06000
   Cl    log(A)=        -----------------  {compDict['Cl'][1]:0.6f}        {compDict['Cl'][2]:0.6f}       35.45300
   Ar    log(A)=        -----------------  {compDict['Ar'][1]:0.6f}        {compDict['Ar'][2]:0.6f}       39.94800
   K     log(A)=        -----------------  {compDict['K'][1]:0.6f}        {compDict['K'][2]:0.6f}       39.09830
   Ca    log(A)=        -----------------  {compDict['Ca'][1]:0.6f}        {compDict['Ca'][2]:0.6f}       40.08000
   Sc    log(A)=
   Ti    log(A)=        -----------------  {compDict['Ti'][1]:0.6f}        {compDict['Ti'][2]:0.6f}       47.90000
   V     log(A)=
   Cr    log(A)=        -----------------  {compDict['Cr'][1]:0.6f}        {compDict['Cr'][2]:0.6f}       51.99600
   Mn    log(A)=        -----------------  {compDict['Mn'][1]:0.6f}        {compDict['Mn'][2]:0.6f}       54.93800
   Fe    log(A)=        -----------------  {compDict['Fe'][1]:0.6f}        {compDict['Fe'][2]:0.6f}       55.84700
   Co    log(A)=
   Ni    log(A)=        -----------------  {compDict['Ni'][1]:0.6f}        {compDict['Ni'][2]:0.6f}       58.70000"""
    return '\n'.join([headerBaseString, '', AbuncenceSummary, ''])

def format_OPAL_table(
        tableDict: List[dict],
        compDict: dict
        ) -> str:
    """
    Given a dictionary of tables and a composition Dictionary for solar
    composition in a given mixture (AGSS08, GS98, etc...) merge all the
    information together into a string which can be written to disk and
    would be the format of an opacoty project table (what DSEP expects)

    Parameters
    ----------
        tableDict : dict
            dictionary of table elements, containing a "Summary" entry
            (metadata) and a "Table" entry. All occcurences of the the string
            "TNUM" will be replaced with the index+1 of where that table occurs
            in the file.
        compDict : dict
            dictionary in the form: {'Element': (massFrac, numFrac), ...} used
            to fill up the header with composition information. This is meant
            to be the "solar" compositon of whatever mix you are using so...
            [Fe/H] = 0.0, [alpha/H] = 0.0, a(He) = 10.93

    Returns
    -------
        OPALFormatted : string
            Opacity Project formated table as a string which can be written to
            disk

    """
    ph = '' # place holder empty string to be used when adding arbitrary spaces
    header = format_OPAL_header(compDict)
    # The space at the start of this (and the table summary lines) is
    #  important as that seems to be how opal95.f determines comment lines
    summaryHeader = f" Table Summaries- There are {len(tableDict)} tables"

    # Put together the summary list of table number and corresponding 
    #  compesition at the top of the file
    summaries = map(lambda x: x[1]['Summary'].replace('TNUM', f"{x[0]+1:>3}"),
                    enumerate(tableDict))
    summaries = map(lambda x: x.replace('NSPACES', f"{ph:<2}"), summaries)
    summaries = map(lambda x: x.replace('TSPACES', f"{ph:<6}"), summaries)
    summary = '\n'.join(list(summaries))

    # In the current opacity files there are 50 lines of blank space, emulate
    #  that
    interStage = '\n'.join([' ']*51)
    tableStart = ("************************************ Tables ****************"
                  "********************")
    # merge the actual tables together (note these contain metadata and table
    #  information, but that has already been put in the right order on a
    #  table-by-table basis.
    # The [1:] is to remove the space at the start of the line which is used
    #  to mark the summary lines as comments.
    tables = map(lambda x: x[1]['Table'][1:].replace('TNUM', f"{x[0]+1:>3}"),
                 enumerate(tableDict))
    tables = map(lambda x: x.replace('NSPACES', f"{ph:<5}"), tables)
    tables = map(lambda x: x.replace('TSPACES', f"{ph:<7}"), tables)
    tablesFull = '\n'.join(list(tables))
    # Connect all theses sections together seperated by new lines
    OPALFormatted = '\n'.join([header,
                      summaryHeader,
                      '',
                      summary,
                      interStage,
                      tableStart,
                      '',
                      tablesFull])


    return OPALFormatted

def convert_rho_2_LogR(
        rho: np.ndarray,
        LogT: np.ndarray,
        RMO: np.ndarray
        ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Maps a given kappa(rho,logT) parameter space onto a kappa(LogR, LogT) field
    through interpolation. The final field is the field that DSEP needs.
    Parameters
    ----------
        rho  : np.ndarray
            mass density array of size n
        LogT : np.ndarray
            LogT array of size m
        RMO : np.ndarray
            Opacity Array of size m x n
    Returns
    -------
        targetLogR : np.ndarray(shape=19)
            Log R values which dsep requires
        targetLogT : np.ndarray(shape=70)
            Log T values which dsep requires
        Opacity : np.ndarray(shape=(70, 19))
            Opacity array now interpolated into LogR, LogT space from rho LogT
            space and sampled at the exact LogR and LogT values required.
    """
    # build a function that can interpolate log opacity on a mass density log
    #  temperature grid
    kappaFunc = interp2d(LogT, rho, RMO, kind='cubic')

    # mapping from T, R to rho
    rhof = lambda T, R: R*((T*1e-6)**3)

    # The target LogR an LogT grids which we would like to use
    targetLogT = get_target_log_T()
    targetLogR = get_target_log_R()

    # The array to be filled with the converted opaicities
    opacity = np.zeros(shape=(targetLogT.shape[0], targetLogR.shape[0]))

    # This function maps the vector function kappaFunc to a scaler function
    #  so that for a given target R and temperature array you get out an 
    #  1D array not a 2D array. There is probably a more elegant way of doing
    #  this. However, theis seems to work well enough and is not slow persay.
    opacityF = lambda x, RTarg: kappaFunc(x, rhof(10**x, 10**RTarg))

    for i, logR in enumerate(targetLogR):
        # vectorize it so I can call it. However, this can only take a function
        #  of one argument so use an anoymous function to hide the second
        #  argument
        f = np.vectorize(lambda x: opacityF(x, logR))
        opacity[:, i] = f(targetLogT)

    return targetLogR, targetLogT, opacity

def format_TOPS_to_OPAL(
        TOPSTable: str,
        comp: tuple,
        tnum: int,
        upperNonRect: np.ndarray=None
        ) -> Tuple[str, float, float, float, str, np.ndarray, np.ndarray, np.ndarray]:
    """
    Take the path to a table queried from the TOPS web form and fully convert it
    into a table which can be directly read by DSEP. (Note this function
    does not write anything to disk; however, the return products can be
    written to disk)

    Parameters
    ----------
        TOPSTable : string
            path to table queried from TOPS web form
        comp : dict
            composition dictionary
        tnum : int
            table number
        upperNonRect : np.ndarray, optional
            array describing how to fill the top of the table non rectangurally

    Returns
    -------
        metaLine : str
            metadata extracted from table
        X : float
            Hydrogen mass fraction
        Y : float
            Helium mass fraction
        Z : float
            Metal mass fraction
        fullTable : str
            The full table as a string which may be directly written to a file.
            Note that this includes all the relevant white space to allow this
            table to be parsed by DSEP.
        LogR : np.ndarray(shape=19)
            Log R values which dsep expects
        LogT : np.ndarray(shape=70)
            Log Temperature values which dsep expects.
        LogRMO : np.ndarray(shape=(70, 19))
            Log rossland mean opacities for the LogT and LogR arrays
    """
    # Parse the raw TOPS data into a usable form
    rhoInit, logTInit, OPALTableInit = load_tops(TOPSTable)

    # Interpolate raw TOPS data onto the LogR LogT grid DSEP expects
    LogR, LogT, LogRMO = convert_rho_2_LogR(rhoInit, logTInit, OPALTableInit)

    X, Y, Z = extract_composition_path(TOPSTable)

    metaLine, fullTable = format_opal_comp_table(LogR,
                                                 LogT,
                                                 LogRMO,
                                                 tnum,
                                                 upperNonRect=upperNonRect)

    return metaLine, X, Y, Z, fullTable, LogR, LogT, LogRMO

def rebuild_formated_tables(
        formatedTables : List[dict],
        interpRMO : np.ndarray,
        pContents : np.ndarray,
        upperNonRect: Union[np.ndarray, None],
        nonRect : bool = False
        ) -> List[dict]:
    """
    Iterate over a list of opacity tables and a list of desired chemical
    compositions then replace the contents of the table list with the newly
    updated RMOs frmo the interpolation.

    Parameters
    ----------
        formatedTables : list of dicts
            List of dictionaries holding three axis each. X, Z, and LogRMO.
            These are the "observed" values to be interpolared
        interpRMO : ndarray
            RMOs after interpolation to LogR-LogT space from rho-LogT space.
        pContents : np.array(shape=(n, 3))
            Numpy array of all the compositions of length n.  For a dsep n=126.
            Along the second axis the first column is X, the second is Y, and
            the third is Z.
        upperNonRect : ndarray
            Array describing how to fill the top of the table non rectangurally
            This array should be of the shape (nRowsPerTable * nTables, 3). So
            if you have 5 tables each with 70 rows then this array should have
            a shape of (350,3). The first column of this array correspond to
            the table that the row is a member of, the second column correspond
            to the row in that table that the row is. so the first row of the
            first table would be at upperNonRect[0,:] = [0,0,...] while the
            first row of the second table would be at upperNonRect[n,:]
            [1,0,...]. The final column desribes how many of the elements,
            counting from the left of the opacity table should be blanked out
            to 99.999 (the sentinal value DSEP uses for non entries). So a row
            of [2,55,8] would mean that for the 56th row in the 3rd table blank
            out the firts 8 opacity values (opacities for the first 8 values of
            logR).
        nonRect : bool, default = False
            Flag to control whether output tables will be rectangular or have
            their corners cut off in a way consistant which how DSEP expects
            OPAL tables.

    Returns
    -------
        formatedTables : list of dicts
            List of dictionaries holding three axis each. X, Z, and LogRMO.
            These have been updated to reflect the compositions in pContents.
    """
    for tnum, (table, RMO, comp) in enumerate(zip(formatedTables, interpRMO, pContents)):
        table["X"] = comp[0]
        table["Y"] = comp[1]
        table["Z"] = comp[2]

        metaLine, fullTable = format_opal_comp_table(table['LogR'],
                                                     table['LogT'],
                                                     RMO,
                                                     tnum,
                                                     comp=comp,
                                                     upperNonRect=upperNonRect,
                                                     nonRect=nonRect)
        table["Summary"] = metaLine
        table["Table"] = fullTable
        table["LogRMO"] = RMO
    return formatedTables


def TOPS_2_OPAL(
        outputDirectory : str,
        aTable : str,
        aMap : str,
        output : str,
        nonRect : bool = False
        ):
    """
    Main conversoin utility to go between some set of TOPS tables and an OPAl
    table. Will take a set of 126 TOPS tables where each one is the opacity for
    one composition over a number of temperature and densities and rearange them
    into one large file with 126 tables within it. Each table will be over a
    range of temperatures and R values. To get to R val interpolation is used.

    Parameters
    ----------
        outputDirectory : str
            Path to directory where TOPS query results are stored
        aTable : str
            Path to a reference abundance table to use when filling the header
            with compositional information
        aMap : str
            Path to the abundance map. This should be an ascii file where each
            row is X,Y,Z. Each row will correspond to one rescaled composition
            which will be queried.
        output : str
            Path to save final OPAL formated table too
        nonRect : bool, default=False
            Flag to control whether output tables will be rectangular or have
            their corners cut off in a way consistant which how DSEP expects
            OPAL tables.
    """
    # select all the files matchiong the TOPS file name format from the
    #  save directory
    dirContents = os.listdir(outputDirectory)
    TOPSTables = list(filter(lambda x: re.match(r"OP:\d+", os.path.basename(x)),
                             dirContents))
    tableSummaries = list()
    OPALTables = list()
    formatedTables = list()

    pContents = parse_abundance_map(aMap)

    # For each file put together the relevant information in a dictionary
    #  which will latter be merged and written to disk
    paths = map(lambda x: os.path.join(outputDirectory, x), TOPSTables)

    upperNonRect = (load_non_rect_map() if nonRect else None)

    sortedPaths = sorted(
            paths,
            key=lambda x: int(re.findall(r'(?:OP:)(\d+)',x)[0])
            )

    for i, tablePath in tqdm(enumerate(sortedPaths), total=len(TOPSTables),
                             desc="Building content dictionary"):
        comp = pContents[i]

        summary, X, Y, Z, table, *raw = format_TOPS_to_OPAL(
                tablePath,
                comp,
                i
                )

        tableSummaries.append(summary)
        OPALTables.append(table)
        formatedTables.append({
            "X":X,
            "Y":Y,
            "Z":Z,
            "Summary":summary,
            "Table":table,
            "LogRMO": raw[2],
            "LogR": raw[0],
            "LogT": raw[1]
            })

    KappaT = np.array(list(map(lambda x: x['LogRMO'], formatedTables)))
    interpFormatedTables = rebuild_formated_tables(formatedTables,
                                                   KappaT,
                                                   pContents,
                                                   upperNonRect,
                                                   nonRect=nonRect)

    # Get the solar composition for use in the header
    template_compList, X, Y, Z = get_base_composition(aTable)
    compDict = comp_list_2_dict(template_compList)
    # Write all the tables to one file in the proper format
    with open(output, 'w') as f:
        f.write(format_OPAL_table(interpFormatedTables, compDict))

