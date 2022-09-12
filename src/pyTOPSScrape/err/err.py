from pyTOPSScrape.api.utils import validate_extant_tables

import os
import shutil

def error_check(kwargs : dict, mode : int):
    """
    Basic error checking to run

    Parameters
    ----------
        kwargs : dict
            keyword argument dictionary used by main function
        mode : int
            Define error check mode.
                - 0 : web mode (check errors for TOPS erb query)
                - 1 : opal mode (convert tops to opal format)

    Raises
    ------
        OSError
            If all of the TOPS files have been verrified as downloaded and the
            force flag has been set.
        OSError
            If all of the TOPS files have not been verified but some have
            downloaded and the force flag has not been set
        OSError
            If all of the TOPS files have be verified and the force flag has
            not been set.
        OSError
            If opal has been set but the TOPS files are unable to be validated.
    """
    if mode == 0:
        # Some defined excetions
        # if the directory exists, and the force flag is set, but the TOPS
        #  files have not been fully quiered go aheead and allow the code to
        #  continue buy removing the direcotory and starting over
        if (kwargs["hardforce"]):
            if os.path.exists(kwargs["outputDirectory"]):
                shutil.rmtree(kwargs["outputDirectory"])
        elif (
                os.path.exists(kwargs["outputDirectory"])
                and kwargs["force"]
                and not validate_extant_tables(kwargs["outputDirectory"],
                                               "PLACEHOLDER")
             ):
            shutil.rmtree(kwargs["outputDirectory"])
        # If the directory exists an the force flag is set and all the TOPS
        #  files have been quired prevent the code from running. This is to
        #  keep the traffic on the tops site down. If you need to run again
        #  manually delete the folder. i.e. no way to programtically
        #  overwride this
        if (
                os.path.exists(kwargs["outputDirectory"])
                and kwargs["force"]
                and validate_extant_tables(kwargs["outputDirectory"], "PLACEHOLDER")
                and not kwargs["hardforce"]
           ):
            raise OSError(f"Cannot force override of {kwargs['outputDirectory']} as"
                            " it has been validated as complete")
        # If the directory exists, and is not validated, but the force flag is
        #  not set alert the user the directory will not be overwritten if the
        #  force flag is not set
        elif (
                not kwargs["force"]
                and os.path.exists(kwargs["outputDirectory"])
                and not validate_extant_tables(kwargs["outputDirectory"],
                                               "PLACEHOLDER")
             ):
            raise OSError(f"Output dir {kwargs['outputDirectory']} exists, you can"
                           " force this path to be overwritten with the"
                           " -f/--force flag")

        # if the path exists, the path is validate, and the force flag is not
        #  set, let the user know to run with nofetch and opal to skip this
        #  stage entirly
        elif (
                not kwargs["force"]
                and os.path.exists(kwargs["outputDirectory"])
                and validate_extant_tables(kwargs["outputDirectory"], "PLACEHOLDER")
             ):
            raise OSError(f"Output dir {kwargs['outputDirectory']} already exists"
                           " and is validated as complete, set the --nofetch "
                           "flag to skip the TOPS fetch portion of the program "
                           "(This assues that the raw TOPS files have in fact "
                           "already been cached in the outputDirectory). If "
                           "you are sure that this is in error its likely the "
                           "outputDirectory was made on a previous run. You "
                           "can either delete this directory or use the "
                           "--hardforce flag to force the program to run.")
    elif mode == 1:
        # A defined execption
        # If the directory exists but the TOPS files cannot be validated halt
        if not validate_extant_tables(kwargs["outputDirectory"], "PLACEHOLDER"):
            raise OSError(f"Unable to validate quality of TOPS opacity tables"
                           " in {kwargs['outputDirectory']}, run again without"
                           " --nofetch flag to refetch tables")
