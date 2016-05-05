import lib.solutions.pbs.modelParameters as parameters
import lib.interface
import lib.spice
import lib.files.measurements
import lib.plot.formatter
import matplotlib.pyplot as plt
import numpy as np
import time
import scipy.optimize
import math
import cmath
import sys
import copy
from matplotlib.ticker import FuncFormatter
import matplotlib.ticker



def toImpedance(voltage, current):
    return map(lambda (voltage, current): voltage / current,
               zip(voltage, current))


class ParameterSet(object):


    vals = None

    def __init__(self, *args):
        self.vals = args

    def ladder_Resistor_RadialElectrode(self):
#         return complex(self.a, self.b)
#         return complex(self.vals[0], -self.vals[5])
        return self.vals[0]

    def ladder_Resistor_RadialInsulator(self):
        return self.ladder_Resistor_RadialElectrode() * (3.0 / 4.0)

    def ladder_Resistor_LongitudinalCommence(self):
#         return complex(self.c, self.d)
#         return complex(self.vals[1], -self.vals[6])
        return self.vals[1]


    def displacement_m(self):
        return 1.34

    def displacement_k(self):
        return 1.773

    def displacement_mag(self):
        """
        The value of the CPE impedance magnitude at 1Hz
        """
        return self.vals[2]

    def displacement_slope(self):
        return -0.79052566


    def faradaic_CM(self):
        return None

    def faradaic_RM(self):
        return None

    def faradaic_i0(self):
        return None

    def faradaic_n(self):
        return None

    def seriesResistance(self):
        """
        Model series resistance or Rs as it is called in the paper.
        """
#         return self.vals[3]

        return self.vals[3]
#     complex(self.vals[3], self.vals[4])

    def temperature(self):
        return 20.0

def simulate_Sheep_CPE(*optParams):
    #==========================================================================
    # Create the model
    #==========================================================================
    sheep_parameters = ParameterSet(*optParams)
    interfaceModel = lib.interface.Model(sheep_parameters)

    spice_ckt = interfaceModel.get_spiceModel()
    spice_ckt.append('R_in 1 e2 0')
    spice_ckt.append('R_out 0 e7 0')
    spice_ckt.append('I1 1 0 DC 0 AC 0.5e-3')

    #==========================================================================
    # Simulate the circuit
    #==========================================================================
    simulator = lib.spice.Simulator()

    analysis = 'AC DEC 10 0.05 10000'

    measurements = [simulator.Measurement('v(e7,e6)', 'voltage')]

    results = simulator.simulate(spice_ckt,
                                 analysis,
                                 measurements)

    out = []

    for row in results:
        current = complex(0.5e-3, 0)
        out.append((row['frequency'], (row['voltage'] / current)))

    return np.array(out, dtype={'names': ('frequency', 'impedance'), 'formats': ('f', 'complex')})




x0_cpe = [261.9, 619.0, 11310.0, 33.71]

lib.plot.formatter.plot_params['margin']['left'] = 0.11

fig = lib.plot.formatter.format(style='IEEE')

sheep = np.load('measurements/sheep/displacement/LiveSheep.npy')
sheep_sim = simulate_Sheep_CPE(*x0_cpe)
saline010 = np.load('measurements/pbs/displacement/0.1X-PBS.npy')

print sheep_sim
#---------------------------------------------------------- Plot magnitude data


plt.scatter(sheep['frequency'],
            map(lambda x: abs(x), sheep['impedance']),
            label='Measured',
            edgecolor='none',
            color='blue')


plt.scatter(map(lambda x: x['frequency'], saline010),
            map(lambda x: abs(x['impedance']), saline010),
            label='0.1X - PBS',
            edgecolor='none',
            marker='v',
            color='green')

plt.plot(sheep_sim['frequency'],
         map(lambda x: abs(x), sheep_sim['impedance']),
         label='Simulated',
         color='red')

plt.legend(frameon=False, loc=0)

ax1 = plt.gca()
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlim(1e-2, 1e5)
ax1.set_ylabel('Impedance Magnitude ($\Omega$)')
ax1.set_xlabel('Frequency (Hz)')
plt.savefig('plot_displacement_sheep_sheepSimulation_magnitudeFrequency.pdf', format='pdf')


#-------------------------------------------------------------- Plot phase data

plt.cla()
plt.scatter(sheep['frequency'],
            map(lambda x: math.degrees(cmath.phase(x)), sheep['impedance']),
            color='blue',
            edgecolor='none',
            label='Measured')

plt.scatter(saline010['frequency'],
            map(lambda x: math.degrees(-cmath.phase(x)), saline010['impedance']),
            label='0.1X - PBS',
            marker='v',
            edgecolor='none',
            color='green')

plt.plot(sheep_sim['frequency'],
         map(lambda x: math.degrees(cmath.phase(x)), sheep_sim['impedance']),
         label='Simulated',
         color='red')

ax2 = plt.gca()
ax2.set_xlim(1e-2, 1e5)
ax2.set_ylim(-80, 0)
ax2.set_ylabel('Impedance Phase (Degrees)')
ax2.set_xlabel('Frequency (Hz)')
ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%i' % x))
ax2.legend(frameon=False, loc=0)

ax2.set_xscale('log')
plt.savefig('plot_displacement_sheep__sheepSimulation_phaseFrequency.pdf', format='pdf')
