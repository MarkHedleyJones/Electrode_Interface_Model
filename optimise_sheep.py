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
        return 1.77

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

def simulate_Sheep_CPE(frequencies, *optParams):
    #==========================================================================
    # Create the model
    #==========================================================================
    sheep_parameters = ParameterSet(*optParams)
    interfaceModel = lib.interface.Model(sheep_parameters)

    spice_ckt = interfaceModel.get_spiceModel()
    for line in spice_ckt:
        print line
    spice_ckt.append('R_in 1 e2 0')
    spice_ckt.append('R_out 0 e7 0')
    spice_ckt.append('I1 1 0 DC 0 AC 0.5e-3')

    #==========================================================================
    # Simulate the circuit
    #==========================================================================
    simulator = lib.spice.Simulator()

    analysis = ('AC lin 1', frequencies)
    # analysis = 'AC DEC 10 0.05 10000'

    measurements = [simulator.Measurement('v(e7,e6)', 'voltage')]

    results = simulator.simulate(spice_ckt,
                                 analysis,
                                 measurements)

    current = [complex(0.5e-3, 0) for x in results['voltage']]

    #==========================================================================
    # Process results
    #==========================================================================
    return toImpedance(results['voltage'], current)



def simulate_Sheep_Transimpedance(measureSets, *args):
    #==========================================================================
    # Create the model
    #==========================================================================
    sheep_parameters = ParameterSet(*args)
    interfaceModel = lib.interface.Model(sheep_parameters)

    # Collect all stimulus configs together
    sets = {}
    out = {}
    for stim, meas in measureSets:
        if stim in sets:
            sets[stim].append(meas)
        else:
            sets[stim] = [meas]
            out[stim] = {}

    simulator = lib.spice.Simulator()
    spice_ckt = interfaceModel.get_spiceModel()


    # Iterate through stimus set
    for stim, measSets in sets.items():
        # Append the stimulus jumpers to correct electrode terminals
        spice_tmp = copy.copy(spice_ckt)
        spice_tmp.append('I1 1 0 DC 0 AC 500e-6')
        spice_tmp.append('R_in 1 e' + str(stim)[0] + ' 0')
        spice_tmp.append('R_out 0 e' + str(stim)[1] + ' 0')
        electrodes = range(1, 9)
        electrodes.remove(int(str(stim)[0]))
        electrodes.remove(int(str(stim)[1]))
        for i, electrode in enumerate(electrodes):
            spice_tmp.append('R_tie' + str(i) + '  0 e' + str(electrode) + ' 1e9')

        measurements = []
        # Build up measurement points
        for measurement in measSets:
            measurements.append(simulator.Measurement('v(e' + str(measurement)[0] + ',e' + str(measurement)[1] + ')',
                                                      'voltage' + str(measurement)))

        # Simulate the circuit
        analysis = 'AC lin 1 10e3 10e3'

        results = simulator.simulate(spice_tmp,
                                     analysis,
                                     measurements)

        for measurement in measSets:
            impedance = results['voltage' + str(measurement)] / complex(500e-6)
            out[stim][measurement] = impedance[0]

    return out


class TransMeasurement(object):

    def mod180(self, result):
        mag, phi = cmath.polar(result)
        phi = math.degrees(phi)
        if abs(phi) > 100:
            phi += 180
        phi %= 360

        phi = phi
        return cmath.rect(mag, math.radians(phi))


    def __init__(self, stim, meas, result_sim, result_meas):
        self.stim = stim
        self.meas = meas
        self.result_sim = self.mod180(result_sim)
        self.result_meas = self.mod180(result_meas)
#         print self.result_meas

    def __lt__(self, measurement):
        if self.stim < measurement.stim:
            return True
        elif self.stim == measurement.stim:
            if self.meas < measurement.meas:
                return True
        return False

    def error(self):
#         return (abs(self.result_meas) - abs(self.result_sim)) / abs(self.result_meas)
        x = self.result_meas.real
        y = self.result_meas.imag
        dx = x - self.result_sim.real
        dy = y - self.result_sim.imag
        destance_measured = math.sqrt(math.pow(x, 2) + math.pow(y, 2))
        distance_between = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
        return (distance_between / destance_measured)


