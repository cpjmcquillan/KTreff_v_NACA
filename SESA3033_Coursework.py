import sys

import numpy as np

from karman_vs_naca import compare_ktreff_naca as compare
from variable_sweep_ktreff import variable_sweep_ktreff as sweep
from doublet_panel_order import dpan_order as doublet
from run_xfoil import run_xfoil
from xfoil_post import XFoilPost

folder_path = sys.argv[1]

naca_digits = compare(folder_path, alpha=0.0, eps=0.06, beta=0.02, tau=0.15, n=150, output_naca=True)

sweep(folder_path, alpha=0.0, eps=[0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08], beta=0.02, tau=0.15, n=150)
sweep(folder_path, alpha=0.0, eps=0.06, beta=[0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08], tau=0.15, n=150)

doublet(folder_path, alpha=3.0, eps=0.06, beta=0.02, tau=0.15, n_list=np.arange(10, 330, 10), dpan=True)

run_xfoil(folder_path, 50000000, 0.0,
          -2.0, 30.0, 0.1,
          1000,
          aerofoil_filename='aerofoil.dat')

run_xfoil(folder_path, 50000000, 0.0,
          -2.0, 30.0, 0.1,
          1000,
          naca_4_name='1510')

xfoil_post = XFoilPost(folder_path, ['aerofoil', 'naca1510'])
xfoil_post()
