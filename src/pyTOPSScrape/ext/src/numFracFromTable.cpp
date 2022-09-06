#include<iostream>
#include<fstream>
#include<string>
#include<vector>
#include<sstream>
#include<iterator>
#include<map>
#include<math.h>
#include<limits>
#include<ctype.h>
#include<stdio.h>
#include<cstring>

#include"boost/format.hpp"


#include<Python.h>

using namespace std;

typedef struct mfrac{
	float X;
	float Y;
} mfrac;


/* linspace
 *
 * Desc: simple implimentation of matlabs linspace function
 *       for floats. Will generate a vector of floats from 
 *       start (inclusive) to end (non inclusive) with a 
 *       total of num elements.
 * Params:
 * 		 start - (float) start value
 * 		 end - (float) end value
 * 		 num - (int) number of elements
 * Returns:
 * 	     vector<float> running from start (inclusive) to
 * 	     end (non-inclusive)
 */
vector<float> linspace(float start, float end, int num);

/* parse_dat_file
 *
 * Desc: Given some path to a datafile for atmospheric boundary conditions
 *       which is formated correctly, parse that to a list of elemental
 *       abundances
 * Params:
 *       filename - (&string) path to file to open
 *       parsedData - (&vector<float>) vector to store results in
 * Returns:
 * 	     Y - (float) Initial Heliumn Mass Fraction
 * Pre-state:
 *       some vector<float> must be initialized
 * Post-state:
 * 	     vectot<float> &parsedData filled with elemental abundances
 */
mfrac parse_dat_file(const string& filename, vector<float> &parsedData);

/* parse_line
 *
 * Desc: given some line of floats seperated by white space
 *       fill a vector of floats with each float.
 * Params:
 * 		 line - (&string) line to parse
 *		 lineContent - (&vector<float>) vector to store results in
 * Returns:
 * 	     void
 * Pre-state:
 *       some vector<float> must be initialized
 * Post-state:
 * 	     vectot<float> &lineContent filled with every white space delimited
 * 	     			   float on line
 */
void parse_line(const string& line, vector<float> &lineContent);

/* alpha_enhance
 *
 * Desc: add given AlphaFe to alpha elements
 * Params: 
 * 		 AlphaFe - (float) [Alpha/Fe] value
 * 		 abundances - (vector<float>) elemental abundances
 * Returns:
 * 		 void
 * Pre-state:
 *  	 some vector<float> has been initialized and filled with
 *  	 elemental abundances
 * Post-state:
 *		 vector<float> &abundances has had indicies 7, 9, 11, 15, 19,
 *		 21, 24 equal to their initial value + AlphaFe	
 */
void alpha_enhance(float AlphaFe, vector<float> &abundances);

/* feh_enhance
 *
 * Desc: add given [Fe/H] to all elemets above He
 * Params: 
 * 		 FeH - (float) [Fe/H] value
 * 		 abundances - (vector<float>) elemental abundances
 * Returns:
 * 		 void
 * Pre-state:
 *  	 some vector<float> has been initialized and filled with
 *  	 elemental abundances
 * Post-state:
 *		 vector<float> &abundances has every element set to self+FeH
 */
void feh_enhance(float FeH, vector<float> &abundances);


/* in_arr
 *
 * Desc: Is element x in array a
 * Params: 
 * 		 x - (string) element to check
 * 		 a - (* string) array to check against
 * 		 n - (int) size of array a
 * Returns:
 * 		 bool - (True) if x in a
 * 		      - (False) if x is not in a
 */
bool in_arr(string x, string *a, int n);

extern "C" void free_str(char* str);

char* run(const char* fnamei_p, float FeHi, float FeHf, int FeHN, float AlphaFei, float AlphaFef, int AlphaFeN, float aHei, float aHef, int aHeN, bool def, float ah, float Xc, float Yc);

static PyObject* method_numFrac(PyObject* self, PyObject* args);