class CPEMeasurement(object):


    def __init__(self, freq, result_meas, result_sim):
        self.freq = freq
        self.result_sim = result_sim
        self.result_meas = result_meas

    def __lt__(self, measurement):
        if self.freq < measurement.freq:
            return True
        else:
            return False

    def error(self):
        x = self.result_meas.real
        y = self.result_meas.imag
        dx = x - self.result_sim.real
        dy = y - self.result_sim.imag
        destance_measured = math.sqrt(math.pow(x, 2) + math.pow(y, 2))
        distance_between = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
        return (distance_between / destance_measured)

#         magMeas = abs(self.result_meas)
#         magSim = abs(self.result_sim)
#         phiMeas = cmath.phase(self.result_meas)
#         phiSim = cmath.phase(self.result_sim)
#         magError = (magSim - magMeas) / magMeas
#         phiError = (phiSim - phiMeas) / phiMeas
#         return abs(magError) + abs(phiError)

def shift_phase(impedance, degrees):
    mag, phi = cmath.polar(impedance)
    phi += math.radians(degrees)
    return cmath.rect(mag, phi)

def compare_Transimpedance(*args):

    wrongs = [0, 1, 12, 14, 18, 19, 20, 22, 23, 24, 28, 29, 31, 32, 33, 36, 37, 40, 41, 44]
    measuredData = np.load('measurements/sheep/transimpedance/sheepData.npy')

    measureSets = set()
    for row in measuredData:
            measureSets.add((row['stim'], row['meas']))

    measureSets = list(measureSets)

    simulationData = simulate_Sheep_Transimpedance(measureSets, *args)

    newMeas = []
    tmp = []
    for (stim, meas, measurement) in measuredData:
        if (stim, meas) not in tmp:
            newMeas.append((stim, meas, measurement))
            tmp.append((stim, meas))

    results = []
    for i, (stim, meas, measuredImpedance) in enumerate(newMeas):
        sim_z = simulationData[stim][meas]
        if int(str(stim)[1]) < 8:
            sim_z = shift_phase(sim_z, 180)
        results.append(TransMeasurement(stim,
                                        meas,
                                        sim_z,
                                        measuredImpedance))

    results.sort()
    return results

def compare_Sim_Meas_CPE(*optParams):

    data = np.load('measurements/sheep/displacement/LiveSheep.npy')

    frequencies = list(data['frequency'])

    sim_impedances = simulate_Sheep_CPE(frequencies, *optParams)

    results = []
    for (frequency, measZ, simZ) in zip(frequencies,
                                        list(data['impedance']),
                                        sim_impedances):
        results.append(CPEMeasurement(frequency, measZ, simZ))

    results.sort()
    return results


sheepData = np.load('measurements/sheep/displacement/LiveSheep.npy')
frequencies = list(sheepData['frequency'])

def print_results(params, result):
    for param in params:
        print '{:>6}'.format(float('%.4g' % param)),
    print '= ' + str(result)

def residuals_cpe(params, printProgress=True):
    results = compare_Sim_Meas_CPE(*params)
    result = sum(map(lambda x: x.error(), compare_Sim_Meas_CPE(*params)))
    if printProgress:
        print_results(params, result)
    return result

def residuals_transimpedance(params, printProgress=True):
    results = compare_Transimpedance(*params)
    out = []
    for result in results:
        out.append(result.error())
    result = sum(map(abs, out))
    if printProgress:
        print_results(params, result)
    return result

def residuals_both(params, printProgress=True):
    result = residuals_transimpedance(params, False) + residuals_cpe(params, False)
    if printProgress:
        print_results(params, result)
    return result


def plot_cpe_difference(results, save=False):
    plt.clf()
    lib.plot.formatter.plot_params['margin']['bottom'] = 0.1
    lib.plot.formatter.format()
    ax1 = plt.subplot(211)
    ax1.plot(map(lambda x: x.freq, results),
             map(lambda x: abs(x.result_meas), results),
             label='Measured',
             marker='d')

    ax1.plot(map(lambda x: x.freq, results),
             map(lambda x: abs(x.result_sim), results),
             label='Simulated',
             marker='d')
    ax1.legend(frameon=False, loc=0)
#     plt.title('Magnitude')
    ax1.set_xscale('log')
    ax1.set_yscale('log')

    ax2 = plt.subplot(212)
    ax2.plot(map(lambda x: x.freq, results),
             map(lambda x: math.degrees(cmath.phase(x.result_meas)), results),
             label='Measured',
             marker='d')

    ax2.plot(map(lambda x: x.freq, results),
             map(lambda x: math.degrees(cmath.phase(x.result_sim)), results),
             label='Simulated',
             marker='d')
    ax1.set_ylabel('$|Z|$ ($\Omega$)')
    ax2.set_ylabel('Phase (Degrees)')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%i' % x))
    ax2.legend(frameon=False, loc=0)
