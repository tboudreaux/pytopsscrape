from pyTOPSScrape.api import call
from pyTOPSScrape.err import error_check
from pyTOPSScrape.api import TOPS_2_OPAL

import os

def full_run(kwargs : dict):
    """
    Main function to call all the right functions in order to get the TOPS
    formated ATOMIC opacity tables downloaded and converted to the proper
    format for dsep to understand.

    Parameters
    ----------
        kwargs : dict
            Dictionary containing all of the configuration information
            requiried for this function to run. This must include

                * abunTable (*str*)
                    Path of checmical abundance table to use for composition.
                * outputDirectory (*str*)
                    Directory to save results of numFrac executable to.
                * nofetch (*bool*)
                    If no fetch is true then the TOPS webform will not be
                    called. In this case all of the raw TOPS formated opacity
                    tables must have already been downloaded.
                * hardforce (*bool*)
                    Delete all existing directories that this function would
                    need. Use with caution. This has its own flag in an attempt
                    to mitigate server load on TOPS. Essentially the program
                    really tries to force you to not query TOPS if it detects
                    that the files have already been downloaded.
                * force (*bool*)
                    If true will allow program to refetch if not all the TOPS
                    files were downloaded (if the directory is not complete).
                    Will not overwride the TOPS directory if all of the files
                    were downloaded.
                * noopal (*bool*)
                    Flag whether or not to run the conversion of the TOPS
                    tables to OPAL/DSEP formated table. If opal is set True
                    this will happen, otherwise no conversion will take place.
                    If you set opal to falce and nofetch to true the program
                    will not do anything.
                * output (*str*)
                    Path to save DSEP/OPAL formated opacity table to.
                * jobs (*int*)
                    Number of threads to run TOPS query with
                * rect (*bool*)
                    Flag which controls whether or not to clip corners of OPAL
                    tables to put them into the non rectangular format DSEP
                    expects. If False then this will happen (output will be non
                    rectangular). If True then this will not happen (output
                    will be rectangular).
    Notes
    -----
        If there is an issue on the server end with TOPS this program will
        attempt to retry 10 times per composition by default (defined with the
        nAttepmts variable).
    """


    # you can set nofetch so you avoid the TOPS web query part if that was
    #  already done and you just want to reparse into a DSEP formated table
    #  already queried files.
    if not kwargs["nofetch"]:
        error_check(kwargs, 0)
        os.mkdir(kwargs["outputDirectory"])

        call(
                kwargs['abunMap'],
                kwargs['abunTable'],
                kwargs['outputDirectory'],
                kwargs['jobs']
            )

    # Convert the many files saved from the TOPS query to one file in the form
    #   DSEP expects. Mean to limit the number of calls to the LANL web server
    #   so that if the raw tables have already been quieried they do not need
    #   to be again.
    if not kwargs["noopal"]:
        error_check(kwargs, 1)

        TOPS_2_OPAL(
                kwargs['outputDirectory'],
                kwargs['abunTable'],
                kwargs['abunMap'],
                kwargs['output'],
                nonRect=not kwargs['rect']
                )