int main(){
	return 0;
}
// Function Definitions
static PyMethodDef numfracMethods[] = {
    {"C_run", method_numFrac,
      METH_VARARGS,
      "Fast C++ based number fraction generation" },
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef numfracModule = {
    PyModuleDef_HEAD_INIT,
    "numfrac",
      "Fast C++ based number fraction generation" ,
    -1,
    numfracMethods
};

PyMODINIT_FUNC PyInit_numfrac(void) {
    return PyModule_Create(&numfracModule);
}

static PyObject* method_numFrac(PyObject* self, PyObject* args){
	char* fnamei_p;
	float FeHi, FeHf, AlphaFei, AlphaFef, aHei, aHef, ah, Xc, Yc;
	int FeHN, AlphaFeN, aHeN;
	bool def;

	if(!PyArg_ParseTuple(args, "sffiffiffipfff", &fnamei_p, &FeHi, &FeHf, &FeHN,
						 &AlphaFei, &AlphaFef, &AlphaFeN, &aHei, &aHef, &aHeN,
						 &def, &ah, &Xc, &Yc)){
		return NULL;
	}

	PyObject* outStr_P;
	char* outStr_C;

	outStr_C = run(fnamei_p, FeHi, FeHf, FeHN, AlphaFei, AlphaFef, AlphaFeN,
			aHei, aHef, aHeN, def, ah, Xc, Yc);
	outStr_P = PyUnicode_FromString(outStr_C);
	return outStr_P;
}

char* run(const char* fnamei_p, float FeHi, float FeHf, int FeHN, float AlphaFei, float AlphaFef, int AlphaFeN, float aHei, float aHef, int aHeN, bool def, float ah, float Xc, float Yc){
	string filename(fnamei_p);

	ostringstream out;

	vector<float> abundances;
	// The masses and symbols for every element in the tables provided
	// by greg
	float Mass[92] = { 1.008, 4.002602, 6.94, 9.0121831, 10.81, 12.011,
					   14.007, 15.999, 18.998403163, 20.1797, 22.98976928,
					   24.305, 26.9815385, 28.085, 30.973761998, 32.06,
					   35.45, 39.948, 39.0983, 40.078, 44.955908, 47.867,
					   50.9415, 51.9961, 54.938044, 55.845, 58.933194,
					   58.6934, 63.546, 65.38, 69.723, 72.63, 74.921595,
					   78.971, 79.904, 83.798, 85.4678, 87.62, 88.90584,
					   91.224, 92.90637, 95.95, 97.90721, 101.07, 102.9055,
					   106.42, 107.8682, 112.414, 114.818, 118.71, 121.76,
					   127.6, 126.90447, 131.293, 132.90545196, 137.327,
					   138.90547, 140.116, 140.90766, 144.242, 144.91276,
					   150.36, 151.964, 157.25, 158.92535, 162.5, 164.93033,
					   167.259, 168.93422, 173.045, 174.9668, 178.49,
					   180.94788, 183.84, 186.207, 190.23, 192.217, 195.084,
					   196.966569, 200.592, 204.38, 207.2, 208.9804, 209.0,
					   210.0, 222.0, 223.0, 226.0, 227.0, 232.0377,
					   231.03588, 238.02891 }; 
	// All of the elements tracked by the composition tables
	string Symbols[92] = { "H", "He", "Li", "Be", "B", "C", "N", "O", "F",
						   "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl",
						   "Ar", "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn",
						   "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As",
						   "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr", "Nb",
						   "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In",
						   "Sn", "Sb", "Te", "I", "Xe", "Cs", "Ba", "La",
						   "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb",
						   "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta",
						   "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl",
						   "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac",
						   "Th", "Pa", "U"};
	// Elements which will be written out to the numFrac file
	string targetSymbols[23] = {"H", "He", "C", "N", "O", "Ne", "Na", "Mg",
								"Al", "Si", "P", "S", "Cl", "Ar", "Ca",
								"Ti", "Cr", "Mn", "Fe", "Ni", "Li", "Be",
								"B"};
	
	mfrac iM = parse_dat_file(filename,abundances); 

	int nE = abundances.size();
	float cln, errsum, sum, sum1, sumam, sumz;
	float b[nE], b1[nE], a[nE];
	vector<float> FeH, AlphaFe, aHe;
	vector<float> new_(abundances.size());
	
	if (def == true){
		FeH = linspace(0.0, 0.0, 1);
		AlphaFe = linspace(0.0, 0.0, 1);
		aHe = linspace(abundances.at(1), abundances.at(1), 1);	
	} else{
		FeH = linspace(FeHi, FeHf, FeHN);
		AlphaFe = linspace(AlphaFei, AlphaFef, AlphaFeN);
		aHe = linspace(aHei, aHef, aHeN);
	}
	// Reimplimentation of numFrac programs, matches most of the output so
	// that the same parsing code may be used
	// N.B. -> Currently the error calculations are not included as the 
	// table from greg don't have an error dimension 
	double tmpVar;
	sum1 = 0;
	for (vector<float>::iterator feh = FeH.begin(); feh != FeH.end(); feh++){
		for (vector<float>::iterator alphafe = AlphaFe.begin(); alphafe != AlphaFe.end(); alphafe++){
			for(vector<float>::iterator ahe = aHe.begin(); ahe != aHe.end(); ahe++){
				sum1 = 0;
				copy(abundances.begin(), abundances.end(), new_.begin());

				new_.at(0) = ah;
				new_.at(1) = *ahe;
				feh_enhance(*feh, new_);
				alpha_enhance(*alphafe, new_);

				out << " Asplund: [Fe/H] = " << *feh << " [Alpha/Fe] = " << *alphafe;
				out << " a(He) = " << *ahe << endl;	

				
				sumz = 0.0e0;
				sum1 = 0.0e0;
				for (int i=0; i<nE; i++){
					a[i] = 0;
					if (in_arr(Symbols[i], targetSymbols, 23)){
						if (ah < -90){
							a[i] = ((Yc*Mass[i])/4.002602)*pow(10, new_.at(i)-abundances.at(1));
						}else{
							a[i] = ((Xc*Mass[i])/1.008)*pow(10, new_.at(i)-abundances.at(0));
						}
						// Handle the special case where X = 0
						if (a[i] > 1.0){
								a[i] = 1.0;
						}
						if (i > 2){
							sumz += a[i];
						}
						sum1 += a[i] * Mass[i];
					}
				}

				for (int i=0; i<nE; i++){
					if (in_arr(Symbols[i], targetSymbols, 23)){
						b1[i] = (a[i]*Mass[i])/sum1;
					}
				}

				out << " Number fractions" << endl;
				for (int i=0; i<nE; i++){
					if (in_arr(Symbols[i], targetSymbols, 23)){
						out << boost::format(" %-2s=   %.5E +/-   0.00E+00") % Symbols[i] % b1[i] << endl; 
					}
				}
				out << " Mass fractions" << endl;
				for (int i=0; i<nE; i++){
					if (in_arr(Symbols[i], targetSymbols, 23)){
						out << boost::format(" %-2s=   %.10E +/-   0.00E+00") % Symbols[i] % a[i] << endl;
					}
				}

				out << boost::format(" sumZ =  %.5E+/- 0.000E+00    %.5E+/- 0.000E+00") % sumz % (sumz/a[0]) << endl;
				out << " Z Mass fractions" << endl;
				for (int i=2; i<nE; i++){
					if (in_arr(Symbols[i], targetSymbols, 23)){
						out << boost::format(" %-2s=   %.10E +/-   0.00E+00") % Symbols[i] % (a[i]/sumz) << endl;

					}
				}
			}
		}
	}
	const string tmp = out.str();
	int size = tmp.size();
	const char* cstr = tmp.c_str();
	char *outStr = new char[4*size];
	strcpy(outStr, cstr);
	return outStr;
	
}

vector<float> linspace(float start, float end, int num){
	vector<float> linspaced;

	if (num == 0) { return linspaced; }
	if (num == 1) {
		linspaced.push_back(start);
		return linspaced;
	}
	float delta = (end - start) / (num - 1);
	for (int i=0; i < num - 1; ++i){
		linspaced.push_back(start+delta*i);
	}
	linspaced.push_back(end);

	return linspaced;
}


mfrac parse_dat_file(const string& filename, vector<float> &parsedData){
	string line;
	int linenum = 0;
	ifstream file (filename);
	vector<float> abundanceRatio;
	mfrac iM;
	if (file.is_open()){
		while (getline (file, line)){
			// Allow for comment lines and ignore short lines
			if (line.at(0) != '#' & linenum > 1){
				parse_line(line, parsedData);
			}
			else if (line.at(0) != '#' & linenum == 1){
				parse_line(line, abundanceRatio);
			}
			linenum ++;
		}
		
	}else{
		cerr << "Error! File " << filename << " Could Not be Opened!" << endl;
		throw 2;
	}
	
	iM.X = abundanceRatio.at(9);
	iM.Y = abundanceRatio.at(10);
	return iM;
}

void parse_line(const string& line, vector<float> &lineContents){
	istringstream iss(line);
	vector<string> tokens;
	// get each non white space charectar progressivly as a string
	copy(istream_iterator<string>(iss), istream_iterator<string>(), back_inserter(tokens));

	for (int i=0; i<tokens.size(); i++){
		// cout << (char)tokens.at(i).at(0) << endl;
		if (isalpha((char)tokens.at(i).at(0))){
			lineContents.push_back(0);
		} else{
			lineContents.push_back((float)stof(tokens.at(i)));
		}
		// lineContents.push_back((float)stof(tokens.at(i)));
	}

}

void alpha_enhance(float AlphaFe, vector<float> &abundances){
	abundances.at(7) += AlphaFe;
	abundances.at(9) += AlphaFe;
	abundances.at(11) += AlphaFe;
	abundances.at(15) += AlphaFe;
	abundances.at(19) += AlphaFe;
	abundances.at(21) += AlphaFe;
	abundances.at(24) -= AlphaFe;
}

void feh_enhance(float FeH, vector<float> &abundances){
	// Enhance every element
	// TODO: I think this needs to be changed to just element lighter than Iron.
	for (int i=5; i < abundances.size(); i++){
		abundances.at(i) += FeH;
	}
}

bool in_arr(string x, string *a, int n){
	bool found=false;
	for (int i=0; i<n; i++){
		if (a[i] == x) found=true;
	}
	return found;
}

extern "C" void free_str(char* ptr){
	delete []ptr;
}
