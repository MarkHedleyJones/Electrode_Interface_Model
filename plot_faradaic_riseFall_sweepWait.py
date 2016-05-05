import sys
import matplotlib.pyplot as plt
import lib.plot.formatter
import lib.files.dataset
import numpy as np
import os
from pyPdf import PdfFileWriter, PdfFileReader
from matplotlib.ticker import FuncFormatter

lib.plot.formatter.format()

concs = [1.0 / (2 ** x) for x in range(6)]
waitTimes = [32, 64]
hues = [211, 0, 200]

sat = lambda x: list(np.linspace(0, 100, x))
val = lambda x: list(np.linspace(100, 100, x))

cs = {}
for waitTime, hue in zip(waitTimes, hues):
    cs[waitTime] = lib.plot.formatter.generate_colours(hue,
                                                       sat(waitTime),
                                                       val(waitTime))
print 'working'
def colours(x): return [lib.plot.formatter.generate_colours((180.0 / x) * y, 100, 100) for
                y in range(0, x + 1)]

voltages = [0.5,
            0.55,
            0.575,
            0.6,
            0.625,
            0.65,
            0.675,
            0.7,
            0.725,
            0.75,
            0.775,
            0.8,
            0.825,
            0.85,
            0.875,
            0.9,
            0.925,
            0.95,
            0.975,
            1.0,
            1.025,
            1.05,
            1.075,
            1.1,
            1.125,
            1.15,
            1.175,
            1.2]

def fetch(filename):
    filename = 'measurements/pbs/faradaic/diode/dilutionRun/' + filename
    if os.path.isfile(filename):
        data, settings = lib.files.dataset.import_dataset(filename)
        return data
    else:
        return None

def combine_graphs(filenames, outputFilename):
    """
    Combines multiple graphs into a single document
    """
    print "Starting pdf export"
    print filenames
    output = PdfFileWriter()
    files = []
    inputStreams = []
    for filename in filenames:
        files.append(file(filename, "rb"))
        num = len(files) - 1
        inputStreams.append(PdfFileReader(files[num]))
        output.addPage(inputStreams[num].getPage(0))
    outputStream = file(outputFilename, "wb")
    output.write(outputStream)
    outputStream.close()
    for filename in files:
        filename.close()

def extract_TimeCurrentVoltage(conc, waitTime):
    if waitTime == 64:
            clip = 976
    elif waitTime == 32:
        clip_max = 463
        clip_min = 34
    out = []
    filename = str(conc) + 'X-PBS_' + str(waitTime) + 's_stirred.csv'
    data = fetch(filename)
    if data is not None:
        xs_tmp = map(lambda x: x - data['time'][0], data['time'])
        ys_tmp = data['current']
        vs_tmp = data['voltage']
        times = []
        currents = []
        voltages = []
        for x, y, v in zip(xs_tmp, ys_tmp, vs_tmp):
            if x < clip_max and x > clip_min:
                times.append(x)
                currents.append(y)
                voltages.append(v)
        out = {'times':times,
               'currents': currents,
               'voltages': voltages}
        dout = np.array(zip(out['times'], out['voltages'], out['currents']),
                        dtype={'names':('time', 'voltage', 'current'),
                               'formats': ('i', 'f', 'f')})
        return dout


def binBy(data, header):
    headVals = set()
    for row in data:
        headVals.add(round(row[header], 3))
    headVals = list(headVals)
    headVals.sort()
    out = {}
    for headVal in headVals:
        out[headVal] = []

    for headVal in headVals:
        for row in data:
            if round(row[header], 3) == headVal:
                out[headVal].append(row)
    return headVals, out


def plot_faradaicDecay(conc, waitTime, show=False):
    d = extract_TimeCurrentVoltage(conc, waitTime)
    bins, data = binBy(d, 'voltage')
    g_colours = map(lambda x: x[0], colours(len(bins)))

    for i, bin in enumerate(bins):
        print bin
        xs = []
        ys = []
        offset = 0
        for row in data[bin]:
            if offset == 0:
                offset = row['time']
            xs.append(row['time'] - offset)
            ys.append(row['current'])
        plt.plot(xs, ys, marker='d', color=g_colours[len(g_colours) - i - 1], label=str(bin) + ' Volts')
    plt.title(str(conc) + 'X PBS')
    plt.gca().legend(frameon=False, loc=0)
    if show:
        plt.show()


