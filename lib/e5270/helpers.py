import sys

def value(line, verbose=False):
    value = float(line[3:])
    if verbose:
        dtype = line[2]
        if dtype == 'V':
            print 'Voltage measurement'
        elif dtype == 'I':
            print 'Current measurement'
        elif dtype == 'T':
            print 'Time data'
        else:
            print 'Unknown data type'
        status = line[0]
        channels = {'A':1,
                    'B':2,
                    'C':3,
                    'D':4,
                    'E':5,
                    'F':6,
                    'G':7,
                    'H':8}
        print 'value = ' + str(value)
        if status == 'N':
            print 'No status error occured'
        elif status == 'T':
            print 'Another channel reached its compliance setting.'
            sys.exit()
        elif status == 'C':
            print 'This channel (' + str(channels[line[1]]) + ') reached its compliance setting.'
            sys.exit()
        elif status == 'V':
            print 'Measurement data is over the measurement range. Or the sweep'
            print 'measurement was aborted by the automatic stop function or power'
            print 'compliance. D will be the meaningless value 199.999E+99'
            sys.exit()
        elif status == 'X':
            print 'One or more channels are oscillating. Or source output did not settle'
            print 'before measurement.'
            sys.exit()
        elif status == 'G':
            print 'For linear or binary search measurement, the target value was not found'
            print 'within the search range. Returns the source output value.'
            print 'For quasi-pulsed spot measurement, the detection time was over the limit'
            print '(3 s for Short mode, 12 s for Long mode).'
            sys.exit()
        elif status == 'S':
            print 'For linear or binary search measurement, the search measurement was'
            print 'stopped. Returns the source output value. See status of Data_sense.'
            print 'For quasi-pulsed spot measurement, output slew rate was too slow to'
            print 'perform the settling detection.c Or quasi-pulsed source channel reached'
            print 'the current compliance before the source output voltage changed 10 V'
            print 'from the start voltage.'
            sys.exit()
        channel = line[1]
        print 'Measurement channel: ' + str(channels[channel])
    return value


def error(inst):
    errors = inst.ask("ERR?")
    errors = errors.split(',')
    for error in errors:
        e = int(error)
        if e == 100:
            print 'Undefined GPIB command.'
            print 'Send the correct command.'
            print
        elif e == 102:
            print 'Incorrect numeric data syntax.'
            print 'Correct the data syntax.'
            print
        elif e == 103:
            print 'Incorrect terminator position.'
            print 'Correct the command syntax.'
            print 'The number of parameters will be incorrect.'
            print
        elif e == 120:
            print 'Incorrect parameter value. Correct the parameter value.'
            print
        elif e == 121:
            print 'Channel number must be 1 to 2, or 1 to 8.'
            print 'Correct the channel number.'
            print 'The channel number must be 1 to 2 for the Agilent E5262A/E5263A,'
            print 'or 1 to 8 for the Agilent E5260A/E5270B.'
            print
        elif e == 122:
            print 'Number of channels must be corrected.'
            print 'Check the MM, FL, CN, CL, IN, DZ, or RZ command, and correct the'
            print 'number of channels.'
            print
        elif e == 123:
            print 'Compliance must be set correctly.'
            print 'Incorrect compliance value was set. Set the compliance value correctly.'
            print
        elif e == 124:
            print 'Incorrect range value for this channel.'
            print 'Check the range value available for the channel, and correct the range value.'
            print
