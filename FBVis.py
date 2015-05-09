import fileinput, glob
import matplotlib.pyplot as plt
import numpy as np
import os

class FBVis:
    units = {'Density':'(kg m^-3)',
             'Enthalpy of Vaporization':'(kJ mol^-1)',
             'Thermal Expansion Coefficient':'(10^-4 K^-1)',
             'Isothermal Compressibility':'(10^-6 bar^-1)',
             'Isobaric Heat Capacity':'(cal mol^-1 K^-1)',
             'Dielectric Constant':''}

    def __init__(self):
        self.prefix = self._get_prefix()
        self.properties = self._load_properties()
        self.it_data, self.parameters, self.experiment = self._parse(self.prefix)

    def _get_prefix(self):
        """
        There should be only one FB input file in the working directory.
        """
        return glob.glob('*.in')[0].split('.')[0]

    def _parse(self, job_prefix):
        out_filenms = glob.glob('*.out')
        concat_filenm = self._concatenate(out_filenms)
        raw_dat = self._get_raw_dat()       
        params = self._parse_params(raw_dat)
        exp_dat = self._parse_exp_dat(raw_dat)
        sim_dat = self._parse_sim_dat(raw_dat)

        return sim_dat, params, exp_dat

    def _concatenate(self, filenms):
        """
        Concatenate all files in filenms into one txt file.
        """
        out_name = 'compiled.out'

        with open(out_name, 'w') as fout:
            for line in fileinput.input(filenms):
                fout.write(line)
        fout.close()

        return out_name

    def _load_properties(self):
        with open('props.dat', 'r') as f:
            props = [line.strip() for line in f]        
        f.close()
        
        return props

    def _parse_params(self, raw_dat):
        """
        Parse parameter names and indeces. 
        """
        params = []
        
        for i, line in enumerate(raw_dat):
            if 'Starting parameter indices, physical values and IDs' in line:
                parsed = False
                current = i + 2

                while not parsed:
                    fields = raw_dat[current].split()

                    if fields[0].isdigit():
                        params.append((int(fields[0]), float(fields[2]), fields[-1]))
                        current += 1
                    else:        
                        # Reached end of parameter block            
                        parsed = True 
        return params        

    def _parse_exp_dat(self, raw_dat):
        exp_dat = {}
        flag = 'Temperature  Pressure  Reference  Calculated +- Stdev'

        for prop in self.properties:
            for i, line in enumerate(raw_dat):
                if prop in line and flag in raw_dat[i+1]:
                    # Parse experimental data for prop
                    parsed = False
                    current = i + 3
                    temp_dat = []

                    while not parsed:
                        fields = raw_dat[current].split()

                        if fields[0][0].isdigit():
                            T = float(fields[0])
                            press = float(fields[1])
                            ref = float(fields[3])
                            temp_dat.append((T, press, ref))
                            current += 1
                        else:
                            parsed = True

                    exp_dat[prop] = temp_dat
                    break
        
        return exp_dat

    def _parse_sim_dat(self, raw_dat):
        sim_dat = {}
        
        for prop in self.properties:
            sim_dat[prop] = []            

            for i, line in enumerate(raw_dat):
                flag = 'Liquid ' + prop + ' ' + units[prop]  
                if flag in line:
                    parsed = False
                    current = i + 3
                    temp_dat = []

                    while not parsed:
                        fields = raw_dat[current].split()
                        
                        if fields[0][0].isdigit():
                            T = float(fields[0])
                            press = float(fields[1])
                            val = float(fields[4])
                            err = float(fields[6])
                            temp_dat.append((T, press, val, err))
                            current += 1
                        else:
                            parsed = False

                    sim_dat[prop].append(np.array(temp_dat))

        return sim_dat
        
    def _get_raw_dat(self):
        out_file = open('compiled.out', 'r')
        raw_dat = out_file.readlines()
        out_file.close()
        return raw_dat   

    def param_deviations(self):
        num_params = len(self.parameters)
        step_file = open('param_steps.dat', 'w')
        raw_dat = self._get_raw_dat()
        step_line_idxs = [(i, line) for i, line in enumerate(raw_dat) if 'Physical Parameters (Current + Step = Next)' in line]
        param_steps = []

        for occur in step_line_idxs:
            for l in raw_dat[occur[0]:(occur[0]+num_params+2)]:
                param_steps.append(l)

        param_labels = [elem[-1] for elem in self.parameters]
        diffs = {}

        for lab in param_labels:
            # First field in key's value is the original paramater
            # value. Second field is a list of percent differences.
            diffs[lab] = [0, []]

            for line in param_steps:
                if lab in line and diffs[lab][0] == 0:
                    fields = line.split()
                    diffs[lab][0] = float(fields[2])
                    diffs[lab][1].append(0.0)
                elif lab in line:
                    value = float(line.split()[2])
                    diffs[lab][1].append((value - diffs[lab][0]) / diffs[lab][0] * 100)                    

            plt.figure()
            colors = plt.get_cmap('spectral')(np.linspace(0,1.0,num_params))

            for k, color in zip(diffs.keys(), colors):
                plt.plot(np.array(diffs[k][1]), '--o', label=k, color=color, linewidth=2, markersize=10) 
                
            plt.legend(loc=0)
            plt.title('Parameter deviations from original values')
            plt.xlabel('Iteration')
            plt.ylabel('% difference from original')
            plt.savefig('parameter_deviations.png', dpi=300)
            plt.show()
