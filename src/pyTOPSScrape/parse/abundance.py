"""
**Author:** Thomas M. Boudreaux\n
**Created:** May 2021\n
**Last Modified:** September 2022

Module responsible for the parsing and handeling of chemical composition files
in the form of

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

Where each number is a(i) for the ith element and lines starting with # are
comments.
"""

import re
import argparse
import numpy as np

from typing import Tuple

def mfrac_to_a(mfrac,amass,X,Y):
	"""
	Convert mass fracition of a given element to a for that element at a given
	hydrogen mass fraction using the equation

	.. math::

		a(i) = \\log(1.008) + \\log(F_{i}) - \\left[\\log(X) + \\log(m_{i}) \\right]

	Where :math:`F_{i}` is the mass fraction for the :math:`i^{th}` element and
	:math:`m_{i}` is the mass fraction for the :math:`i^{th}` element.

	Parameters
	----------
		mfrac : float
			Mass fraction of the ith element.
		amass : float
			Mass of the ith element in atomic mass units.
		X : float
			Hydrogen mass fraction
		Y : float
			Helium mass fraction, will be used as reference if X = 0

	Returns
	-------
		a : float
			a for the ith element
	"""
	if mfrac == 0:
		a = -99.99
	else:
		if X != 0:
			a = 12 + np.log(mfrac/(amass*(X/1.008)))/(np.log(2)+np.log(5))
		else:
			if Y == 0:
				raise ValueError("Error! X and Y cannot both be equal to 0!")
			a = 10.93 + np.log(mfrac/(amass*(Y/4.002602)))/(np.log(2)+np.log(5))

	return a

def a_to_mfrac(a,amass,X):
    """
    Convert :math:`a(i)` for the :math:`i^{th}` element to a mass fraction using the expression

    .. math::

        a(i) = \\log(1.008) + \\log(F_{i}) - \\left[\\log(X) + \\log(m_{i})\\right] + 12

    Or, equivilenetly, to go from :math:`a(i)` to mass fraction

    .. math::

        F_{i} = \\left[\\frac{X m_{i}}{1.008}\\right]\\times 10^{a(i)-12}

    Where :math:`F_{i}` is the mass fraction of the :math:`i^{th}` element,
    :math:`X` is the Hydrogen mass fraction, and :math:`m_{i}` is the ith
    element mass in hydrogen masses.

    Parameters
    ----------
        a : float
            :math:`a(i)` for the :math:`i^{th}` element. For example for He chem might
            be 10.93. For Hydrogen it would definititionally be 12.
        amass : float
            Mass of :math:`i^{th}` element given in atomic mass units.
        X : float
            Hydrogen mass fraction

    Returns
    -------
        mf : float
            Mass fraction of :math:`i^{th}` element.
    """
    mf = X*(amass/1.008)*10**(a-12)
    return mf

def get_atomic_masses():
    """
    Return a dict of atomic masses from Hydrogen all the way to plutonium

    Returns
    -------
        amasses : dict of floats
            Dicionary of atomic masses in atomic mass units indexed by elemental
            symbol.
    """
    amasses = {
        'H': 1.008,
        'He': 4.003,
        'Li': 6.941,
        'Be': 9.012,
        'B': 10.81,
        'C': 12.01,
        'N': 14.01,
        'O': 16.00,
        'F': 19.00,
        'Ne': 20.18,
        'Na': 22.99,
        'Mg': 24.31,
        'Al': 26.98,
        'Si': 28.09,
        'P': 30.97,
        'S': 32.07,
        'Cl': 35.45,
        'Ar': 39.95,
        'K': 39.10,
        'Ca': 40.08,
        'Sc': 44.96,
        'Ti': 47.87,
        'V': 50.94,
        'Cr': 52.00,
        'Mn': 54.94,
        'Fe': 55.85,
        'Co': 58.93,
        'Ni': 58.69,
        'Cu': 63.55,
        'Zn': 65.38,
        'Ga': 69.72,
        'Ge': 72.63,
        'As': 74.92,
        'Se': 78.97,
        'Br': 79.90,
        'Kr': 83.80,
        'Rb': 85.47,
        'Sr': 87.62,
        'Y': 88.91,
        'Zr': 91.22,
        'Nb': 92.91,
        'Mo': 95.95,
        'Tc': 98.00,
        'Ru': 101.1,
        'Rh': 102.9,
        'Pd': 106.4,
        'Ag': 107.9,
        'Cd': 112.4,
        'In': 1148,
        'Sn': 118.7,
        'Sb': 121.8,
        'Te': 127.6,
        'I': 126.9,
        'Xe': 131.3,
        'Cs': 132.9,
        'Ba': 137.3,
        'La': 138.6,
        'Ce': 140.1,
        'Pr': 149.9,
        'Nd': 144.2,
        'Pm': 145.0,
        'Sm': 150.4,
        'Eu': 152.0,
        'Gd': 157.3,
        'Tb': 158.9,
        'Dy': 162.5,
        'Ho': 164.9,
        'Er': 167.3,
        'Tm': 168.9,
        'Yb': 173.04,
        'Lu': 175.0,
        'Hf': 178.5,
        'Ta': 180.9,
        'W': 183.8,
        'Re': 186.2,
        'Os': 190.2,
        'Ir': 192.2,
        'Pt': 195.1,
        'Au': 197.0,
        'Hg': 200.6,
        'Tl': 204.4,
        'Pb': 207.2,
        'Bi': 209.0,
        'Po': 209,
        'At': 210,
        'Rn': 222,
        'Fr': 223,
        'Ra': 226,
        'Ac': 227,
        'Th': 232,
        'Pa': 231,
        'U': 238
    }
    return amasses

