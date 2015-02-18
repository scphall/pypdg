import pandas
from uncertainties import ufloat

df = pandas.DataFrame.from_csv('pypdg/pdg_particles.csv')

class _Detail(object):
    def __init__(self, detail, df):
        for d in df:
            setattr(self, d, df[d][detail])
        return

class _DetailErr(object):
    def __init__(self, detail, df):
        for d in df:
            setattr(self, d,
                    ufloat(df[d][detail], df[d]['{}err'.format(detail)]))
        return

class Particles(pandas.DataFrame):
    def __init__(self, *args, **kwargs):
        pandas.DataFrame.__init__(self, *args, **kwargs)
        self.mass = _DetailErr('mass', self)
        self.life = _DetailErr('life', self)
        for name in self:
            if name == self[name]['name']:
                continue
            print name, self[name]['name']
            setattr(self, self[name]['name'], self[name])
        return

particles = Particles(df)
