# pypdg
Python library containing Particle Data Group information

```
from pypdg import *
```
will import all particles in the PDG (assuming they are got by my regexps, there are some special cases, which are dealt with) in the classes:

* `alldata` all data including latex names, but data is all strings
* `particles` add data, no latex names, data in floats
* `mass` mass data in floats
* `umass` mass data in ufloats (uncertainty floats)
* `life` life data in floats
* `ulife` life data in ufloats
* `width` width data in floats
* `uwidth` width data in ufloats

The `particles` class inherits from `pandas.DataFrame` but with additional fucntionality to search for details with `particles.guess()`.  Classes `(u)mass`, `(u)width` and `(u)life` are the same, but inherit from `pandas.Series`.

The `guess` method uses the [`fuzzywuzzy`](https://github.com/seatgeek/fuzzywuzzy) module if you have it, otherwise it uses basic string matching.

As well as the particle name adjusted from the LaTeX version in the PDG (so you can get particle using `particles['K*(892)0']`) you can do `particles.Kst_892_0`.
The rules used are as follows:

*  \* *to* st
* _ *to* ''
* () *to* _
* \+ *to* p
* \- *to* m

for exapmple `D_2*(2460)+` goes to `D2st_2460_p`.

If you are not sure of a particle name, you can use the `find()` method, which will output the best matches.

**UNITS are *MeV* and *s* **

##Creating the database
There is a csv file in the module, which is all you need; but in case you want to recreate go into *make_dataset*, run the scripts:

* part1: gets the PDG website, takes ages,
* part2: greps the approriate pages and organizes data into something dealable with in python easily,
* part3: regexp etc. which turns data into a csv, move the resulting file into main directory.

The file *special_cases* contains info for other particles, for example the *K\*(892)<sup>0</sup>* has the same PDG page for the charged and neutral modes, so is dealt with separately.  There are not many examples of this.
