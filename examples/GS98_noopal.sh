#!/bin/bash

# Query raw tables from TOPS web form but do not do any conversion. This is
# intendent to allow other modification scripts to be used inplace of the
# inbuilt one (which was built with DSEP in mind and may therefore not be
# widley applicable)

# Query the tops webform using 20 workers saving the raw output from the webform
# to files in the rawOutput directory.
generateTOPStables ./exampleDataFiles/GS98.abun ./exampleDataFiles/exampleAbunMap.dat -d rawOutput -o GS98.opac -j 20 --noopal
