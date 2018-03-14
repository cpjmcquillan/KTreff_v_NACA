import os
import sys

import pandas as pd
import matplotlib.pyplot as plt


class XFoilPost(object):
    """
    Object to manage post processing of Xfoil runs.
    """
    def __init__(self, folder_path, folder_names):
        self.folder_path = folder_path
        self.folder_names = folder_names
        self.polar_data = {}
        self.cp_data = {}
        self.dump_data = {}

    def __call__(self, *args, **kwargs):
        for folder_name in self.folder_names:
            self._read_polar(folder_name)
            self._read_data(folder_name, [-2.0, 0.0, 4.0, 8.0, 12.0, 16.0, 22.0, 26.0, 28.0], 'cp')
            self._read_data(folder_name, [-2.0, 0.0, 4.0, 8.0, 12.0, 16.0, 22.0, 26.0, 28.0], 'bl')
        self._write_polar()
        self._write_cp()
        self._write_dump()
        self._plot_cl_alpha()
        self._plot_cd_alpha()
        self._plot_ldratio_alpha()
        self._plot_transition_lower_alpha()
        self._plot_transition_upper_alpha()
        self._plot_cp_x()
        self._plot_cf_x()

    def _read_polar(self, folder_name):
        file_path = os.path.join(self.folder_path, folder_name, '{}_polar.dat'.format(folder_name))
        f = open(file_path)
        lines = f.readlines()
        headers = lines[10].strip().strip('\n').split(' ')
        headers = [header for header in headers if len(header)]
        rows = [row.strip().strip('\n').split(' ') for row in lines[12:]]
        data = []
        for row in rows:
            row = [float(cell) for cell in row if len(cell)]
            data.append(row)
        f.close()
        self.polar_data[folder_name] = pd.DataFrame(data, columns=headers)
        self.polar_data[folder_name]['L/D'] = self.polar_data[folder_name]['CL'] / self.polar_data[folder_name]['CD']

    def _read_data(self, folder_name, alphas, ext):
        for alpha in alphas:
            file_path = os.path.join(self.folder_path, folder_name, '{}_alpha={}.{}'.format(folder_name, alpha, ext))
            if os.path.exists(file_path):
                f = open(file_path)
                lines = f.readlines()
                headers = [header for header in lines[0].strip().strip('\n').split(' ')[1:] if len(header)]
                rows = [row.strip().strip('\n').split(' ') for row in lines[1:]]
                data = []
                for row in rows:
                    row = [float(cell) for cell in row if len(cell)]
                    data.append(row)
                f.close()

                if ext == 'cp':
                    if folder_name not in self.cp_data.keys():
                        self.cp_data[folder_name] = {}
                    self.cp_data[folder_name][alpha] = pd.DataFrame(data, columns=headers)

                if ext == 'bl':
                    if folder_name not in self.dump_data.keys():
                        self.dump_data[folder_name] = {}
                    self.dump_data[folder_name][alpha] = pd.DataFrame(data, columns=headers)

    def _write_polar(self):
        writer = pd.ExcelWriter(os.path.join(self.folder_path, 'polar.xlsx'))
        f = open(os.path.join(self.folder_path, 'stall_angle.txt'), 'w')
        for name in self.folder_names:
            data = self.polar_data[name]
            data.to_excel(writer, name)
            f.write('{} - max Cl: {} @ alpha: {}\n'.format(name,
                                                           data['CL'].max(), data.loc[data['CL'].idxmax()]['alpha']))
        f.close()

    def _write_dump(self):
        writer = pd.ExcelWriter(os.path.join(self.folder_path, 'dump.xlsx'))
        for name in self.folder_names:
            for key, data in self.dump_data[name].iteritems():
                data.to_excel(writer, '{}alpha={}'.format(name, key))

    def _write_cp(self):
        writer = pd.ExcelWriter(os.path.join(self.folder_path, 'cp.xlsx'))
        for name in self.folder_names:
            for key, data in self.cp_data[name].iteritems():
                data.to_excel(writer, '{}alpha={}'.format(name, key))

    def _plot_cl_alpha(self):
        for name, data in self.polar_data.iteritems():
            plt.plot(list(data['alpha']), list(data['CL']), label=name)
        plt.xlabel('Angle of attack, alpha')
        plt.ylabel('Lift coefficient, Cl')
        plt.title('Cl vs alpha')
        plt.legend(loc='best', fontsize='small')
        plt.savefig(os.path.join(self.folder_path, 'Cl vs alpha.png'))
        plt.gcf().clear()

    def _plot_cd_alpha(self):
        for name, data in self.polar_data.iteritems():
            plt.plot(list(data['alpha']), list(data['CD']), label=name)
        plt.xlabel('Angle of attack, alpha')
        plt.ylabel('Drag coefficient, Cd')
        plt.title('Cd vs alpha')
        plt.legend(loc='best', fontsize='small')
        plt.savefig(os.path.join(self.folder_path, 'Cd vs alpha.png'))
        plt.gcf().clear()

    def _plot_ldratio_alpha(self):
        for name, data in self.polar_data.iteritems():
            plt.plot(list(data['alpha']), list(data['L/D']), label=name)
        plt.xlabel('Angle of attack, alpha')
        plt.ylabel('Lift to drag ratio, L/D')
        plt.title('L/D vs alpha')
        plt.legend(loc='best', fontsize='small')
        plt.savefig(os.path.join(self.folder_path, 'L_D vs alpha.png'))
        plt.gcf().clear()

    def _plot_transition_lower_alpha(self):
        for name, data in self.polar_data.iteritems():
            plt.plot(list(data['Bot_Xtr']), list(data['alpha']), label='{}_lower'.format(name))
        plt.ylabel('Angle of attack, alpha')
        plt.xlabel('Transition point, Xtr')
        plt.title('Alpha vs lower surface transition')
        plt.legend(loc='best', fontsize='small')
        plt.savefig(os.path.join(self.folder_path, 'Alpha vs lower surface transition.png'))
        plt.gcf().clear()

    def _plot_transition_upper_alpha(self):
        for name, data in self.polar_data.iteritems():
            plt.plot(list(data['Top_Xtr']), list(data['alpha']), label='{}_upper'.format(name))
        plt.ylabel('Angle of attack, alpha')
        plt.xlabel('Transition point, Xtr')
        plt.title('Alpha vs upper surface transition')
        plt.legend(loc='best', fontsize='small')
        plt.savefig(os.path.join(self.folder_path, 'Alpha vs upper surface transition.png'))
        plt.gcf().clear()

    def _plot_cp_x(self):
        for alpha in self.cp_data[self.folder_names[0]].keys():
            for name in self.folder_names:
                plt.plot(list(self.cp_data[name][alpha]['x']), list(self.cp_data[name][alpha]['Cp']), label=name)
            plt.xlabel('x')
            plt.ylabel('Pressure coefficient, Cp')
            plt.title('Pressure distribution alpha={}'.format(alpha))
            plt.legend(loc='best', fontsize='small')
            plt.savefig(os.path.join(self.folder_path, 'Pressure distribution alpha={}.png'.format(alpha)))
            plt.gcf().clear()

    def _plot_cf_x(self):
        for alpha in self.dump_data[self.folder_names[0]].keys():
            for name in self.folder_names:
                plt.plot(list(self.dump_data[name][alpha]['x']), list(self.dump_data[name][alpha]['Cf']), label=name)
            plt.xlabel('x')
            plt.ylabel('Skin friction coefficient, Cf')
            plt.title('Skin friction distribution alpha={}'.format(alpha))
            plt.legend(loc='best', fontsize='small')
            plt.savefig(os.path.join(self.folder_path, 'Cf distribution alpha={}.png'.format(alpha)))
            plt.gcf().clear()


if __name__ == '__main__':
    xfoil_post = XFoilPost(sys.argv[1], ['aerofoil', 'naca1510'])
    xfoil_post()
