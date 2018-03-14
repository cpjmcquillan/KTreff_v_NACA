import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress

from ktreff_aerofoil import KarmanTrefftzAerofoil


def dpan_order(folder_path, **kwargs):
    """
    Function to identify order of accuracy of doublet panel method.
    """
    n_list = kwargs['n_list'].split(' ') if type(kwargs['n_list']) is str else kwargs['n_list']
    kwargs.pop('n_list')

    table = pd.DataFrame(columns=['alpha', 'eps', 'beta', 'tau', 'n',
                                  'cl', 'dpan_cl', 'error',
                                  'log_n', 'log_error'],
                         index=[i for i in range(len(n_list))])

    for idx, n in enumerate(n_list):
        kwargs['n'] = n
        aerofoil = KarmanTrefftzAerofoil(**kwargs)
        aerofoil()
        label = 'n={}'.format(n)
        if idx == 0:
            title = ''.join([elem.strip(',') for elem in aerofoil.get_name().split(label)])
            writer = pd.ExcelWriter(os.path.join(folder_path, '{}_order.xlsx'.format(title)))
        error = aerofoil.dpan_cl - aerofoil.Cl
        table.loc[idx] = [aerofoil.alpha, aerofoil.eps, aerofoil.beta, aerofoil.tau, aerofoil.n,
                          aerofoil.Cl, aerofoil.dpan_cl, error,
                          np.log(int(n)), np.log(error)]

    table.to_excel(writer, 'Cl_error')
    log_n = table['log_n'].values.tolist()
    log_error = table['log_error'].values.tolist()
    slope, intercept, r_value, p_value, std_err = linregress(log_n, log_error)

    plt.plot(log_n, log_error, 'k-')
    plt.title(title)
    plt.xlabel('log n')
    plt.ylabel('log Cl error')
    plt.annotate('y={}x+{}'.format(slope, intercept),
                 xy=(1, 1),
                 xytext=(0.5, 0.8),
                 xycoords='axes fraction',
                 textcoords='axes fraction')
    plt.savefig('{}_order.png'.format(title))


if __name__ == '__main__':
    dpan_order(folder_path=sys.argv[1],
               alpha=sys.argv[2], eps=sys.argv[3], beta=sys.argv[4], tau=sys.argv[5],
               n_list=sys.argv[6], dpan=True)
