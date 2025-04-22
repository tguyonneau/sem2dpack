import numpy as np

class Input:
    def __init__(self, path):
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
    
    def write_general_parameters(self):
        general_param = self.general_dic.keys()
        input_file = open(self.path, 'a')
        input_file.write("\n")
        input_file.write("\n #---------- General parameters ----------")
        input_file.write("\n")
        input_file.write("&GENERAL")
        for param in general_param:
            if self.general_dic[param] != None :
                if type(self.general_dic[param]) is str:
                    input_file.write(f" {param}='{self.general_dic[param]}',")
                else :
                    input_file.write(f" {param}={self.general_dic[param]},") 
        input_file.close()
        input_file = open(self.path, 'rb+')
        input_file.seek(-1,2)
        input_file.truncate()
        input_file.close()
        input_file = open(self.path, 'a')
        input_file.write('/')
        input_file.close()
        

        