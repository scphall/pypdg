# pypdg
Python library containing Particle Data Group information

```
from pypdg import *
```
will import `particles`, `mass`, `width` and `life`, of all particles in the PDG (assuming they are got by my regexps, there are some special cases, which are dealt with).

The `particles` class inherits from `pandas.DataFrame` but with additional fucntionality to search for details with `particles.guess()`.  Classes `mass`, `width` and `life` are the same, but inherit from `pandas.Series`.

The `guess` method uses the [`fuzzywuzzy`](https://github.com/seatgeek/fuzzywuzzy) module if you have it, otherwise it uses basic string matching.

As well as the particle name adjusted from the LaTeX version in the PDG (so you can get particle using `particles['K*(892)0']`) you can do `particles.Kst_892_0`.
The rules used are as follows:

*  \* -> st
* _ -> ''
* (,) -> _
* \+ -> p
* \- -> m

for exapmple `D_2*(2460)+` goes to `D2st_2460_p`.

The `particles` class has all errors and asymmetries, but the other classes contain a `ufloat` for each particle (so contain errors).

If you are not sure of a particle name, you can use the `find()` method, which will output the best matches.


##Creating the database
There is a csv file in the module, which is all you need; but in case you want to recreate go into *make_dataset*, run the scripts:

* part1: gets the PDG website, takes ages,
* part2: greps the approriate pages and organizes data into something dealable with in python easily,
* part3: regexp etc. which turns data into a csv, move the resulting file into main directory.

The file *special_cases* contains info for other particles, for example the *K\*(892)<sup>0</sup>* has the same PDG page for the charged and neutral modes, so is dealt with separately.  There are not many examples of this.