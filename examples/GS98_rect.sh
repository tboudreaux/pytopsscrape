#!/bin/bash

# Generate GS98 opacity table using pyTOPSScrape

# DSEP uses non rectangular high temperature opacity tables. If you wish to save
# all the entries in the table use the --rect option to disable the non rectangular output

# Note that this example assumes that the raw tables have already been cached in the directory rawOutput
generateTOPStables ./GS98.abun ./exampleAbunMap -d rawOutput -o GS98.opac --nofetch --rect