def parse_abundance_map(path : str) -> np.ndarray:
    """
    Parse Hydrogen, Helium, and metal mass fraction out of a csv where each row
    is one composition, the first column is X, second is Y, and the third is Z.
    Comments may be included in the file if the first non white space character
    on the line is a hash.

    Parameters
    ----------
        path : str
            Path to the abundance map. This should be an ascii file where each
            row contains X, Y, and Z (comma delimited with no white space).
            Each row will define one set of tables to be queried with the idea
            being that the entire file describes the entire set of tables to
            be queried.

    Returns
    -------
        pContents : np.ndarray(shape=(n,3))
            numpy array of all the compositions of length n where n is the
            number of rows whos first non white space character was not a hash.
            For a DSEP n=126. Along the second axis the first column is X, the
            second is Y, and the third is Z.

    """
    with open(path, 'r') as f:
        contents = f.read().split('\n')
        pContents = np.array([[float(y) for y in x.split(',')]
                               for x in contents
                              if x != '' and x.lstrip()[0] != '#'])
    return pContents


def parse(contents : list) -> dict:
    """
    Parse chem file in the format described in the module documentation.

    The abuundance ratios and abundances on the first row are added to a dict
    under the key ['AbundanceRatio'] and sub indexed by the comments above each
    entry (Note that these are not read; rather, they are assumed to be the
    same in every file). The subsequent values (on all other rows) are added to
    the same dict under the key ['RelativeAbundance'] and sub indexed by their
    chemical symbols.

    Parameters
    ----------
        contents : list
            List of list of strings. The outter index selects the row, the
            inner index selected the column in the row and at each coordinate
            is a string which can be cast as a float. The one exception is that
            string at 0,0 is a charectar.

    Returns
    -------
        extracted : dict
            Dictionary with two indexes.

                * Abundance Ratio
                    Includes the indexes:

                        - STD (*str*)
                        - [Fe/H] (*float*)
                        - [alpha/Fe] (*float*)
                        - [C/Fe] (*float*)
                        - [N/Fe] (*float*)
                        - [O/Fe] (*float*)
                        - [r/Fe] (*float*)
                        - [s/Fe] (*float*)
                        - C/O (*float*)
                        - X (*float*)
                        - Y (*float*)
                        - Z (*float*)

                * RelativeAbundance
                    Includes an index for each chemical symbol given in the
                    file format from the module documentation. These are all
                    floats.

    """
    contentMap = [
            [
                'STD',
                '[Fe/H]',
                '[alpha/Fe]',
                '[C/Fe]',
                '[N/Fe]',
                '[O/Fe]',
                '[r/Fe]',
                '[s/Fe]',
                'C/O',
                'X',
                'Y',
                'Z'
            ],
            [
                ('H', 1.008),
                ('He', 4.003),
                ('Li', 6.941),
                ('Be', 9.012),
                ('B', 10.81),
                ('C', 12.01),
                ('N', 14.01),
                ('O', 16.00),
                ('F', 19.00),
                ('Ne', 20.18)
            ],
            [
                ('Na', 22.99),
                ('Mg', 24.31),
                ('Al', 26.98),
                ('Si', 28.09),
                ('P', 30.97),
                ('S', 32.07),
                ('Cl', 35.45),
                ('Ar', 39.95),
                ('K', 39.10),
                ('Ca', 40.08)
            ],
            [
                ('Sc', 44.96),
                ('Ti', 47.87),
                ('V', 50.94),
                ('Cr', 52.00),
                ('Mn', 54.94),
                ('Fe', 55.85),
                ('Co', 58.93),
                ('Ni', 58.69),
                ('Cu', 63.55),
                ('Zn', 65.38)
            ],
            [
                ('Ga', 69.72),
                ('Ge', 72.63),
                ('As', 74.92),
                ('Se', 78.97),
                ('Br', 79.90),
                ('Kr', 83.80),
                ('Rb', 85.47),
                ('Sr', 87.62),
                ('Y', 88.91),
                ('Zr', 91.22)
            ],
            [
                ('Nb', 92.91),
                ('Mo', 95.95),
                ('Tc', 98.00),
                ('Ru', 101.1),
                ('Rh', 102.9),
                ('Pd', 106.4),
                ('Ag', 107.9),
                ('Cd', 112.4),
                ('In', 1148),
                ('Sn', 118.7)
            ],
            [
                ('Sb', 121.8),
                ('Te', 127.6),
                ('I', 126.9),
                ('Xe', 131.3),
                ('Cs', 132.9),
                ('Ba', 137.3),
                ('La', 138.6),
                ('Ce', 140.1),
                ('Pr', 149.9),
                ('Nd', 144.2)
            ],
            [
                ('Pm', 145.0),
                ('Sm', 150.4),
                ('Eu', 152.0),
                ('Gd', 157.3),
                ('Tb', 158.9),
                ('Dy', 162.5),
                ('Ho', 164.9),
                ('Er', 167.3),
                ('Tm', 168.9),
                ('Yb', 173.04)
            ],
            [
                ('Lu', 175.0),
                ('Hf', 178.5),
                ('Ta', 180.9),
                ('W', 183.8),
                ('Re', 186.2),
                ('Os', 190.2),
                ('Ir', 192.2),
                ('Pt', 195.1),
                ('Au', 197.0),
                ('Hg', 200.6)
            ],
            [
                ('Tl', 204.4),
                ('Pb', 207.2),
                ('Bi', 209.0),
                ('Po', 209),
                ('At', 210),
                ('Rn', 222),
                ('Fr', 223),
                ('Ra', 226),
                ('Ac', 227),
                ('Th', 232)
            ],
            [
                ('Pa', 231),
                ('U', 238)
            ]
        ]
    extracted = {'AbundanceRatio': dict(), 'RelativeAbundance': dict()}
    for rowID, (row,target) in enumerate(zip(contents, contentMap)):
        for colID, (element, targetElement) in enumerate(zip(row, target)):
            if rowID == 0:
                if colID != 0:
                    element = float(element)
                extracted['AbundanceRatio'][targetElement] = element
            else:
                element = float(element)
                extracted['RelativeAbundance'][targetElement[0]] = {"a": element,
                                               "m_f": a_to_mfrac(element,
                                                                 targetElement[1],
                                                                 extracted['AbundanceRatio']['X']
                                                                )
                                              }
    return extracted

