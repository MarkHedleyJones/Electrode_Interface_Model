import sys
sys.path.append('../')
import matplotlib.pyplot as plt
import lib.plot.formatter
import lib.files.dataset
import numpy as np
import os
from matplotlib.ticker import FuncFormatter

concs = [1.0 / (2 ** x) for x in range(5)]


def fetch(filename):
    filename = 'measurements/pbs/faradaic/diode/' + filename
    if os.path.isfile(filename):
        data, settings = lib.files.dataset.import_dataset(filename)
        return data
    else:
        return None


def time_current(conc, waitTime):

    filename = str(conc) + 'X-PBS_' + str(waitTime) + 's_stirred.csv'
    data = fetch(filename)

    plt.scatter(map(lambda x: x - data['time'][0], data['time']),
                data['current'],
                label=str(conc),
                edgecolors='none',
                s=2)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%1.0f' % (x * 1e6)))
    plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%1.0f' % (x)))
    plt.gca().set_ylabel('Current ($\mu A$)')
    plt.gca().set_xlabel('Time (seconds)')
    plt.title(str(conc) + 'X PBS - ' + str(waitTime) + ' second wait time', size=8)
    plt.gca().set_xlim(0, 975)
    plt.gca().set_ylim(-0.5e-5, 1.6e-5)
    filename = 'graphs/currentVsTime_' + str(conc) + 'X-PBS.pdf'
    plt.savefig(filename, format='pdf')
    return filename


def get_data():

    voltages_up = set()
    d = {}
    for conc in concs:
        waitTime = 64
        filename = 'measurements/pbs/faradaic/diode/dilutionRun/'
        filename += str(conc) + 'X-PBS_' + str(waitTime) + 's_stirred.npy'
#         data = fetch(filename)
        data = np.load(filename)
        d[conc] = {}
        lastV = 0
        for row in data:
            if row['voltage'] >= 0.75:
                if row['voltage'] > lastV:
                    voltages_up.add(row['voltage'])
                    lastV = row['voltage']
                if row['voltage'] not in d[conc]:
                    d[conc][row['voltage']] = [row['current']]
                else:
                    d[conc][row['voltage']].append(row['current'])


    voltages_up = list(voltages_up)
    voltages_up.sort()
    # Remove voltage above 1.05 - memristor cutoff
    voltages = filter(lambda x: x <= 1.5, voltages_up)

    # Remove first voltages
    return voltages, d


lib.plot.formatter.plot_params['margin']['left'] += 0.01
lib.plot.formatter.format(style='Thesis')
voltages, data = get_data()


for conc in concs:
    xs = []
    ys = []
    err = []
    for i, voltage in enumerate(voltages):
        currents = data[conc][voltage]
        print voltage,
        print currents
        vals = np.array(currents[40:])
        xs.append(voltage)
        ys.append(vals.mean())
        err.append(vals.std() * 2)

    plt.errorbar(xs, ys, err, label=str(conc) + 'X PBS')
#     plt.plot(xs,
#              ys,
#              marker='d',
#              mec='none',
#              label=str(conc) + 'X PBS')

print xs
print ys

plt.gca().set_ylim(1e-7, 2e-5)
plt.gca().set_xlim(0.7, 1.25)
plt.gca().set_yscale('log')
plt.gca().set_ylabel('Current (A)')
plt.gca().set_xlabel('Electrode 2-7 Potential (V)')
plt.legend(frameon=False, loc=0)
# plt.show()
plt.savefig('plot_currentVoltage_logY_Thesis.pdf', format='pdf')

