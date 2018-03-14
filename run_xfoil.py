import os
import sys

import numpy as np

XFOIL_PATH = '/Applications/University/Xfoil.app/Contents/Resources/xfoil'


def run_xfoil(folder_path,
              reynolds_number, mach_number,
              min_alpha, max_alpha, step_alpha,
              iterations,
              aerofoil_filename=None, naca_4_name='1510'):
    """
    Function to generate commands.in file and then run Xfoil.
    """
    folder_name = aerofoil_filename if aerofoil_filename is not None else 'naca{}'.format(naca_4_name)
    name = folder_name.split('.dat')[0]
    output_folder = os.path.join(folder_path, name)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    command_filepath = os.path.abspath(os.path.join(output_folder, 'commands.in'))
    load_data = 'load {}\n'.format(os.path.abspath(os.path.join(folder_path, aerofoil_filename))) \
        if aerofoil_filename is not None else 'naca {}\n'.format(naca_4_name)

    output_file = os.path.abspath(os.path.join(output_folder, '{}_polar.dat'.format(name)))

    with open(command_filepath, 'w') as command:
        command.write(load_data)
        if aerofoil_filename is not None:
            command.write('aerofoil\n')
            command.write('panel\n')
        command.write('oper\n')
        command.write('visc {}\n'.format(reynolds_number))
        command.write('M {}\n'.format(mach_number))
        command.write('type 1\n')
        command.write('Pacc \n{}\n \n'.format(output_file))
        command.write('iter {}\n'.format(iterations))

        for alpha in np.arange(min_alpha, max_alpha, step_alpha):
            alpha = np.round(alpha, 2)
            command.write('Alfa {}\n'.format(alpha))
            if not (np.round(alpha, 2) * 10) % 5:   # Only write files for .5, .0 alpha (i.e 0.0, 0.5 etc)
                dump_file = os.path.abspath(os.path.join(output_folder, '{}_alpha={}.bl'.format(name, alpha)))
                cp_file = os.path.abspath(os.path.join(output_folder, '{}_alpha={}.cp'.format(name, alpha)))
                command.write('DUMP {}\n'.format(dump_file))
                command.write('CPWR {}\n'.format(cp_file))

        command.write('\n')
        command.write('quit\n')

    run_command = '{} < {}'.format(XFOIL_PATH, command_filepath)

    os.system(run_command)


if __name__ == '__main__':
    if sys.argv[7] == '-naca':
        run_xfoil(folder_path=sys.argv[1],
                  reynolds_number=sys.argv[2], mach_number=sys.argv[3],
                  min_alpha=sys.argv[4], max_alpha=sys.argv[5], step_alpha=sys.argv[6],
                  iterations=sys.argv[6],
                  naca_4_name=sys.argv[8])
    else:
        run_xfoil(folder_path=sys.argv[1],
                  reynolds_number=sys.argv[2], mach_number=sys.argv[3],
                  min_alpha=sys.argv[4], max_alpha=sys.argv[5], step_alpha=sys.argv[6],
                  iterations=sys.argv[6],
                  aerofoil_filename=sys.argv[7])
