import math
import mpmath
import lib.solutions.pbs.modelParameters

class SpiceComponent(object):

    componentType = None
    componentValue = None

    def __init__(self, componentType, componentValue):
        self.componentType = componentType
        self.componentValue = componentValue



class Model(object):

    parameterSet = None
    includes_diode = True
    includes_memristor = True
    autoCircuits = None
    impedeors = None

    def __init__(self, parameterSet):
        miss = 'WARNING: parameter'
        self.includes_diode = True
        self.includes_memristor = True
        self.parameterSet = parameterSet

        if parameterSet.faradaic_CM() is None:
            miss += ' cm'
            self.includes_memristor = False
        if parameterSet.faradaic_RM() is None:
            miss += ' rm'
            self.includes_memristor = False
        if parameterSet.faradaic_i0() is None:
            miss += ' i0'
            self.includes_diode = False
        if parameterSet.faradaic_n() is None:
            miss += ' n'
            self.includes_diode = False

#         if self.includes_diode == False:
#             print miss + ' is not available from parameter set!'
#             print 'Excluding Faradaic (memristor and diode) components!'
#         elif self.includes_memristor == False:
#             print miss + ' is not available from parameter set!'
#             print 'Excluding memristive component!'

        self.autoCircuits = []
        self.impedeors = {}

    def subcircuit_impedance(self, real, imaginish, name='impedeor'):
        '''
        Generates a generic impedance element from a resistor, capacitor and
        an inductor
        '''
        # Generate the resistor ladder
        out = []
        out.append("*************************Impedeor subckt")
        out.append(".SUBCKT " + name + " a b")
        out.append("R1 a mid " + str(real))
        if imaginish > 0.0:
            out.append("L1 mid b " + str(imaginish))
            out.append("R2 mid b 1e9")
        elif imaginish < 0.0:
            out.append("C1 mid b " + str(-imaginish))
            out.append("R2 mid b 1e9")
        else:
            out.append('R2 mid b 0')
        out.append(".ENDS " + name)
        return out

    def impedeor(self, name, nodeA, nodeB, value):
        if value in self.impedeors:
            return ('X_' + str(name) + ' ' +
                    str(nodeA) + ' ' +
                    str(nodeB) + ' ' +
                    str(self.impedeors[value]))
        else:
            subCktName = 'impedeor' + str(len(self.impedeors))
            self.autoCircuits.append(self.subcircuit_impedance(value.real,
                                                               value.imag,
                                                               subCktName))
            self.impedeors[value] = subCktName
            return ('X_' + str(name) + ' ' +
                    str(nodeA) + ' ' +
                    str(nodeB) + ' ' +
                    str(subCktName))

    def as_spiceComponent(self, item, nodeA, nodeB, elementNumber):
        """
        Allows passing of individual spice components or subcircuit names for
        combination in the combine_subcircuits function.
        """
        if type(item) == SpiceComponent:
            if type(item.componentValue) == complex:
                return self.impedeor(item.componentType + str(elementNumber),
                                     nodeA,
                                     nodeB,
                                     item.componentValue)
            else:
                return (item.componentType + str(elementNumber) + ' ' +
                        str(nodeA) + ' ' +
                        str(nodeB) + ' ' +
                        str(item.componentValue))
        else:
            return ('X_' + str(elementNumber) + ' ' +
                    str(nodeA) + ' ' +
                    str(nodeB) + ' ' +
                    item)

    def subcircuit_ladder(self, electrodes=8, depth=5, padding=3, name='ladder'):
        """
        Generates a resistor ladder circuit for insertion into a spice file.
        Parameters:
        """

        Rv_commence = self.parameterSet.ladder_Resistor_LongitudinalCommence()
        Rr_insulator = self.parameterSet.ladder_Resistor_RadialInsulator()
        Rr_electrode = self.parameterSet.ladder_Resistor_RadialElectrode()

        # Populate the latitude resistor value array
        Rv = []
        for i in range(depth):
            Rv.append(Rv_commence / pow(4, i))

        # Keep track of which nodes correspond to which electrodes
        nodes = {}

        # Generate the resistor ladder
        out = []
        out.append("****************************************")
        out.append("*         Resistor ladder start        *")
        out.append("****************************************")
        tmp = ".SUBCKT " + name
        for electrode in range(electrodes):
            tmp += " e" + str((electrode + 1))
        out.append(tmp)

        # Figure out which nodes correspond to electrodes
        for row in range(((electrodes + electrodes - 1) * 2 - 1) + 4 * padding):
            for col in range(depth):
                if col == 0 and row % 2 == 0:
                    actRow = row / 2
                    if actRow < (padding + (electrodes * 2) - 1):
                        segment = (actRow - padding)
                        if segment % 2 == 0 and segment >= 0:
                            nodes[col + (int(row / 2) * 5) + 1] = (int(segment / 2)
                                                                   + 1)

        # Step over each component adding as necessary
        for row in range(((electrodes + electrodes - 1) * 2 - 1) + 4 * padding):
            for col in range(depth):

                fromNode = col + (int(row / 2) * 5) + 1

                if (row % 2) == 0:
                    if (row / 2 >= padding and
                        row / 2 < (padding + (electrodes * 2) - 1) and
                        (row / 2 - padding) % 2 != 0):
                        value = Rr_insulator
                    else:
                        value = Rr_electrode

                    component = "RRAD_" + str(row + 1) + "_" + str(col + 1)
                    if col == (len(Rv) - 1):
                        toNode = 1000
                    else:
                        toNode = col + (int(row / 2) * 5) + 2
                else:
                    value = Rv[col]
                    toNode = col + (int(row / 2 + 1) * 5) + 1
                    component = "RVERT_" + str(row + 1) + "_" + str(col + 1)


                if fromNode in nodes:
                    fromNode = 'e' + str(nodes[fromNode])

                if toNode in nodes:
                    toNode = 'e' + str(nodes[toNode])


