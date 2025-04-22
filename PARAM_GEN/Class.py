import numpy as np
import os

class Input:
    def __init__(self, path):
        os.remove(path)
        self.path = path

    def set_general_parameters(self, ndof, ItInfo, ngll=5, iexec=1, fmax=None, title=None, verbose='1011'):
        self.general_dic = {}
        self.general_dic['ndof'] = ndof
        self.general_dic['ItInfo'] = ItInfo
        self.general_dic['ngll'] = ngll
        self.general_dic['iexec'] = iexec
        self.general_dic['fmax'] = fmax
        self.general_dic['title'] = title
        self.general_dic['verbose'] = verbose

    def set_time_scheme(self, TotalTime, dt, courant, kind='leapfrog'):
        self.time_scheme_dic = {}
        self.time_scheme_dic['TotalTime'] = TotalTime
        self.time_scheme_dic['dt'] = dt
        self.time_scheme_dic['courant'] = courant
        self.time_scheme_dic['kind'] = kind

    def set_materials(self, mat_list):
        self.mat_list = mat_list

    def write_file(self):
        self.write_general_parameters()
        self.write_time_scheme()
        self.write_materials()

    def write_from_dictionnary(self, target_dic):
        input_file = open(self.path, 'a')
        params = target_dic.keys()
        for param in params:
            if target_dic[param] != None :
                if type(target_dic[param]) is str:
                    input_file.write(f" {param}='{target_dic[param]}',")
                else :
                    input_file.write(f" {param}={target_dic[param]},") 
        input_file.close()
        input_file = open(self.path, 'rb+')
        input_file.seek(-1,2)
        input_file.truncate()
        input_file.close()
        input_file = open(self.path, 'a')
        input_file.write(' /')
        input_file.close()
    
    def write_general_parameters(self):
        input_file = open(self.path, 'a')
        input_file.write("\n")
        input_file.write("\n #---------- General parameters ----------")
        input_file.write("\n")
        input_file.write("&GENERAL")
        input_file.close()
        self.write_from_dictionnary(self.general_dic)

    def write_time_scheme(self):
        input_file = open(self.path, 'a')
        input_file.write("\n")
        input_file.write("\n #---------- Time scheme settings ----------")
        input_file.write("\n")
        input_file.write("&TIME")
        input_file.close()
        self.write_from_dictionnary(self.time_scheme_dic)

    def write_materials(self):
        input_file = open(self.path, 'a')
        input_file.write("\n")
        input_file.write("\n #---------- Material parameters ----------")
        input_file.close()
        for m in self.mat_list:
            input_file = open(self.path, 'a')
            input_file.write(f"\n&MATERIAL tag={m.tag}, kind='{m.kind}' /")
            if m.kind == 'ELAST':
                input_file.write("\n&MAT_ELASTIC")
            elif m.kind == 'IWAN':
                input_file.write("\n&MAT_IWAN")
            input_file.close()
            self.write_from_dictionnary(m.mat_dic)
            


class Material():
    def __init__(self, tag, kind):
        self.tag = tag
        self.kind = kind
        self.mat_dic = {}
        if kind == 'ELAST':
            self.mat_dic['rho'] = 0
            self.mat_dic['cp'] = 0
            self.mat_dic['cs'] = 0
        elif kind == 'IWAN':
            self.mat_dic['rho'] = 0
            self.mat_dic['cp'] = 0
            self.mat_dic['cs'] = 0
            self.mat_dic['Nspr'] = 0
            self.mat_dic['gref'] = 0

    def set_properties(self, **kwargs):
        for key, val in kwargs.items():
            self.mat_dic[key] = val
        



Test = Input('./PARAM_GEN/Par.inp')
Test.set_general_parameters(ndof=2, ItInfo=1000, verbose='1101')
Test.set_time_scheme(TotalTime=10, dt=1e-5, courant=0.3)


Mat = Material(1, "IWAN")
Mat.set_properties(rho=1000, cp=100, cs=200, Nspr=50, gref=0.000365)

Mat2 = Material(2, 'ELAST')    
Mat2.set_properties(rho=1, cp=2, cs=3)

Test.set_materials([Mat,Mat2])

Test.write_file()