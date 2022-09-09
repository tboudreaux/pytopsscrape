"""
**Author:** Thomas M. Boudreaux\n
**Created:** September 2021\n
**Last Modified:** September 2022

Psuedo API for querying TOPS webform
"""

from pyTOPSScrape.api.utils import format_TOPS_string
from pyTOPSScrape.parse import parse_abundance_map
from pyTOPSScrape.parse import open_and_parse

from tqdm import tqdm

from concurrent.futures import ThreadPoolExecutor
from concurrent import futures

from bs4 import BeautifulSoup
import mechanize

from typing import TextIO
import numpy as np

TOPS_URL = "https://aphysics2.lanl.gov/apps/"

def submit_TOPS_form(
        mixString: str,
        mixName:str,
        massFrac: bool=True
        ) -> bytes:
    """
    Open the Los Alamos opacity website, submit a given composition and then
    return the resultant table.

    Parameters
    ----------
        mixString : string
            string in the form of: "massFrac0 Element0 massFrac1 Element1 ..."
            which will be submitted in the webform for mixture
        mixName : string
            name to be used in the webform

        massFrac : bool, default=True
            Submit as massFrac instead of numberFrac

    Returns
    -------
        tableHTML : bytes
            Table quired from TOPS cite.

    """
    br = mechanize.Browser()
    br.open(TOPS_URL)
    br.select_form(nr=0)
    if massFrac:
        br.form.find_control(name="fractype").value = ['mass']
    br.form['mixture'] = mixString
    br.form['mixname'] = mixName

    tlow = br.find_control(name="tlow", type="select").get("0.0005")
    tlow.selected = True
    tup = br.find_control(name="tup", type="select").get("60")
    tup.selected = True


    # These are the lowest and highest densities DSEP should need based
    #  on R = rho/T_6^3
    br.form['rlow'] = "1.77827941e-15"
    br.form['rup'] = "1.0e7"
    br.form['nr'] = '100'


    # get to the first submission page
    r1 = br.submit()

    # get to the second submission page
    br.select_form(nr=0)
    r2 = br.submit()

    tableHTML = r2.read()
    br.close()
    return tableHTML

def TOPS_query(mixString: str, mixName: str, nAttempts: int) -> bytes:
    """
    Query TOPS form and retry n times

    Parameters
    ----------
        mixString : string
            string in the form of: "massFrac0 Element0 massFrac1 Element1 ..."
            which will be submitted in the webform for mixture
        mixName : string
            name to be used in the webform
        nAttemptes : int
            How many times to reattempt after a failure.

    Returns
    -------
        tableHTML : bytes
            Table queried from TOPS cite.

    """
    attempts = 0
    while attempts < nAttempts:
        try:
            tableHTML = submit_TOPS_form(mixString, mixName)
            break
        except mechanize.HTTPError as e:
            attempts += 1
            print(f"Unable to Query TOPS form for {mixName} "
                  f". Attempt number {attempts} of "
                  f"{nAttempts}")
            print(e)
    else:
        print(f"Unable to query TOPS form for {mixName}. Skipping!")
    return tableHTML


def query_and_parse(compList : list, outputDirectory: int, i: int, nAttempts: int=10):
    """
    Async coroutine to query TOPS webform, parse the output, and write that
    to disk.

    Parameters
    ----------
        comList : list
            3D list containing the mass frac for each element for each rescaled
            composition requested. For n compositions this should be of the shape
            (n, 30, 2). n compositions, 30 elements, then the first element of 
            the last axis is the elemental symbol (i.e. H, He, Li, Be, etc...)
            and the second element is the mass fraction.
        outputDirectory : str
            Path to write out results of TOPS webquery
        i : int
            Index of composition so file name can properly keep track of where
            it is, even in parallel processing.
        nAttempts : int, default=10
            Number of time to retry TOPS query before failing out
    """
    mixString = format_TOPS_string(compList)
    X = compList[0][1]
    Y = compList[1][1]
    Z = sum([x[1] for x in compList[2:]])
    Xfmt = (int(X*1000) if int(X*1000) > 0 else 0)
    Yfmt = (int(Y*1000) if int(Y*1000) > 0 else 0)
    Zfmt = (int(Z*1000) if int(Z*1000) > 0 else 0)
    mixName = f"X{Xfmt} Y{Yfmt} Z{Zfmt}"
    continuity = sum([x[1] for x in compList])

    assert 1 - continuity <= 1e-3

    tableHTML = TOPS_query(mixString, mixName, nAttempts)

    table = parse_table(tableHTML)

    filePath = f"{outputDirectory}/OP:{i}_{X}_{Y}_{Z}.dat"
    return (table, filePath)

