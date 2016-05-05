import sys
import matplotlib.pyplot as plt
import lib.plot.formatter
import lib.files.dataset
import numpy as np
import os

lib.plot.formatter.plot_params['margin']['top'] = 0.1
lib.plot.formatter.format()
measuredConcs = [1.0]
colours = ['red', 'blue', 'green', 'grey', 'black', 'orange']

def get_data(conc, waitTime, filename=False):
    """
    Find and open the data record. Performs numpy conversion if not done on
    the dataset already and saves result in same directory.
    """
    filename_input = 'measurements/pbs/faradaic/diode/' + str(waitTime) + 's/' + str(conc) + 'X-PBS'
    if filename != False:
        filename_input = filename

    if os.path.isfile(filename_input + '.npy'):
        data = np.load(filename_input + '.npy')
    elif os.path.isfile(filename_input + '.csv'):
        data, settings = lib.files.dataset.import_dataset(filename_input + '.csv')
        np.save(filename_input + '.npy', data)
    elif os.path.isfile(str(conc) + 'X-PBS.csv'):
        print "PLEASE MOVE " + str(conc) + 'X-PBS.csv' + " INTO MEASUREMENT DIRECTORY"
        data, settings = lib.files.dataset.import_dataset(str(conc) + 'X-PBS.csv')

    print conc
    return data


def get_concFilename(concs):
    if len(concs) > 1:
        return str(min(concs)) + '-' + str(max(concs))
    else:
        return str(concs[0])


def plot_voltageVsCurrent(concs,
                          measured_waitTime,
                          plot_relWait=0.99,
                          ylog=False,
                          alpha=1.0,
                          save=False):
    for conc, colour in zip(concs, colours):
        data = get_data(conc, measured_waitTime)

        changePoints = []
        lastVoltage = 0
        holdTime = 0
        for index, row in enumerate(data):
            if row['voltage'] != lastVoltage:
                changePoints.append(index)
                lastVoltage = row['voltage']
                holdTime = 0
            else:
                holdTime += 1

        offset = plot_relWait * holdTime
        changePoints = map(lambda x: x + offset, changePoints[:-1])
        xs = []
        ys = []
        lenData = len(data)
        for point in changePoints:
            xs.append(data[point]['voltage'])
            ys.append(data[point]['current'])

        plt.plot(xs, ys, marker='s', markersize=2.0, label=str(conc) + 'X (' + str(measured_waitTime) + 's)',
                 color=colour, alpha=alpha)

    ax = plt.gca()
    plt.legend(frameon=False, loc=0)
    if ylog:
        ax.set_yscale('log')
    ax.set_xlabel('Voltage (V)')
    ax.set_ylabel('Current (A)')

    if save == True:
        filename = 'plot_faradaic_diodeCurves_' + get_concFilename(concs)
        if ylog:
            filename += 'X-PBS_voltageVsLogCurrent.pdf'
        else:
            filename += 'X-PBS_voltageVsCurrent.pdf'

        plt.savefig(filename, format='pdf')
        plt.cla()


def plot_timeVsCurrent(concs, waitTime, save=True):
    for conc in concs:
        data = get_data(conc, waitTime)
        plt.plot(map(lambda x: x - data[0]['time'], data['time']),
                 data['current'],
                 label=str(conc) + 'X PBS',
                 linewidth=0.1)
    ax = plt.gca()
    plt.title('Current versus time during measurement')
    plt.legend(frameon=False, loc=0)
    ax.set_xlabel('Time (s)')
    quantifier = lib.plot.formatter.format_labels(plt.gca().yaxis, data['current'])
    ax.set_ylabel('Current ($' + quantifier + '$A)')

    if save == True:
        filename = 'plot_faradaic_diodeCurves_' + get_concFilename(concs) + 'X-PBS_timeVsCurrent.pdf'

        plt.savefig(filename, format='pdf')
        plt.cla()


def plot_timeVsCurrent_closeup(concs, waitTime, save=True):
    for conc in concs:
        data = get_data(conc, waitTime)
        plt.plot(map(lambda x: x - data[0]['time'], data['time']),
                 data['current'],
                 label=str(conc) + 'X PBS',
                 linewidth=0.1)
    ax = plt.gca()
    plt.title('Current versus time during measurement')
    plt.legend(frameon=False, loc=0)
    ax.set_xlabel('Time (s)')
    ax.set_xlim(left=5.0e4, right=7.4e4)
    ax.set_ylim(bottom=0)
    quantifier = lib.plot.formatter.format_labels(plt.gca().yaxis, data['current'])
    ax.set_ylabel('Current ($' + quantifier + '$A)')

    if save == True:
        filename = 'plot_faradaic_diodeCurves_' + get_concFilename(concs) + 'X-PBS_timeVsCurrent_closeup.pdf'

        plt.savefig(filename, format='pdf')
        plt.cla()


def plot_effectOfWaiting(data, seconds):

    xs = []
    ys = []
    lastVoltage = 0.0
    lastChange = 0.0
    for row in data:
        if row['voltage'] > lastVoltage:
            lastChange = row['time']
            lastVoltage = row['voltage']
        if row['time'] == lastChange + seconds:
            xs.append(row['voltage'])
            ys.append(row['current'])

    return xs, ys

def plot_stirr(conc, waits):
    for wait in waits:
        filename = str(conc) + 'X-PBS_' + str(wait) + 's_stirred.csv'
        data = get_data(conc, filename=filename)


def plot_effectOfWaiting():
    for conc in measuredConcs:
        data = get_data(conc)
        seconds = 128
        xs, ys = plot_effectOfWaiting(data, seconds)
        plt.plot(xs, ys, color='green', label=str(seconds) + ' seconds - ' + str(conc))
    plt.legend()
    plt.show()




# Measured wait times are: 32s, 128s, 600s
plot_timeVsCurrent(measuredConcs, 600)
plot_voltageVsCurrent(measuredConcs, 128, 0.4, ylog=True, save=True)
plot_timeVsCurrent_closeup(measuredConcs, 600, True)


