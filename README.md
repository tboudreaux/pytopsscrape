<h1> pyTOPSScrape </h1>
<h2> A tool for scrapign OPLIB opacities from the TOPS web form and converting
them into a format more similar to that used by OPAL </h2>

The <a href="https://aphysics2.lanl.gov/apps/">TOPS webform</a> provides access
to some of the most up to date high temperature radiative opacities. However,
entering compositions manually into a webpage can be a chore. Especially when
one needs opacities for a variety of rescaled compositions as is often the case
when working stellar evolution programs.

pyTOPSScrape aims to address this by providing a simple interfact to query the
TOPS webform for n tables rescaled from a base composition. Moreover,
pyTOPSScrape can transform the parameterization of opacities from mass density
and temperature to R and temperature. Additionally, pyTOPSScrape will automatically
merge tables from rescaled compositions into a single table mimicing the form
of high temperature opacity tables already used by the Dartmouth Stellar
Evolution Program (DSEP).

The primary interface for pyTOPSScrape is a bash script included with the package
an example use of which follows

```bash
generateTOPStables GS98.abun rescalings.dat -d ./rawOutput -o GS98.opac -j 20
```

In addition to this bash script pyTOPSScrape provides a programatic interface
made up of primarily the pyTOPSScrape.api.call and pyTOPSScrape.api.TOPS_2_OPAL
functions. These can be called indidually if you wish to impliment your own
custom converter function (In that case you would use call aand then some
custom function in place of TOPS_2_OPAL)


