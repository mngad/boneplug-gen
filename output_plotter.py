import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.lines as mlines
import os



fig, ax = plt.subplots(1, 1)
fileLoc = os.getcwd() + '/'
for filename in os.listdir(fileLoc):
    if filename.endswith("parsed.txt"):
        df = pd.read_csv(
                filename,
                header=0,
                sep=',')

        plt.plot(df['disp'],df['force'], label=filename[:-11].replace('high_cart_pfit_low_fict__','').replace('_','.'))


plt.ylabel('Force (N)')
plt.xlabel('Displacement (mm)')
plt.legend()
#plt.show()
plt.savefig('uni_pfit.pdf', dpi=320, facecolor='w', edgecolor='w',
    orientation='landscape', papertype=None, format=None,
    transparent=False, bbox_inches=None, pad_inches=1,
    frameon=None)