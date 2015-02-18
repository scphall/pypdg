################################################################################
import pandas
import os
from uncertainties import ufloat
################################################################################
__author__ = 'Sam Hall'
__all__ = ['particles', 'mass', 'life', 'width']
################################################################################

_FUZZ_ERROR_MESSAGE = False
_ALIASES = {
    'K*' : 'K*(892)0',
    'Kst' : 'K*(892)0',
    'rho' : 'rho(770)0',
}
################################################################################

def _fuzzy_match(s1, s2):
    '''Fuzzy string matching if fuzzywuzzy is not available'''
    import string
    def normalize(s):
        for p in string.punctuation:
            s = s.replace(p, '')
        return s.lower().strip()
    return normalize(s1) == normalize(s2)


################################################################################
def _guess_list(self, n):
    '''Guess what particle is interesting and return the relevant object'''
    try:
        from fuzzywuzzy import fuzz
        tpls = [(k, fuzz.ratio(n, k)) for k in self.keys()]
        tpls = sorted(tpls, key=lambda x:x[1], reverse=True)
        return tpls
    except ImportError:
        global _FUZZ_ERROR_MESSAGE
        if not _FUZZ_ERROR_MESSAGE:
            print 'For better particle finding install fuzzywuzzy'
            print ' https://github.com/seatgeek/fuzzywuzzy'
        _FUZZ_ERROR_MESSAGE = True
        tpls = [(k, _fuzzy_match(n, k)) for k in self.keys()]
        tpls = [x for x in tpls if x[1]]
        return tpls


################################################################################
def _guess(self, n):
    '''Guess what particle is interesting and return the relevant object'''
    tpls = _guess_list(self, n)
    if len(tpls) > 10:
        if tpls[0][1]<60:
            raise IndexError(
                '''
                Cannot guess reliably from {}
                Best guesses are {} and {}
                '''.format(n, *tpls))
            return self[tpls[0][0]]
    elif not len(tpls):
        raise IndexError(
            '''
            Cannot guess reliably from {}
            No guesses
            '''.format(n))
    elif len(tpls)>1:
        raise IndexError(
            '''
            Cannot guess reliably from {}
            Some guesses are {} and {}
            '''.format(n, *tpls))
    return self[tpls[0][0]]

################################################################################
class DetailErr(pandas.Series):
    def __init__(self, detail, df):
        details = {}
        for k, i in df.iteritems():
            details.update(
                {k : ufloat(df[k][detail], df[k]['{}err'.format(detail)])}
            )
            details.update(
                {df[k]['name'] : ufloat(df[k][detail], df[k]['{}err'.format(detail)])}
            )
        df = pandas.DataFrame.from_dict({'mass' :details})
        pandas.Series.__init__(self, df['mass'])
        return

    def guess(self, n):
        return _guess(self, n)


################################################################################
class Particles(pandas.DataFrame):
    def __init__(self, df):
        dfalias = pandas.DataFrame()
        for name in df:
            if name == df[name]['name']:
                continue
            dfalias[df[name]['name']] = df[name]
        pandas.DataFrame.__init__(self, df.join(dfalias))
        self.setaliases()
        self.allaliases()
        return

    def setaliases(self, aliases=_ALIASES):
        for new, old in aliases.iteritems():
            self[new] = self[old]
        return

    def allaliases(self):
        for k, i in self.iteritems():
            if k.endswith('pm'):
                self[k.replace('pm', 'p')] = i
                self[k.replace('pm', '+')] = i
                self[k.replace('pm', 'm')] = i
                self[k.replace('pm', '-')] = i
        return

    def guess(self, n):
        return _guess(self, n)

    def find(self, name, n=5):
        '''Fine name in database, best n matches in order'''
        return [x[0] for x in _guess_list(self, name)[:n]]


################################################################################
csvfile = 'pdg_particles.csv'
abscsvfile = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    csvfile
)
df = pandas.DataFrame.from_csv(abscsvfile)

particles = Particles(df)
mass = DetailErr('mass', particles)
life = DetailErr('life', particles)
width = DetailErr('width', particles)
################################################################################
