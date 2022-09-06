#!/bin/bash

# Generate GS98 opacity table using pyTOPSScrape assuming raw output has
# already been quieried and saved. This is intended to reduce the load on the
# LANL webservers by removing redundant accesses

# Using the already fetched results saved in the directory rawOutput generate 
# the OPAL table GS98.opac
generateTOPStables ./GS98.abun ./exampleAbunMap -d rawOutput -o GS98.opac --nofetch
