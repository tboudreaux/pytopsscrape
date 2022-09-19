# pyTOPSScrape
### A tool for scraping OPLIB opacities from the TOPS web form and converting them into a format more similar to that used by OPAL
![Liscence](https://img.shields.io/github/license/tboudreaux/pyTOPSSCrape?style=for-the-badge) ![DOI](https://zenodo.org/badge/532559997.svg)

#### Documentation
This README provides a basic overview; however, more in depth documentation, including 
detailed descriptions of command line arguments and file formats may be found in
the following links

<a href="https://tboudreaux.github.io/pytopsscrape/">Official Documentation</a> (<a href="https://algebrist.com/~tboudreaux/docs/pyTOPSScrape/">mirror</a>)

<a href="https://raw.githubusercontent.com/tboudreaux/pytopsscrape/master/docs/build/latex/pytopsscrape.pdf">PDF Documentation</a>

#### Overview 
The <a href="https://aphysics2.lanl.gov/apps/">TOPS webform</a> provides access
to some of the most up to date high temperature radiative opacities. However,
entering compositions manually into a webpage can be a chore. Especially when
one needs opacities for a variety of rescaled compositions as is often the case
when working stellar evolution programs.

pyTOPSScrape aims to address this by providing a simple interface to query the
TOPS webform for n tables rescaled from a base composition. Moreover,
pyTOPSScrape can transform the parameterization of opacities from mass density
and temperature to R and temperature. Additionally, pyTOPSScrape will automatically
merge tables from rescaled compositions into a single table mimicking the form
of high temperature opacity tables already used by the Dartmouth Stellar
Evolution Program (DSEP).

The primary interface for pyTOPSScrape is a bash script included with the package
an example use of which follows

```bash
generateTOPStables GS98.abun rescalings.dat -d ./rawOutput -o GS98.opac -j 20
```

Further examples and the data files needed to run them may be found in the
examples directory of this repository.

In addition to this bash script pyTOPSScrape provides a programmatic interface
made up of primarily the pyTOPSScrape.api.call and pyTOPSScrape.api.TOPS_2_OPAL
functions. These can be called individually if you wish to implement your own
custom converter function (In that case you would use call and then some
custom function in place of TOPS_2_OPAL)


## Install

#### Prerequisites
<ul>
	<li>python >= 3.8</li>
	<li>mechanize >= 0.4.5</li>
	<li>scipy >= 1.5.2 </li>
	<li>tqdm >= 4.50.2 </li>
	<li>beautifulsoup4 >= 4.8.2 </li>
	<li>importlib_resources >= 5.2.0 </li>
</ul>

#### pip
If you install with pip all the dependencies should be automatically installed.
```bash
pip install pyTOPSScrape
```

#### Source
```bash
git clone https://github.com/tboudreaux/pytopsscrape.git
cd pytopsscrape
python setup.py install
```


## Current Potential Issues
There seem to be small variations in the results I get from the web form for
the same inputs between queries. I have yet to track down if this is on my end
of on there end but be aware of this. (This also makes some of the tests fail
as I am doing a character to character check and not a numeric similarity
within threshold check)

# Examples
There are examples of the command line interface and the python interface in
the examples directory of this repository. It is recommended you look at those
before querying your own opacity files. The command line examples are all shell
scripts with names that describe that they are examples of while the python
interface example is in the form of a Jupyter notebook in the
examples/Notebooks directory. If you do not have jupyter installed on your
computer you should be able to view the .ipynb file on Github.