def time_current(conc, waitTime):
#     data = extract_TimeCurrentVoltage(conc, waitTime)
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
#     plt.gca().set_yscale('log')
#     plt.gca().set_xlim(left=0.2)
    plt.gca().set_xlim(0, 1000)
    plt.gca().set_ylim(-0.5e-5, 1.6e-5)
    filename = '/tmp/currentVsTime_' + str(conc) + 'X-PBS.pdf'
    plt.savefig(filename, format='pdf')
    return filename
#     plt.legend()

#     plt.show()


def voltage_current1(conc, waitTimes):
    for waitTime in waitTimes:
        filename = str(conc) + 'X-PBS_' + str(waitTime) + 's_stirred.csv'
        data = fetch(filename)
        if data is not None:
            xs = []
            ys = []
            err = []
            lastRow = data[0]
            for i, row in enumerate(data):
                if row['voltage'] != lastRow['voltage']:
                    xs.append(row['voltage'])
                    ys.append(row['current'])
                    err.append(row['stdDev'])

                lastRow = row
            plt.scatter(xs, ys, color=cs[waitTime], label=str(waitTime) + 's wait')

    plt.gca().set_ylim(-1e-5, 2e-5)
    plt.legend()
    plt.show()

def voltage_current2(conc, waitTimes):
    filenames = []
    for waitTime in waitTimes:
        plt.cla()
        filename = str(conc) + 'X-PBS_' + str(waitTime) + 's_stirred.csv'
        data = fetch(filename)
        if data is not None:
            plt.scatter(data['voltage'], data['current'], color=cs[waitTime], label=str(waitTime) + 's stir')
        plt.gca().set_ylim(-1e-5, 2e-5)
        plt.legend()
        plt.title(str(conc) + 'X PBS')
        filename = str(waitTime) + 's.pdf'
        filenames.append(filename)
        plt.savefig(filename, format='pdf')

    combine_graphs(filenames, str(conc) + 'X-PBS_all.pdf')


def spanplot(conc, waitTime):
    filename = str(conc) + 'X-PBS_' + str(waitTime) + 's_stirred.csv'
    data = fetch(filename)
    xs = data['voltage']
    ys = data['current']
    new_xs = []
    new_ys = []
    i = 0.0
    lastX = None
    res = 0.025
    colours = []
    label = False
    for x, y in zip(xs, ys):
        if x != lastX:
            i = 0.0
            if label == False:
                plt.scatter(new_xs[-waitTime:],
                            new_ys[-waitTime:],
                            color=cs[waitTime],
                            label=str(waitTime) + ' seconds',
                            s=2.0)
                label = True
            else:
                plt.scatter(new_xs[-waitTime:],
                            new_ys[-waitTime:],
                            color=cs[waitTime],
                            s=2.0)

            new_xs = []
            new_ys = []
        else:
            i += 1.0
        adjust = (i * res) / float(waitTime)
        tmpx = int(round(x * 1000))

        if tmpx % 50 == 25:
            new_xs.append(x + res - adjust)
            new_ys.append(y)
        else:
            new_xs.append(x - res + adjust)
            new_ys.append(y)

        lastX = x

    plt.gca().set_ylim(-2.5e-6, 2e-5)
    plt.gca().set_xlim(0.4, 1.3)

def plot_voltSecondsSpan(concs, waitTimes):
    filenames = []
    for conc in concs:
        plt.cla()
        for waitTime in waitTimes:
            spanplot(conc, waitTime)
        plt.legend(frameon=False, loc=0)
        plt.title(str(conc) + 'X PBS', size=8)
        plt.gca().set_xlabel('Voltage (staggered in time)')
        plt.gca().set_ylabel('Current (V)')
        filename = str(conc) + '_all.pdf'
        filenames.append(filename)
        plt.savefig(filename)
    combine_graphs(filenames, 'PBS_all.pdf')


filenames = []
for conc in concs:
    plt.clf()
    lib.plot.formatter.plot_params['margin']['top'] = 0.1
    lib.plot.formatter.format()
    filenames.append(time_current(conc, 64))
combine_graphs(filenames, 'plot_faradaic_riseFall_sweepWait_currentVsTime_All-PBS.pdf')

#plot_faradaicDecay(1.0, 32)
#plot_voltSecondsSpan(concs, waitTimes)


