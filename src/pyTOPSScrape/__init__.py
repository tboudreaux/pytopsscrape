"""
pyTOPSScrape
============
A package which aims to make the programatic retrieval and use of high
temperature radiative opacity tables from LANL somewhat simple

pyTOPSScrape provides both a command line and a python interface. The command
line interface runs through the generateTOPStables script (which will have been
installed to your path when you installed this package)

The python interface can mimic the full command line interface (including error
checking and rate limiting) using the full_run function. If however, you wish
to dig down to a more granular level the api module includes both query and
convert submodules which may be composed as needed.

Installation
============
PyPi
----

>>> pip install pyTOPSScrape

GitHub
------

>>> git clone git@github.com:tboudreaux/pytopsscrape.git
>>> cd pytopsscrape
>>> python setup.py install

Command Line Usage Example
----------------------------
>>> generateTOPStables GS98.abun rescalings.dat -d ./rawOutput -o GS98.opac -j 20


Input File Formats
==================
pyTOPSScrape requires two input files to run. One (the first positional
argument and hereafter the 'composition file') describes the base composition.
The second positional argument (hereafter the 'map file') describes the set of
classical compositions which will be queried from the TOPS web form. Each of
these compositions will be a rescaling of the base composition (therefore the
metal mass fractions wrt. Z will be maintained)

Composition file
----------------
The composition file should be in the following form

::

    #STD [Fe/H] [alpha/Fe] [C/Fe] [N/Fe] [O/Fe] [r/Fe] [s/Fe] C/O X Y,Z
    F -1.13 0.32 -0.43 -0.28 0.31 -1.13 -1.13 0.10 0.7584 0.2400,1.599E-03
    #H He Li Be B C N O F Ne
    12.00 10.898 -0.08 0.25 1.57 6.87 6.42 7.87 3.43 7.12
    #Na Mg Al Si P S Cl Ar K Ca
    5.11 6.86 5.21 6.65 4.28 6.31 -1.13 5.59 3.90 5.21
    #Sc Ti V Cr Mn Fe Co Ni Cu Zn
    2.02 3.82 2.80 4.51 4.30 6.37 3.86 5.09 3.06 2.30
    #Ga Ge As Se Br Kr Rb Sr Y Zr
    0.78 1.39 0.04 1.08 0.28 0.99 0.26 0.61 1.08 1.45
    #Nb Mo Tc Ru Rh Pd Ag Cd In Sn
    -0.80 -0.38 -99.00 -0.51 -1.35 -0.69 -1.32 -0.55 -1.46 -0.22
    #Sb Te I Xe Cs Ba La Ce Pr Nd
    -1.25 -0.08 -0.71 -0.02 -1.18 1.05 -0.03 0.45 -1.54 0.29
    #Pm Sm Eu Gd Tb Dy Ho Er Tm Yb
    -99.00 -1.30 -0.61 -1.19 -1.96 -1.16 -1.78 -1.34 -2.16 -1.42
    #Lu Hf Ta W Re Os Ir Pt Au Hg
    -2.16 -1.41 -2.38 -1.41 -2.00 -0.86 -0.88 -0.64 -1.34 -1.09
    #Tl Pb Bi Po At Rn Fr Ra Ac Th
    -1.36 -0.51 -1.61 -99.00 -99.00 -99.00 -99.00 -99.00 -99.00 -2.20
    #Pa U
    -99.00 -2.80

Map file
--------
The map file should be in the following form

::

    0.75,0.24,0.01
    0.75,0.23,0.02

Where each row is X,Y,Z. The number of rows in this file will correspond to the
number of queries issued against the TOPS web form

Testing
=======
pyTOPSScrape ships with a number of tests which should be run to make sure that
it installed correctly on your system. Additionally, as it is reliant on an
external server it is a certainty that one day it will break. To run the tests
a script has been included. From the pyTOPSScrape root directory

>>> cd tests
>>> ./runTests.sh

Etiquette & Cacheing
====================
pyTOPSScrape makes use web servers hosted at Los Alamos National Labs (LANL).
Before releasing this software I spoke with the T-1 group at LANL and received
their assent. However, try to limit requests made against their web servers as
much as possible. Obviously, if you are querying  a few hundred tables because
your stellar evolution code needs a few hundred opacity tables there is little
to be done; however, do try and make sure that you have sorted out any and all
bugs or typos in your input files before you query so that you won't have to go
back and query multiple times. We want to be respectful of of the generosity of
LANL here!

Additionally, pyTOPSScrape caches the raw query results to whatever directory
is specified by the -d or --outputDirectory flag. This is so that if you want
to implement your own converted you can do so without constantly re running the
query functions. These results are cached in whatever directory is set in the
--outputDirectory (or -d) command line option. To call the command line
interface with cache usage enabled use the --nofetch flag. If you want to fetch
tables and don't want to run the conversion set use the no opal flag.

As an example, if you have already queried the TOPS web form using the command 

>>> generateTOPStables GS98.abun rescalings.dat -d ./rawOutput -o GS98.opac -j 20 --noopal

this will save all the raw output to the directory ./rawOutput (if you run the
first example from this docs page this will also cache the results). You can
then convert these to DSEP's OPAL format using the command

>>> generateTOPStables GS98.abun rescalings.dat -d ./rawOutput -o GS98.opac -j 20 --nofetch
"""
from pyTOPSScrape.scripts.main import full_run
