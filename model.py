import lib.solutions.pbs.modelParameters as parameters
import lib.interface
import lib.spice
import lib.files.measurements
import lib.plot.formatter
import scipy.optimize
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
import math



#==============================================================================
# Measurement Notes
#==============================================================================
# When the E5270 increments its output voltage it does so like a capacitor
# charging. A sufficient approximation suitable for simulation would to be
# to assume a linear rise by the 50mV in 500e-6 seconds.

print("This file has been kept for archive purposes, but does not function in its current state")
sys.exit()

def toImpedance(voltage, current):
    return map(lambda (voltage, current): voltage / current,
               zip(voltage, current))



class PBSParameterSet(object):

    concentration = None
    i0 = 3.5e-9
    n = 1.0

    i0_scaler = 1.0
    n_scaler = 1.0

    def __init__(self, concentration):
        self.concentration = concentration
        self.conductivity()

    def conductivity(self):
        """
        Converts a concentration of PBS into a conductivity according to a
        least squares fit of the solutions used
        """
        m = 1.67296736e-02  # Determined from optimisation
        c = 8.54665149e-05  # Determined from optimisation
        return m * self.concentration + c


    def ladder_Resistor_RadialElectrode(self):
        return 0.407 / self.conductivity()

    def ladder_Resistor_RadialInsulator(self):
        return self.ladder_Resistor_RadialElectrode() * (3.0 / 4.0)

    def ladder_Resistor_LongitudinalCommence(self):
        return 3.71 / self.conductivity()


    def displacement_m(self):
        return 1.34

    def displacement_k(self):
        return 1.773

    def displacement_mag(self):
        """
        The value of the CPE impedance magnitude at 1Hz
        """

        return 3284 * math.pow(self.concentration, -0.158)

    def displacement_slope(self):
        return -0.79052566


    def faradaic_CM(self):
        return None

    def faradaic_RM(self):
        return None

    def faradaic_i0(self):
        return self.i0 * self.i0_scaler

    def faradaic_n(self):
        return self.n * self.n_scaler


    def seriesResistance(self):
        """
        Model series resistance or Rs as it is called in the paper.
        """
        return 13.38 * math.pow(self.concentration, -0.8397)

    def temperature(self):
        return 20.0

def simulate_PBS_CPE(concentration, frequencies):
    #==========================================================================
    # Create the model
    #==========================================================================
    pbs_parameters = parameters.ParameterSet(concentration)
    interfaceModel = lib.interface.Model(pbs_parameters)

    spice_ckt = interfaceModel.get_spiceModel()
    spice_ckt.append('R_in 1 e2 0')
    spice_ckt.append('R_out 0 e7 0')
    spice_ckt.append('V1 1 0 DC 0 AC 1')

    #==========================================================================
    # Simulate the circuit
    #==========================================================================
    simulator = lib.spice.Simulator()

    analysis = ('AC lin 1', frequencies)
    # analysis = 'AC DEC 10 0.05 10000'

    measurements = [simulator.Measurement('v(e7,e6)', 'voltage'),
                    simulator.Measurement('i(V1)', 'current')]

    results = simulator.simulate(spice_ckt,
                                 analysis,
                                 measurements)

    #==========================================================================
    # Process results
    #==========================================================================
    return (results['frequency'], toImpedance(results['voltage'],
                                              results['current']))


def build_peasewiseLinear(sampleConc):
    data = np.load('measurements/pbs/faradaic/diode/dilutionRun/' + str(sampleConc) + 'X-PBS_64s_stirred.npy')
    pieces = []
    lastVoltage = data['voltage'][0]

    for row in data:
        if round(row['voltage'], 3) >= 1.05:
            break
        elif row['voltage'] != lastVoltage:
            print row['voltage']
            pieces.append((row['time'] - 1, round(lastVoltage, 2)))
            pieces.append((row['time'], round(row['voltage'], 2)))
            lastVoltage = row['voltage']

    return pieces

linearPieces = None

def simulate_PBS_Faradaic(pbs_parameters):

    global linearPieces
    #==========================================================================
    # Create the model
    #==========================================================================
    if pbs_parameters is False:
        print 'loading default parameters'
        pbs_parameters = PBSParameterSet(1.0)
    concentration = pbs_parameters.concentration
    interfaceModel = lib.interface.Model(pbs_parameters)
    spice_ckt = interfaceModel.get_spiceModel()
    spice_ckt.append('R_in 1 e7 0')
    spice_ckt.append('R_out 0 e2 0')
    line = 'V1 1 0 DC 0 PWL('
    if linearPieces is None:
        linearPieces = build_peasewiseLinear(concentration)
    for piece in linearPieces:
        line += str(piece[0]) + ' ' + str(piece[1]) + ' '
    line += ')'

    spice_ckt.append(line)


    #==========================================================================
    # Simulate the circuit
    #==========================================================================
    simulator = lib.spice.Simulator()

    analysis = 'TRAN ' + str(1) + ' 651 0'
    # analysis = 'AC DEC 10 0.05 10000'

    measurements = [simulator.Measurement('v(e7,e2)', 'voltage'),
                    simulator.Measurement('i(V1)', 'current')]

    results = simulator.simulate(spice_ckt,
                                 analysis,
                                 measurements,
                                 timeout=60)

    #==========================================================================
    # Process results
    #==========================================================================
    return (list(results['time']), map(lambda x:-x, list(results['current'])))

