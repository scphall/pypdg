#!/usr/bin/python
import re
import numpy as np
import pandas


class Particle(object):
    def __init__(self, name='{{'):
        if not name.startswith('{{'):
            raise ValueError('This is not a particle name')
        self.makenames(name)
        self.mass = {
            'mass' : -1, 'masserr' : -1,
            'masserrlow' : -1, 'masserrup' : -1,
            'masslimlow' : -1, 'masslimup' : -1,
        }
        self.tau = {
            'life' : -1, 'lifeerr' : -1,
            'lifeerrlow' : -1, 'lifeerrup' : -1,
        }
        self.width = {
            'width' : -1, 'widtherr' : -1,
            'widtherrlow' : -1, 'widtherrup' : -1,
        }
        return

    @staticmethod
    def isparticle(line):
        if line.startswith('{{'):
            return True
        return False

    def makenames(self, n):
        latex = n.rstrip('\n')
        name = re.sub(r'{|}|mathrm|mathit|wide|\\| |\^', '', latex)
        basicname = name.replace('*', 'st').replace(r'/', '')
        basicname = re.sub(r'_', '', basicname)
        basicname = basicname.replace('-', 'm').replace('+', '')
        basicname = basicname.replace(r"'", 'prime')
        basicname = re.sub(r'\(|\)', '_', basicname)
        self.names = {
            'latex' : latex,
            'name' : name,
            'basicname' : basicname
        }
        return

    def getmass(self, line):
        searchdict = re.search(r'\$(?P<mass>.*?)\$ (?P<units>[kMTG]?eV)?', line)
        if searchdict is None:
            return
        units = searchdict.groupdict()['units']
        mass = searchdict.groupdict()['mass'].replace(' ', '')
        if units is None:
            return
        if mass.count(r'\pm'):
            self.mass['mass'] = float(mass.split(r'\pm')[0])
            err = [float(x)**2 for x in mass.split(r'\pm')[1:]]
            err = np.sqrt(sum(err))
            self.mass['masserr'] = err
            self.mass['masserrlo'], self.mass['masserrup'] = err, err
        elif mass.count(r'>'):
            self.mass['masslimlow'] = float(mass.replace('>', ''))
        elif mass.count(r'<'):
            self.mass['masslimup'] = float(mass.replace('<', ''))
        else:
            search = re.search('(?P<m>[0-9\.]*)\^{\+(?P<up>.*)}_{-(?P<lo>.*)}', mass)
            if search is None:
                return
            mass = search.groupdict()
            self.mass['mass'] = mass['m']
            self.mass['masserrlo'] = float(mass['lo'])
            self.mass['masserrup'] = float(mass['up'])
            self.mass['masserr'] = np.sqrt(
                self.mass['masserrup']**2 + self.mass['masserrlo']**2
            ) / np.sqrt(2.)
        if units == 'MeV':
            return
        factor = {'eV':1e-6, 'keV':1e-3, 'GeV':1e3, 'TeV':1e6}[units]
        self.mass = {key : item*factor for key, item in self.mass.iteritems()}
        return

    def getlife(self, line):
        search = re.search('\$(.*?)\$', line)
        if search is None or line.count('eV'):
            return
            return
        tau = search.groups()[0].replace(' ', '')
        if tau.count('pm') and tau.count('times'):
            regexp = r'((?P<t>[0-9\.]+).*pm(?P<e>[0-9\.]+)).*times10\^{(?P<exp>.*)}'
            search = re.search(regexp, tau).groupdict()
            search = {key: float(item) for key, item in search.iteritems()}
            self.tau['life'] = search['t']*(10**search['exp'])
            self.tau['lifeerr'] = search['e']*(10**search['exp'])
            self.tau['lifeerrlow'] = self.tau['lifeerr']
            self.tau['lifeerrup'] = self.tau['lifeerr']
        elif tau.count('pm'):
            regexp = r'((?P<t>[0-9\.]+).*pm(?P<e>[0-9\.]+))'
            search = re.search(regexp, tau).groupdict()
            search = {key: float(item) for key, item in search.iteritems()}
            self.tau['life'] = search['t']
            self.tau['lifeerr'] = search['e']
            self.tau['lifeerrlow'] = self.tau['lifeerr']
            self.tau['lifeerrup'] = self.tau['lifeerr']
        else:
            regexp = '(?P<t>[0-9\.]*)\^{\+(?P<up>.*)}_{-(?P<lo>.*)}.*times10\^{(?P<exp>.*)}'
            search = re.search(regexp, tau).groupdict()
            search = {key: float(item) for key, item in search.iteritems()}
            self.tau['life'] = search['t']*(10**search['exp'])
            self.tau['lifeerrlow'] = search['lo']*(10**search['exp'])
            self.tau['lifeerrup'] = search['up']*(10**search['exp'])
            self.tau['lifeerr'] = np.sqrt(
                self.tau['lifeerrlow']**2 + self.tau['lifeerrup']**2
            ) / np.sqrt(2.)
        return

    def getwidth(self, line):
        regexp = r'\$(?P<width>.*?)\$ (?P<units>[kMTG]?eV)?'
        search = re.search(regexp, line)
        if search is None:
            return
        units = search.groupdict()['units']
        if units is None:
            return
        width = search.groupdict()['width'].replace(' ', '')
        if width.count('pm'):
            regexp = r'(?P<width>[0-9\.]+).*pm(?P<err>[0-9\.]+)'
            search = re.search(regexp, width).groupdict()
            self.width['width'] = float(search['width'])
            self.width['widtherr'] = float(search['err'])
            self.width['widtherrlow'] = float(search['err'])
            self.width['widtherrup'] = float(search['err'])
        elif width.count('^{+'):
            search = re.search('(?P<w>[0-9\.]*)\^{\+(?P<up>.*)}_{-(?P<lo>.*)}', width)
            search = {key: float(item) for key, item in search.groupdict().iteritems()}
            self.width['width'] = search['w']
            self.width['widtherrlow'] = search['lo']
            self.width['widtherrup'] = search['up']
            self.width['widtherr'] = np.sqrt(
                self.width['widtherrlow']**2 + self.width['widtherrup']**2
            ) / np.sqrt(2.)
        #else:
            #print width
        #if units != 'MeV':
            #1/0
        if units == 'MeV':
            return
        factor = {'eV':1e-6, 'keV':1e-3, 'GeV':1e3, 'TeV':1e6}[units]
        self.width = {key : item*factor for key, item in self.width.iteritems()}
        return

    def add(self, line):
        if line.startswith('MASS'):
            self.getmass(line)
        elif line.startswith('LIFE'):
            self.getlife(line)
        elif line.startswith('WIDTH'):
            self.getwidth(line)
        return

    def getdict(self):
        if self.mass['mass'] < 0:
            return {}
        out = {}
        out.update(self.mass)
        out.update(self.tau)
        out.update(self.width)
        for k in out:
            if out[k] < 0:
                out[k] = None
        out.update({
            'latex' : self.names['latex'],
            'name' : self.names['basicname'],
        })
        dfdict = {self.names['name'] : out}
        return dfdict


dfdict = {}
with open('all_details') as f:
    line = f.readline()
    particle = Particle()
    while line:
        if line.startswith('#'):
            line = f.readline()
            continue
        if Particle.isparticle(line):
            dfdict.update(particle.getdict())
            particle = Particle(line)
        elif particle is not None:
            particle.add(line)
        line = f.readline()
    dfdict.update(particle.getdict())

df = pandas.DataFrame.from_dict(dfdict)
df.to_csv('pdg_particles.csv')

