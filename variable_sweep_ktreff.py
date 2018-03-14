import os
import sys

import matplotlib.pyplot as plt
import pandas as pd

from ktreff_aerofoil import KarmanTrefftzAerofoil


def variable_sweep_ktreff(folder_path, **kwargs):
    """
    Fixture that generates Karman-Trefftz aerofoils at each of the variables.
    Compares each in a plot and writes a .csv containing data.
    Arguments can be number (int/float) or a list of values.
    Comparisons made by sweeping the list of values.
    Vary only one of eps/beta/tau at a time. (i.e only one argument should be a list).
    """
    # Called from __main__
    if 'variables' in kwargs.keys():
        parsed_variables = []
        for variable in kwargs['variables']:
            if len(variable.split(' ')) > 1:
                variable = variable.split(' ')
            parsed_variables.append(variable)
        kwargs['alpha'] = parsed_variables[0]
        kwargs['eps'] = parsed_variables[1]
        kwargs['beta'] = parsed_variables[2]
        kwargs['tau'] = parsed_variables[3]
        kwargs['n'] = parsed_variables[4]
        kwargs.pop('variables')

    # Iterate over arguments to determine which is a list (i.e which variable to vary)
    for key, arg in kwargs.iteritems():
        if type(arg) is list:
            sweep_variable_name = key
            sweep_variable_values = arg
            break

    # Table of aerofoil data
    table = pd.DataFrame(columns=['alpha', 'eps', 'beta', 'tau',
                                  'max_camber', 'max_camber_x', 'max_thickness', 'Cl'],
                         index=[n for n in range(len(sweep_variable_values))])

    # Generate ktreff aerofoil for each value of variable and write data to excel file.
    # Generate plot comparing aerofoils.
    for idx, value in enumerate(sweep_variable_values):
        kwargs[sweep_variable_name] = value
        aerofoil = KarmanTrefftzAerofoil(**kwargs)
        aerofoil()
        label = '{}={}'.format(sweep_variable_name, value)
        if idx == 0:
            title = ''.join([elem.strip(',') for elem in aerofoil.get_name().split(label)])
            writer = pd.ExcelWriter(os.path.join(folder_path, '{}.xlsx'.format(title)), engine='xlsxwriter')
        table.loc[idx] = [aerofoil.alpha, aerofoil.eps, aerofoil.beta, aerofoil.tau,
                          aerofoil.get_max_camber()[1], aerofoil.get_max_camber()[0], aerofoil.get_max_thickness(),
                          aerofoil.Cl]
        data = aerofoil.get_data(False)
        pd_data = pd.DataFrame(data, columns=['x', 'y', 'Cp'])
        pd_data.to_excel(writer, label)
        plt.plot(data[:, 0], data[:, 1], label=label)
        plt.legend(loc='best', fontsize='small')

    plt.title(title)
    plt.xlabel('x/c')
    plt.ylabel('y/c')
    plt.savefig(os.path.join(folder_path, '{}.png'.format(title)))
    plt.gcf().clear()

    plt.title('Maximum camber vs {}'.format(sweep_variable_name))
    plt.xlabel(sweep_variable_name)
    plt.ylabel('Maximum camber')
    plt.plot(list(table[sweep_variable_name]), list(table['max_camber']))
    plt.savefig(os.path.join(folder_path, 'Maximum camber vs {}.png'.format(sweep_variable_name)))
    plt.gcf().clear()

    plt.title('Maximum camber x location vs {}'.format(sweep_variable_name))
    plt.xlabel(sweep_variable_name)
    plt.ylabel('Maximum camber x location')
    plt.plot(list(table[sweep_variable_name]), list(table['max_camber_x']))
    plt.savefig(os.path.join(folder_path, 'Maximum camber location vs {}.png'.format(sweep_variable_name)))
    plt.gcf().clear()

    plt.title('Maximum thickness vs {}'.format(sweep_variable_name))
    plt.xlabel(sweep_variable_name)
    plt.ylabel('Maximum thickness')
    plt.plot(list(table[sweep_variable_name]), list(table['max_thickness']))
    plt.savefig(os.path.join(folder_path, 'Maximum thickness vs {}.png'.format(sweep_variable_name)))
    plt.gcf().clear()

    table.to_excel(writer, 'table')


if __name__ == '__main__':
    variable_sweep_ktreff(folder_path=sys.argv[1], variables=sys.argv[2:])