#     plt.title('Phase')
    plt.gcf().subplots_adjust(hspace=0.05)
    plt.setp(ax1.get_xticklabels(), visible=False)
    ax2.set_xscale('log')
    if save:
        plt.savefig('optimise_sheep_comparison_cpe_sheep_MeasuredSimulated.pdf', format='pdf')
    else:
        plt.show()


def conditionPhase(phase):
    phase = math.degrees(phase)
    return phase



def plot_transimpedance_difference_paperPlotter_mag(results):
    plt.clf()
    lib.plot.formatter.plot_params['margin']['bottom'] = 0.20
    lib.plot.formatter.plot_params['margin']['top'] = 0.05
    lib.plot.formatter.plot_params['margin']['right'] = 0.01
    lib.plot.formatter.plot_params['margin']['left'] = 0.10
    lib.plot.formatter.format(style='Thesis')
    ax1 = plt.subplot()
    locator = matplotlib.ticker.IndexLocator(1, 0)
    xticks = []
    for i, measurement in enumerate(results):
        stim = str(measurement.stim)
        meas = str(measurement.meas)
        if stim[0] not in meas and stim[1] not in meas:
            xticks.append(str(measurement.stim) + ',' + str(measurement.meas))

    for (ax, mode) in [(ax1, 'mag')]:
        xs = []
        ys = []
        ys2 = []
        count = 0
        for i, measurement in enumerate(results):
            stim = str(measurement.stim)
            meas = str(measurement.meas)
            if stim[0] not in meas and stim[1] not in meas:
                count += 1
                xs.append(count)
                ys.append(abs(measurement.result_sim))
                ys2.append(abs(measurement.result_meas))

        ax.plot(xs, ys2, color='blue', label='Measured', mec='blue', linestyle='', marker='o', markersize=4)
        ax.plot(xs, ys, color='red', label='Simulated')
        ax.set_xticklabels(xticks)
        ax.xaxis.set_major_locator(locator)

    plt.gcf().subplots_adjust(hspace=0.1)
#    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.xticks(rotation=90)
    formy = plt.ScalarFormatter()
    formy.set_scientific(False)
    ax1.yaxis.set_major_formatter(formy)
#     ax2.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%i' % x))
#     ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%i' % x))
    ax1.set_ylabel('$|Z|$ ($\Omega$)')
    ax1.set_xlabel('Electrode pairs  (stimulus, measured)')
    ax1.set_xlim(left=0, right=26)
#   ax1.set_yscale('log')
    ax1.legend(loc=0, frameon=False)

#    plt.show()
    plt.savefig('optimise_sheep_transimpedance_doubleFit_mag_thesis.pdf', format='pdf')

def plot_transimpedance_difference_paperPlotter_phase(results):
    plt.clf()
    lib.plot.formatter.plot_params['margin']['bottom'] = 0.20
    lib.plot.formatter.plot_params['margin']['top'] = 0.05
    lib.plot.formatter.plot_params['margin']['left'] = 0.12
    lib.plot.formatter.plot_params['margin']['right'] = 0.01
    lib.plot.formatter.format(style='Thesis')
    ax1 = plt.subplot()
    locator = matplotlib.ticker.IndexLocator(1, 0)
    xticks = []
    for i, measurement in enumerate(results):
        stim = str(measurement.stim)
        meas = str(measurement.meas)
        if stim[0] not in meas and stim[1] not in meas:
            xticks.append(str(measurement.stim) + ',' + str(measurement.meas))

    for (ax, mode) in [(ax1, 'mag')]:
        xs = []
        ys = []
        ys2 = []
        count = 0
        for i, measurement in enumerate(results):
            stim = str(measurement.stim)
            meas = str(measurement.meas)
            if stim[0] not in meas and stim[1] not in meas:
                count += 1
                xs.append(count)
                ys.append(conditionPhase(cmath.phase(measurement.result_sim)))
                ys2.append(conditionPhase(cmath.phase(measurement.result_meas)))

        ax.plot(xs, ys2, color='blue', label='Measured', mec='blue', marker='o', markersize=4)
        ax.plot(xs, ys, color='red', label='Simulated')
        ax.set_xticklabels(xticks)
        print ys2
        ax.xaxis.set_major_locator(locator)
    plt.gcf().subplots_adjust(hspace=0.1)
