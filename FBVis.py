import fileinput
import glob
import matplotlib.pyplot as plt
import numpy as np
import os

class FBVis:
    def __init__(self):
        self.prefix = self._get_prefix()
        self.it_data, self.parameters, self.experiment = self._parse(self.prefix)

    def _get_prefix(self):
        return glob.glob('*.in')[0].split('.')[0]

    def _parse(self, job_prefix):
        out_filenms = glob.glob('*.out')
        concat_filenm = self._concatenate(out_filenms)

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
        
