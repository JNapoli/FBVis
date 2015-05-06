import fileinput
import glob
import linecache
import matplotlib.pyplot as plt
import numpy as np
import os

class FBVis:
    def __init__(self, target):
        self.target = target
        self.prefix = self._get_prefix()
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
        f.close()

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
