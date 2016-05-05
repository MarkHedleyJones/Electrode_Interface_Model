import sys
import matplotlib.pyplot as plt
import lib.plot.formatter
import lib.files.dataset
import numpy as np
import os
from matplotlib.ticker import FuncFormatter
from pyPdf import PdfFileWriter, PdfFileReader

lib.plot.formatter.format()
concs = [1.0 / (2 ** x) for x in range(6)]
print concs
# concs = [0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
hue = 211

sat = lambda x: list(np.linspace(5, 100, x))
val = lambda x: list(np.linspace(100, 100, x))


reds = lib.plot.formatter.generate_colours(0,
                                         sat(64),
                                         val(64))

blues = lib.plot.formatter.generate_colours(215,
                                         sat(64),
                                         val(64))


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


def spanplot(conc, waitTime):
    filename = 'measurements/pbs/faradaic/diode/dilutionRun/' + str(conc) + 'X-PBS_' + str(waitTime) + 's_stirred.csv'
    data, settings = lib.files.dataset.import_dataset(filename)
    xs = data['voltage']
    ys = data['current']
    new_xs = []
    new_ys = []
    i = 0.0
    lastX = None
    res = 0.005
    colours = []
    label = False
    for x, y in zip(xs, ys):
        if x != lastX:
            i = 0.0
            if x < lastX:
                plt.scatter(new_xs[-waitTime:],
                            new_ys[-waitTime:],
                            color=reds,
                            s=2.0)
            else:
                plt.scatter(new_xs[-waitTime:],
                            new_ys[-waitTime:],
                            color=blues,
                            s=2.0)

            new_xs = []
            new_ys = []
        else:
            i += 1.0
        adjust = (i * res) / float(waitTime)
        tmpx = int(round(x * 1000))
        if tmpx % 10 == 5:
            new_xs.append(x + res - adjust)
            new_ys.append(y)
        else:
            new_xs.append(x - res + adjust)
            new_ys.append(y)

        lastX = x

    plt.gca().set_ylim(-1e-6, 16e-6)
    plt.gca().set_xlim(0.4, 1.3)

def plot_voltSecondsSpan(concs):
    filenames = []
    for conc in concs:
        plt.cla()
        spanplot(conc, 64)
#         plt.legend(frameon=False, loc=0)
        plt.title(str(conc) + 'X PBS', size=8)
        plt.gca().set_xlabel('Voltage (staggered in time)')
        plt.gca().set_ylabel('Current ($\mu A$)')
        plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, pos: '%1.0f' % (x * 1e6)))
#         plt.gca().set_yscale('log')
        filename = '/tmp/' + str(conc) + '_all.pdf'
        filenames.append(filename)
        plt.savefig(filename)
    combine_graphs(filenames, 'plot_faradaic_riseFall_sweepWait_v2_all.pdf')


plot_voltSecondsSpan(concs)