#    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.xticks(rotation=90)
    #ax1.set_ylim(-90,90)
    plt.yticks([-90,-45,0,45,90])
    formy = plt.ScalarFormatter()
    formy.set_scientific(False)
    ax1.yaxis.set_major_formatter(formy)
#     ax2.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%i' % x))
#     ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%i' % x))
    ax1.set_ylabel('Phase (Degrees)')
    ax1.set_xlabel('Electrode pairs  (stimulus, measured)')
    ax1.set_xlim(left=0, right=26)
 #   ax1.set_yscale('log')
    ax1.legend(loc=0, frameon=False)

    plt.savefig('optimise_sheep_transimpedance_doubleFit_phase_thesis.pdf', format='pdf')



x0_cpe = [261.9, 619.0, 11310.0, 33.71]
x0_trans = [494.4, 177.7, 165800.0, 102.2]
x0_mid = []
for c, t in zip(x0_cpe, x0_trans):
    x0_mid.append((c + t) / 2.0)

def optimise_SheepTransimpedance(recycle=False):

    # pass 2
    x0 = [4.94137268e+02,
          1.77548701e+02,
          1.67539405e+05,
          1.01690631e+02]

    x0 = [261.9, 619.0, 11310.0, 33.71]  # From optimised CPE
    x0 = [358.56614431, 635.95783875, 11311.85101701, 34.44140664]  # Run1 - 20.0946463685
    x0 = [481.0, 184.5, 165800.0, 101.1]  # Run2 - 17.7444054865
    x0 = [494.4, 177.7, 165800.0, 102.2]  # Run3 - 17.7423914292
    x0 = x0_trans
    # Rebuild Params
#     x0 = [50.0 for x in range(5)]
    if recycle:
        return x0

    myBounds = [(1e-6, None) for x in range(4)]

    optimisedParams = scipy.optimize.fmin_l_bfgs_b(residuals_transimpedance,
                                                        x0=x0,
                                                        approx_grad=True,
                                                        epsilon=0.1,
                                                        bounds=myBounds,
                                                        maxfun=60)
    return optimisedParams[0]


def optimise_SheepCPE(recycle=False):

    x0 = [3.63050039e+02,
          6.34701891e+02,
          1.10100785e+04,
          1.00000000e-09,
          - 2.38476285e+02]
#     x0 = [261.94733223, 619.09898023, 11313.12126772, 33.6029017]
    x0 = [261.9, 619.0, 11310.0, 33.71]  # 0.823818134525
    x0 = x0_cpe
    if recycle:
        return x0

    myBounds = [(1e-9, None) for x in range(4)]

    optimisedParams = scipy.optimize.fmin_l_bfgs_b(residuals_cpe,
                                                  x0=x0,
                                                  approx_grad=True,
                                                  epsilon=0.1,
                                                  bounds=myBounds,
                                                  maxfun=60)

    return optimisedParams[0]

def optimise_cpe_transimpedance(recycle=False):

    x0 = [261.9, 619.0, 11310.0, 33.71]  # 0.823818134525
    x0 = x0_mid
    x0 = [374.6, 393.2, 88550.0, 56.87]  # Run1 = 57.4031646838
    x0 = [261.9, 619.0, 11310.0, 33.71]
    x0 = [359.3, 635.3, 11310.0, 21.47]  # Run1 = 21.2143123173
    x0 = [499.9, 175.6, 11340.0, 126.2]  # Run2 = 20.9272608693
    if recycle:
        return x0

    myBounds = [(1, 100000) for x in range(4)]

    optimisedParams = scipy.optimize.fmin_tnc(residuals_both,
                                                  x0=x0,
                                                  approx_grad=True,
                                                  bounds=myBounds)
    # Alternative CPE optimiser
#     optimisedParams = scipy.optimize.fmin_l_bfgs_b(residuals_both,
#                                                   x0=x0,
#                                                   approx_grad=True,
#                                                   epsilon=0.1,
#                                                   bounds=myBounds,
#                                                   maxfun=60)
    return optimisedParams[0]

# Select which optimiser to use
optParams = optimise_SheepCPE(True)
# optParams = optimise_SheepTransimpedance(True)
# optParams = optimise_cpe_transimpedance(True)
#optParams = [500.0, 176.0, 11300.0, 126.0]

plot_cpe_difference(compare_Sim_Meas_CPE(*optParams), True)
plot_transimpedance_difference_paperPlotter_mag(compare_Transimpedance(*optParams))
plot_transimpedance_difference_paperPlotter_phase(compare_Transimpedance(*optParams))