def TOPS_query_async_distributor(compList : list, outputDirectory : str, njobs : int = 10):
    """
    Distributes TOPS query jobs to different threads and gathers the results
    together. Writes out output.

    Parameters
    ----------
        comList : list
            3D list containing the mass frac for each element for each rescaled
            composition requested. For n compositions this should be of the shape
            (n, 30, 2). n compositions, 30 elements, then the first element of 
            the last axis is the elemental symbol (i.e. H, He, Li, Be, etc...)
            and the second element is the mass fraction.
        outputDirectory : str
            Path to directory to save TOPS query results to.
        njobs : int, default=10
            Number of concurrent jobs to allow at a time.
    """
    with tqdm(total=len(compList), desc=f"Querying on {njobs} threads") as pbar:
        with ThreadPoolExecutor(njobs) as executor:
            jobs = list()
            results = list()
            for i, subComp in enumerate(compList):
                jobs.append(executor.submit(query_and_parse, subComp, outputDirectory, i))
            for job in futures.as_completed(jobs):
                results.append(job.result())
                pbar.update(1)

    for table, filePath in tqdm(results, desc="Writing Query Results to Disk"):
        with open(filePath, 'w') as f:
            f.write(table)
            f.flush()


def parse_table(
        html: bytes
        ) -> str:
    """
    Parse the bytes table returned from mechanize into a string

    Parameters
    ----------
        html : bytes
            bytes table retuend from mechanize bowser at second TOPS submission
            form

    Returns
    -------
        table : string
            parsed html soruce in the form of a string
    """
    soup = BeautifulSoup(html, 'html.parser')

    # deal with line breaks
    table = soup.find('code').prettify().replace('<br/>', '')
    table = table.split('\n')

    # cut out the top and bottom lines of the table which dont matter
    table = [x for x in table[1:-2] if x.lstrip().rstrip() != '']

    # recombine the table into one string
    table = '\n'.join(table)
    return table

def call(aMap: str, aTable: str, outputDir: str, jobs: int):
    """
    Main TOPS psuedo API call function. Will save results to outputDir with
    file format OP:IDX_X_Y_Z.dat where IDX is the ID of the composition (parallel
    to DSEP composition ID), X is the classical Hydrogen mass fraction, Y  is
    the classical Helium mass fraction, and Z is the classical metal mass
    fraction.

    Parameters
    ----------
        aMap : str
            Path to the list of classical compositions to be used. List should
            be given as an ascii file where ecach row is X,Y,Z
        aTable : str
            Path to chemical abundance table to be used as base composition.
        outputDir : str
            Path to directory save TOPS query results into
        jobs : int
            Number of threads to query TOPS webform on

    Examples
    --------
    If you have some map of rescalings you would like to used at
    "./rescalings.dat" and you have a base composition in the correct form at
    "./comp.dat" then you can generate and cache the raw output for those rescalings of that composition using

    >>> call("./rescalings.dat", "./comp.dat", "./cache", 5)

    This will save the cache results to the folder ./cache (note that this
    folder must exist before calling call. Moreover, this will query using 5
    workers. You may increase this number to make call run faster; however,
    this will only work to a point. I find that around 20 workes is about the
    most that gives me any speed increase. This will somewhat depend on your
    computer though.
    """
    parsed = open_and_parse(aTable)
    pContents = parse_abundance_map(aMap)
    compList = list()
    for comp in pContents:
        zScale = comp[2]/parsed['AbundanceRatio']['Z']
        subComp = [
                ('H', comp[0]),
                ('He', comp[1])
                  ]
        for sym, data in parsed['RelativeAbundance'].items():
            if sym != 'H' and sym != 'He':
                subComp.append((sym, zScale * data['m_f']))

        compList.append(subComp)

    TOPS_query_async_distributor(compList, outputDir, njobs=jobs)