def open_chm_file(path):
    """
    Open a chemical composition file (format defined in the module
    documentation). Split the contents by line then remove all lines which
    start with #. Finally split each line by both whitespace and commas.

    Parameters
    ----------
        path : str
            Path to file to open

    Returns
    -------
        contents : list
            List of list of strings. The outter index selects the row, the
            inner index selectes the column within the row.
    """
    with open(path, 'r') as f:
        contents = filter(lambda x: x != '', f.read().split('\n'))
        contents = filter(lambda x: x[0] != '#', contents)
    contents = [re.split(' |,', x) for x in contents]
    return contents

def open_and_parse(path):
    """
    Open and parse the contents of a chemical composition file

    Parameters
    ----------
        path : str
            Path to open file

    Returns
    -------
        parsed : dict
            Dictionary with two indexes.

                * Abundance Ratio
                    Includes the indexes:

                        - STD (*str*)
                        - [Fe/H] (*float*)
                        - [alpha/Fe] (*float*)
                        - [C/Fe] (*float*)
                        - [N/Fe] (*float*)
                        - [O/Fe] (*float*)
                        - [r/Fe] (*float*)
                        - [s/Fe] (*float*)
                        - C/O (*float*)
                        - X (*float*)
                        - Y (*float*)
                        - Z (*float*)

                * RelativeAbundance
                    Includes an index for each chemical symbol given in the
                    file format definition provided in the module
                    documentation. These are all floats.
    """
    contents = open_chm_file(path)
    parsed = parse(contents)
    return parsed

def get_base_composition(aTablePath : str) -> Tuple[list, float, float, float]:
    """
    For some abundance path return the "base" composition, this is mainly to be
    used for headers.

    Parameters
    ----------
        aTablePath : str
            Path to the abundance table in the form as described in the
            parseChemFile module documentation
    Returns
    -------
        list
            list of the composition in the form [('Element',massFrac,numberFrac),...]
        float
            Hydrogen mass fraction
        float
            Helium mass fraction
        float
            Metal mass fraction
    """
    aTable = open_and_parse(aTablePath)
    X = aTable['AbundanceRatio']['X']
    Y = aTable['AbundanceRatio']['Y']
    Z = aTable['AbundanceRatio']['Z']
    aHe = aTable['RelativeAbundance']['He']['a']
    aMasses = get_atomic_masses()

    norm = sum([
        data['m_f']/aMasses[sym]
        for sym, data in aTable['RelativeAbundance'].items()
        ])

    numFrac = lambda m_f, sym: (m_f/aMasses[sym])/norm

    compList = [
            (sym, data['m_f'], numFrac(data['m_f'], sym), data['m_f']/Z, 0, 0, 0)
            for sym, data in aTable['RelativeAbundance'].items()
               ]

    return compList, X, Y, Z



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse chemical abundance file")
    parser.add_argument("path", help="Path to chemical abundance file", type=str)

    args=parser.parse_args()
    contents = open_chm_file(args.path)
    extracted = parse(contents)
    print(extracted)



