import subprocess
import threading
import os
import numpy as np
import sys

class Simulator(object):

    command = None
    analysisType = None
    measurements = None
    workingDir = None

    def __init__(self):
        self.command = None
        self.workingDir = os.getcwd()


    class Command(object):

        def __init__(self, cmd):
            self.cmd = cmd
            self.process = None

        def run(self, timeout):
            startDir = os.getcwd()
            def target():
                with open(os.devnull, 'w') as dnull:
                    os.chdir('/tmp/')
                    self.process = subprocess.Popen(self.cmd,
                                                    stdout=dnull,
                                                    stderr=subprocess.STDOUT,
                                                    shell=True)
                self.process.communicate()

            thread = threading.Thread(target=target)
            thread.start()
            thread.join(timeout)
            os.chdir(startDir)
            if thread.is_alive():
                print('Terminating process')
                self.process.terminate()
                thread.join()
                return False
            else:
                return True

    class Measurement(object):

        isComplex = False
        measPoint = None
        measName = None
        measWidth = None  # The number of colums this measurement will produce

        def __init__(self, measPoint, measName):
            self.measName = measName
            self.measPoint = measPoint
            self.measType = measPoint[:measPoint.index('(')]

        def calculate_width(self, analysisType):
            if analysisType == 'ac':
                if self.measType == 'v':
                    self.isComplex = True
                elif self.measType == 'i':
                    self.isComplex = True
            elif len(self.measType) == 2:
                raise Exception('Invalid measurement type (' + self.measType +
                                ') for .' + analysisType.upper())

    class Analysis(object):

        line = None
        analysisType = None

        def __init__(self, mode,
                     start=None,
                     stop=None,
                     step=None,
                     pointArray=None):

            # Determine the analysis type and start the line
            if mode.lower() == 'ac':
                self.line = 'AC LIN '
                self.analysisType = 'ac'
            elif mode.lower() == 'tran':
                self.line = 'TRAN '
                self.analysisType = 'tran'
            else:
                self.line = mode + ' '
                if mode.lower().find('AC '):
                    self.analysisType = 'ac'
                elif mode.lower().find('TRAN '):
                    self.analysisType = 'tran'
                elif mode.lower().find('OP'):
                    self.analysisType = 'op'
                else:
                    raise Exception('Unknown analysis type')

            if (stop is not None and
                pointArray is not None):

                raise Exception('Both range and point array specified')

            elif (stop is None and
                  pointArray is None and
                  mode.lower() != 'op'):

                raise Exception('You must specify the analysis range')

            elif stop is not None:
                if step is None:
                    step = stop / 10
                if start is None:
                    start = 0
                self.line += (str(step) + ' ' +
                             str(stop) + ' ' +
                             str(start) + ' ')
            elif pointArray is not None:
                self.line = []
                for point in pointArray:
                    self.line.append('AC lin 1 ' + str(point))


    def processResult(self, filename):
        """
        Read in a spice output file and interperet results
        """

        # Update the measurements with currenet analysis type
        for measurement in self.measurements:
            measurement.calculate_width(self.analysisType)

        ops = []  # Operations to perform per part of a row
        head = None  # Weather each measurement comes with a header
        if self.analysisType == 'tran' or self.analysisType == 'ac':
            head = True  # Tran and AC come with measurement headers

        for measurement in self.measurements:
            if head == True:
                ops.append(1)  # It is a single value
                head = False  # Indicate that we have accounted for the header
            elif head == False:
                ops.append(0)  # Dont store subsiquent headers
            if measurement.isComplex:
                ops.append(2)  # This measurement is comprised of two values
            else:
                ops.append(1)  # This measurement is comprised of one value

        # Import the data from the datafile according to the ops array
        data = []
        with open('/tmp/' + filename + '.data', 'r') as f:

            line = f.readline()
            while line:
                parts = list(map(float, line.split()))
                row = []
                offset = 0
                for tmpIndex, op in enumerate(ops):
                    index = tmpIndex + offset
                    if op == 1:
                        row.append(parts[index])
                    elif op == 2:
                        row.append(complex(parts[index],
                                           parts[index + 1]))
                        offset += 1
                data.append(tuple(row))
                line = f.readline()

        # Create the dtype header for the return numpy array

        names = []
        formats = []
        if self.analysisType == 'tran':
            names.append('time')
            formats.append('f')
        elif self.analysisType == 'ac':
            names.append('frequency')
            formats.append('f')
        # TODO: Accomodate for format of .OP

        for measurement in self.measurements:
            names.append(measurement.measName)
            if measurement.isComplex:
                formats.append('complex')
            else:
                formats.append('f')

        return np.array(data, dtype={'names': names, 'formats':formats})

    def simulate(self,
                 circuit,
                 analysis,
                 measurements,
                 appendResults=False,
                 timeout=10,
                 cleanup=True,
                 debug=False):

        """
        Takes a string representing a spice circuit, saves it to a file,
        runs it through ngspice and returns the results as an array
        """
        frequencies = None

        # Separate out sim frequencies if passed along with analysis line
        if type(analysis) == tuple:
            frequencies = analysis[1]
            analysis = analysis[0]
            appendResults = True

        if analysis.lower().find('ac') != -1:
            self.analysisType = 'ac'
        elif analysis.lower().find('tran') != -1:
            self.analysisType = 'tran'
        elif analysis.lower().find('op') != -1:
            self.analysisType = 'op'
        else:
            raise Exception('Unknown analysis type')


        self.measurements = measurements

        filename = 'model_netlist.spice'
        outputName = 'model_data'

        # Clean up temp files
        try:
            os.remove('/tmp/' + filename)
            os.remove('/tmp/' + outputName + '.data')
        except OSError:
            pass

        with open('/tmp/' + filename, 'w') as f:
            for line in circuit:
                f.write(line + '\n')

            f.write("****************************************\n")
            f.write("*           Simulation options         *\n")
            f.write("****************************************\n")
            f.write(".control\n")
            if appendResults:
                f.write("set appendwrite\n")

            if frequencies != None:
                for frequency in frequencies:
                    f.write(analysis + ' ' + str(frequency) + ' ' +
                            str(frequency) + '\n')
                    f.write('wrdata ' + outputName + ' ')
                    for measurement in measurements:
                        f.write(measurement.measPoint + ' ')
                    f.write("\n")
            else:
                f.write(analysis + '\n')
                f.write('wrdata ' + outputName + ' ')
                for measurement in measurements:
                    f.write(measurement.measPoint + ' ')
                f.write("\n")
            f.write(".endc\n")
            f.write(".END\n")

        # Run the simulation
        if debug == False:
            # This will use the timeout provided
            if self.command is None:
                self.command = self.Command("ngspice -bp " + filename)
            if self.command.run(timeout) == False:
                print("A errant simulation terminated")
                return None
        else:
                subprocess.call(["ngspice", "-bp", filename])

        return self.processResult(outputName)