def compare_Sim_Meas_CPE():
    concentrations = [1.0, 0.5, 0.25, 0.1, 0.05, 0.025]
    for concentration in concentrations:
        data = lib.files.measurements.get('displacement', concentration)
        plt.scatter(data['frequency'], map(abs, data['impedance']))

    frequencies = list(data['frequency'])

    for concentration in concentrations:
        frequency, impedance = simulate_PBS_CPE(concentration, frequencies)
        plt.plot(frequency, map(abs, impedance), marker='s', markersize=3)

    plt.gca().set_xscale('log')
    plt.gca().set_yscale('log')
    plt.show()

def compare_Sim_Meas_Faradaic(parameters):
    concentration = parameters.concentration
    sim_time, sim_current = simulate_PBS_Faradaic(parameters)
    sim_time = map(lambda x: int(round(x)), sim_time)
    xs_sim = []
    ys_sim = []
    for (x, y) in zip(sim_time, sim_current):
        if x > 195 and x not in xs_sim:
            xs_sim.append(x)
            ys_sim.append(y)

    data = np.load('measurements/pbs/faradaic/diode/dilutionRun/' + str(concentration) + 'X-PBS_64s_stirred.npy')
    xs_meas = []
    ys_meas = []
    for row in data:
        if row['time'] > 651:
            break
        elif row['time'] > 195:
            xs_meas.append(row['time'])
            ys_meas.append(row['current'])

    return (xs_sim, ys_sim, xs_meas, ys_meas)


def filter_Sim_Meas_Faradaic(args):
    points = [196 + x * 65 for x in range(8)]
    xs_sim, ys_sim, xs_meas, ys_meas = args

    xs = points
    ys_out_meas = map(lambda x: ys_meas[xs_meas.index(x)], points)
    ys_out_sim = map(lambda x: ys_sim[xs_sim.index(x)], points)

    return (xs, ys_out_sim, xs, ys_out_meas)


def residuals_Sim_Meas_Faradaic(args):
    xs_sim, ys_sim, xs_meas, ys_meas = args
    out = []
    for sim, meas in zip(ys_sim, ys_meas):
        out.append((meas - sim))
    return out

def plot_Sim_Meas_Faradaic():
    concentrations = [1.0]
    for concentration in concentrations:
        xs_sim, ys_sim, xs_meas, ys_meas = compare_Sim_Meas_Faradaic(concentration)
        plt.plot(xs_sim, ys_sim)
        plt.scatter(xs_meas, ys_meas)
    plt.show()


def residuals(p, pbs_parameters):
    pbs_parameters.n = p[0]
    pbs_parameters.i0 = p[1]
    result = residuals_Sim_Meas_Faradaic(filter_Sim_Meas_Faradaic(compare_Sim_Meas_Faradaic(pbs_parameters)))
    print p, sum(map(abs, result))
    return sum(map(abs, result))
#     return sum(map(abs, result))





#==============================================================================
# Manual Sweep
#==============================================================================
# n_min = 0.3
# n_max = 5.0
# i0_min = 1e-12
# i0_min = math.log10(i0_min)
# i0_max = 1e-3
# i0_max = math.log10(i0_max)
#
# pts = 50
#
# pbs_parameters = PBSParameterSet(1.0)
# ns = list(np.linspace(n_min, n_max, pts))
# i0s = list(np.logspace(i0_min, i0_max, pts))
# with open('nI0Data.csv', 'w') as f:
#     for n in ns:
#         for i0 in i0s:
#             pbs_parameters.n = n
#             pbs_parameters.i0 = i0
#             try:
#                 result = residuals([n, i0], pbs_parameters)
#                 f.write(str(n) + ', ' + str(i0) + ', ' + str(result) + '\n')
#             except IOError:
#                 f.write(str(n) + ', ' + str(i0) + ', 1.234\n')



#==============================================================================
# Optimisation
#==============================================================================

myBounds = [(1e-12, 1e-3), (0.1, 2.0)]
x0 = (1e-7, 1.0)

pbs_parameters = PBSParameterSet(1.0)

optParams = {'n': 1.0,
             'i0': 1.0}
pbs_parameters.i0_scaler = optParams['i0']
pbs_parameters.n_scaler = optParams['n']



optimisedParams = scipy.optimize.fmin_l_bfgs_b(residuals,
                                                x0=(3.0, 3.0),
                                                approx_grad=True,
                                                args=[pbs_parameters],
                                                epsilon=0.01,
                                                bounds=myBounds,
                                                maxfun=60)



print optimisedParams
sys.exit()

while True:
    for param in ['n', 'i0']:
        if param == 'i0':
            pbs_parameters.n_scaler = optParams['n']
            bounds = [(1e-12, 1e-3)]
            epsilon = 2.0
        elif param == 'n':
            pbs_parameters.i0_scaler = optParams['i0']
            bounds = [(0.1, 3.0)]
            epsilon = 2.0
        optimisedParams = scipy.optimize.leastsq(residuals,
                                                 x0=[optParams[param]],
                                                 args=[pbs_parameters, param])
#         optimisedParams = scipy.optimize.fmin_l_bfgs_b(residuals,
#                                                         x0=[optParams[param]],
#                                                         approx_grad=True,
#                                                         args=[pbs_parameters, param],
#                                                         epsilon=epsilon,
#                                                         bounds=bounds,
#                                                         pgtol=1e-10,
#                                                         maxfun=60)
        print 'setting optparams[' + param + '] to ' + str(optimisedParams[0][0])
        optParams[param] = optimisedParams[0][0]
print optimisedParams
# filter_Sim_Meas_Faradaic(compare_Sim_Meas_Faradaic(1.0))

