import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ktreff_aerofoil import KarmanTrefftzAerofoil
from naca_aerofoil import Naca4DigitAerofoil


def compare_ktreff_naca(folder_path, alpha=0.0, eps=0.06, beta=0.02, tau=0.15, n=150, output_naca=False):
    """
    Function to compare a Karman-Trefftz aerofoil against the most similar 4 digit NACA aerofoil.
    :param folder_path: path of folder to save plots.
    :param alpha: angle of incidence.
    :param eps:
    :param beta:
    :param tau:
    :param n: number of points to generate aerofoils with.
    :return:
    """
    # Initialise and call ktreff and naca aerofoils objects and methods.
    ktreff = KarmanTrefftzAerofoil(alpha=alpha, eps=eps, beta=beta, tau=tau, n=n)
    ktreff()
    naca_camber, naca_camber_x, naca_thickness = ktreff.get_naca_digits()
    naca = Naca4DigitAerofoil(naca_camber, naca_camber_x, naca_thickness, int(n))
    naca()

    # Generate and save geometry comparison plot
    ktreff_data = ktreff.get_data(True)
    naca_data = naca.get_data()[:-1]    # Fudge to avoid line back to (0, 0)
    naca_data[0][1] = 0.0               # Fudge to remove -0.0

    # Generate xlsx file
    writer = pd.ExcelWriter(os.path.join(folder_path, '{}.xlsx'.format(ktreff.get_name())))
    data, camber, thickness = ktreff.get_excel()
    data.to_excel(writer, 'data')
    camber.to_excel(writer, 'camber')
    thickness.to_excel(writer, 'thickness')

    # Write .dat files of coordinates for both aerofoils
    np.savetxt('aerofoil.dat', ktreff_data)
    np.savetxt('{}.dat'.format(naca.get_name()), naca_data)

    title = '{} vs {}'.format(ktreff.get_name(), naca.get_name())
    plt.plot(ktreff_data[:, 0], ktreff_data[:, 1], 'k-', label='ktreff')
    plt.plot(naca_data[:, 0], naca_data[:, 1], 'b-', label='naca')
    plt.xlabel('x/c')
    plt.ylabel('y/c')
    plt.title(title)
    plt.legend(loc='best', fontsize='small')
    plt.savefig(os.path.join(folder_path, '{}.png'.format(title)))
    plt.gcf().clear()

    # Generate and save ktreff plot
    title = ktreff.get_name()
    plt.plot(ktreff.lower[:, 0], ktreff.lower[:, 1], 'b-', label='lower')
    plt.plot(ktreff.upper[:, 0], ktreff.upper[:, 1], 'g-', label='upper')
    plt.plot(ktreff.camber[:, 0], ktreff.camber[:, 1], 'r-', label='camber')
    plt.xlabel('x/c')
    plt.ylabel('y/c')
    plt.title(title)
    plt.legend(loc='best', fontsize='small')
    plt.savefig(os.path.join(folder_path, '{}.png'.format(title)))
    plt.gcf().clear()

    # Generate and save ktreff Cp distribution
    ktreff_data = ktreff.get_data(False)
    title = '{}_Cp'.format(ktreff.get_name())
    plt.plot(ktreff_data[:, 0], ktreff_data[:, 2], 'k-')
    plt.xlabel('x/c')
    plt.ylabel('Cp')
    plt.title(title)
    plt.savefig(os.path.join(folder_path, '{}.png'.format(title)))
    plt.gcf().clear()

    if output_naca:
        return '{}{}{}'.format(naca.camber, naca.camber_x, naca.thickness)


if __name__ == '__main__':
    compare_ktreff_naca(folder_path=sys.argv[1],
                        alpha=sys.argv[2], eps=sys.argv[3], beta=sys.argv[4], tau=sys.argv[5], n=sys.argv[6])
