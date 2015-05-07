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
        
        with open(concat_filenm, 'r') as f:
            raw_dat = f.readlines()
            params = self._parse_params(raw_dat)
            exp_dat = self._parse_exp_dat(raw_dat)
        f.close()

        return 0, params, exp_dat

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

