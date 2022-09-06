"""
**Author:** Thomas M. Boudreaux\n
**Created:** September 2021\n
**Last Modified:** September 2021

Psuedo API for querying TOPS webform
"""

from pyTOPSScrape.api.utils import format_TOPS_string
from pyTOPSScrape.parse.abundance import parse_abundance_map
from pyTOPSScrape.parse.abundance import gen_abun_map
from pyTOPSScrape.ext.utils import parse_numfrac_file
from pyTOPSScrape.ext.utils import call_num_frac

from tqdm import tqdm

from concurrent.futures import ThreadPoolExecutor
from concurrent import futures

from bs4 import BeautifulSoup
import mechanize

from typing import TextIO

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
            which will be sumbittedi in the webform for mixture
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
            which will be sumbittedi in the webform for mixture
        mixName : string
            name to be used in the webform
        nAttemptes : int
            How many times to reattempt after a failure.

    Returns
    -------
        tableHTML : bytes
            Table quired from TOPS cite.

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


def query_and_parse(file: TextIO, outputDirectory: int, i: int, nAttempts: int=10):
    """
    Async coroutine to query TOPS webform, parse the output, and write that
    to disk.

    Parameters
    ----------
        file : TextIO
            Abundance file to be parsed for the form as defined in the docstring
            for the function parse_numfrac_file
        outputDirectory : str
            Path to write out results of TOPS webquery
        i : int
            Index of composition so file name can properly keep track of where
            it is, even in parallel processing.
        nAttempts : int, default=10
            Number of time to retry TOPS query before failing out
    """
    compList, X, Y, Z = parse_numfrac_file(file, pbar=False)
    mixString = format_TOPS_string(compList)
    mixName = f"X{int(X*1000)} Y{int(Y*1000)} Z{int(Z*1000)}"

    tableHTML = TOPS_query(mixString, mixName, nAttempts)

    table = parse_table(tableHTML)

    filePath = f"{outputDirectory}/OP:{i}_{X}_{Y}_{Z}.dat"
    return (table, filePath)

def TOPS_query_async_distributor(aFiles, outputDirectory, njobs=10):
    """
    Distributes TOPS query jobs to different threads and gathers the results
    together. Writes out output.

    Parameters
    ----------
        aFiles : list of TextIO
            List of file like objects to abundance files to be parsed
        outputDirectory : str
            Path to directory to save TOPS query results to.
        njobs : int, default=10
            Number of concurrent jobs to allow at a time.
    """
    with tqdm(total=len(aFiles), desc=f"Querying on {njobs} threads") as pbar:
        with ThreadPoolExecutor(njobs) as executor:
            jobs = list()
            results = list()
            for i, file in enumerate(aFiles):
                jobs.append(executor.submit(query_and_parse, file, outputDirectory, i))
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
    """
    # Generate number fractions and save them to temporary files
    aMappingF = gen_abun_map(aTable)
    pContents = parse_abundance_map(aMap)
    aFiles = list()
    for i, abund in tqdm(enumerate(pContents), total=len(pContents),
                         desc="Generate FeH and Alpha/Fe"):
        res = aMappingF(abund[0], abund[1], abund[2])
        fp = call_num_frac(aTable, res[0], 0.0, res[2], abund[0], abund[1])
        aFiles.append(fp)
    # Using the number and mass fractions DSEP needs query the TOPS form
    #  for each and save its output
    TOPS_query_async_distributor(aFiles, outputDir, njobs=jobs)

    # Close all the temp files opened
    for file in aFiles:
        file.close()

