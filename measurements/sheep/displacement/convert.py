import os
import numpy as np
import cmath
import math

filenames = os.listdir('.')

for filename in filenames:
    if filename[-4:] == '.txt' and filename.find('Notes') == -1:

        with open(filename, 'r') as f:
            line = f.readline()
            data = []
            while line:
                p = map(float, line.split())
                o = []
                o.append(p[0])
                v = cmath.rect(p[1], math.radians(p[2]))
                i = cmath.rect(p[3], math.radians(p[4]))
                z = v / i
                o.append(v)
                o.append(i)
                o.append(z)

                data.append(tuple(o))
                line = f.readline()
        out = np.array(data, dtype={'names': ('frequency',
                                             'voltage',
                                             'current',
                                             'impedance'),
                                   'formats': ('f',
                                               'complex',
                                               'complex',
                                               'complex')})
        np.save(filename[:-4], out)