#                 out.append(str(component) + ' ' +
#                            str(fromNode) + ' ' +
#                            str(toNode) + ' ' +
#                            str(value))

                if type(value) == complex:
                    out.append(self.impedeor(str(component),
                                             str(fromNode),
                                             str(toNode),
                                             value))
                else:
                    out.append(str(component) + ' ' +
                               str(fromNode) + ' ' +
                               str(toNode) + ' ' +
                               str(value))


        out.append(".ENDS " + name)
        return out


    def subcircuit_faradaic(self, memristor=True, name='faradaic'):
        """
        Generates the ngspice compatible subcircuit named faradaic that simulates
        the faradic component in the interface. This includes the diode and
        memristor branches
        """
        i0 = self.parameterSet.faradaic_i0()
        n = self.parameterSet.faradaic_n()

        k = 1.38e-23
        T = self.parameterSet.temperature() + 273.15
        T = 300
        q = 1.60e-19
        Vt = (k * T) / q

        out = ["****************************************",
               "*        Faradaic branch start         *",
               "****************************************"]

        if memristor == True:
            cm = self.parameterSet.faradaic_CM()
            rm = self.parameterSet.faradaic_RM()
            out += [".SUBCKT " + name + " n1 n2",
                    ".PARAM Vt=" + str(Vt),
                    ".PARAM i0=" + str(i0),
                    ".PARAM n=" + str(n),
                    ".PARAM CM=" + str(cm),
                    ".PARAM RM=" + str(rm),
                    ".PARAM nVt=n*Vt",
                    "Bdm1 n1 n2 I=i0*(1-v(mset))*exp(v(n1,n2)/nVt)",
                    "Bdm2 n2 n1 I=i0*(1+v(mset))*exp(v(n2,n1)/nVt)",
                    "Bdm1cpy 0 mset I=i0*(1-v(mset))*exp(v(n1,n2)/nVt)",
                    "Bdm2cpy mset 0 I=i0*(1+v(mset))*exp(v(n2,n1)/nVt)",
                    "R_b n1 n2 1e10"
                    "C_M mset 0 cm",
                    "R_M mset 0 rm",
                    ".ENDS " + name]
        else:
            out += [".SUBCKT " + name + " n1 n2",
                    ".PARAM Vt=" + str(Vt),
                    ".PARAM i0=" + str(i0),
                    ".PARAM n=" + str(n),
                    ".PARAM nVt=n*Vt",
                    "Bdm1 n1 n2 I=i0*exp(v(n1,n2)/nVt)",
                    "Bdm2 n2 n1 I=i0*exp(v(n2,n1)/nVt)",
                    "R_b n1 n2 1e10",
                    ".ENDS " + name]

        return out



    def subcircuit_displacement(self,
                                fmin=1e-6,
                                fmax=1e6,
                                elementsPerDecade=3,
                                name='displacement',
                                bypassRes=1e10):
        """
        Generates the ngspice compatible subcircuit named fracpole ready for
        inclusion into a spice file
        """

        # Extend freq range so no funny business appears
        fmin /= 1000.00
        fmax *= 1000.00

        print(fmin)
        print(fmax)

        cpe_mag = self.parameterSet.displacement_mag()
        cpe_slope = self.parameterSet.displacement_slope()
        m = self.parameterSet.displacement_m()

        # Calculate the number of elements to place in this range
        numPts = (math.log10(fmax) - math.log10(fmin)) * elementsPerDecade

        # Calculate the frequency scaling factor
        k_f = math.exp((math.log(fmax) - math.log(fmin)) / numPts)

        # Generate the frequency positions for the cpe branches
        pts = []
        for i in range(int(numPts) + 1):
            pts.append(fmin * math.pow(k_f, i))

        # Determine k - the multiplicity factor
        k = math.pow(k_f, 1 / m)


        y_theta = ((math.pi / (m * math.log(k))) *
                   mpmath.sec(0.5 * math.pi * (1 - (2 / m))))

        out = []
        out.append("****************************************")
        out.append("*           Fracpole/CPE start         *")
        out.append("****************************************")

        fracpoleElements = []
        for point in pts:
            omega = 2 * math.pi * point
            Z = cpe_mag * math.pow(point, cpe_slope)
            R = Z
            C = math.pow((R / (y_theta * Z)), m) / (omega * R)
            fracpoleElements.append({'frequency': point, 'R': R, 'C': C})


        out.append(".SUBCKT " + name + " a b")
        for num, facpoleElement in enumerate(fracpoleElements):
            out.append("R" + str(num) + " a " + str(num + 1)
                       + " " + str(facpoleElement['R']))
            out.append("C" + str(num) + " " + str(num + 1)
                       + " b " + str(facpoleElement['C']))
        out.append("R" + str(num + 1) + " a b " + str(bypassRes))
        out.append(".ENDS " + name)

        return out


    def combine_subcircuits(self, input_elements, output_subcircuitName):
        """
        Combile an array of subcircuit names and spice components according
        to the nesting of the input array (input_subcircuitNames).

        E.g.
        Combine sub1 in series with a parallel combination of sub2 and sub3
        which is then in series with sub4

        input = ['sub1', ['sub2', 'sub3'], 'sub4']
        spice output:

        XC1 a n1 sub1
        XC2 n1 n2 sub2
        XC3 n1 n2 sub3
        XC4 n2 b sub4
        """

        out = []
        out.append("****************************************")
        out.append("*          Combine subcircuits         *")
        out.append("****************************************")
        out.append(".SUBCKT " + output_subcircuitName + " a b")
        nodeCount = 0
        elementCount = 1
        seriesLength = len(input_elements)

        for index, element in enumerate(input_elements):

            incCount = False

            # Determine name of this node
            if index == 0:
                thisNode = 'a'
            else:
                thisNode = 'n' + str(nodeCount)
                incCount = True

            # Determine name of next node
            if index == (seriesLength - 1):
                nextNode = 'b'
            else:
                nextNode = 'n' + str(nodeCount + 1)
                incCount = True


            if type(element) == list:
                for parallelElement in element:
                    out.append(self.as_spiceComponent(parallelElement,
                                                      thisNode,
                                                      nextNode,
                                                      elementCount))
                    elementCount += 1
            else:
                out.append(self.as_spiceComponent(element,
                                                  thisNode,
                                                  nextNode,
                                                  elementCount))
                elementCount += 1

            if incCount == True:
                nodeCount += 1


        out.append(".ENDS " + output_subcircuitName)

        return out


    def get_spiceModel(self):
        out = []
        out.append('electrodeModel')
        if self.includes_diode:
            out += self.subcircuit_faradaic(memristor=self.includes_memristor)

        out += self.subcircuit_ladder()
        out += self.subcircuit_displacement()

#         r_series = SpiceComponent('R', self.parameterSet.seriesResistance())
        r_series = SpiceComponent('R', self.parameterSet.seriesResistance())
        if self.includes_diode:
            model_layout = [['faradaic', 'displacement'], r_series]
        else:
            model_layout = ['displacement', r_series]

        out += self.combine_subcircuits(model_layout, 'interface')

        for autoCircuit in self.autoCircuits:
            out += autoCircuit

        out.append("****************************************")
        out.append("*          Circuit description         *")
        out.append("****************************************")
        out.append('X_ladder w1 w2 w3 w4 w5 w6 w7 w8 ladder')
        for i in range(1, 9):
            out.append('X_interface' + str(i) + ' ' +
                       'e' + str(i) + ' ' +
                       'w' + str(i) + ' ' +
                       'interface')
        return out
