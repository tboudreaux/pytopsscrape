#!/bin/bash

# Generate GS98 opacity table using pyTOPSScrape

# Query the tops webform using 20 workers saving the raw output from the webform
# to files in the rawOutput directory. The final result will be saved to
# the file GS98.opac
generateTOPStables ./exampleDataFiles/GS98.abun ./exampleDataFiles/exampleAbunMap.dat -d MultiGroupOutput -o GS98.opac -j 5 --multi
