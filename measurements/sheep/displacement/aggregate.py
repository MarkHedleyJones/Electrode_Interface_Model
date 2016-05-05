import os
import numpy as np
import cmath
import math
import matplotlib.pyplot as plt

filenames = []

dtimes = ['-0:02:08', '0:07:56']

for dtime in dtimes:
    filenames.append('Day2_Sheep_' + dtime + '_CPE.npy')

frequency = []
impedance = []

d1 = np.load(filenames[0])
d2 = np.load(filenames[1])

frequency = list(d1['frequency'])

for a, b in zip(list(d1['impedance']), list(d2['impedance'])):
#     mag = abs(a) + abs(b)
#     phi = cmath.phase(a) + math.pi + cmath.phase(b)
#     mag /= 2.0
#     phi /= 2.0
    mag = abs(a)
    phi = -cmath.phase(a) - math.radians(180)
    impedance.append(cmath.rect(mag, phi))
frequency = frequency[1:-2]
impedance = impedance[1:-2]
out = np.array(zip(frequency, impedance), dtype={'names':('frequency', 'impedance'),
                                                'formats':('f', 'complex')})

np.save('LiveSheep', out)

ax1 = plt.subplot(121)
data = np.load('LiveSheep.npy')
ax1.plot(data['frequency'], map(abs, data['impedance']))
ax1.set_xscale('log')
ax1.set_yscale('log')
ax2 = plt.subplot(122)
ax2.plot(data['frequency'], map(lambda x: math.degrees(cmath.phase(x)), data['impedance']))
ax2.set_xscale('log')
plt.show()
