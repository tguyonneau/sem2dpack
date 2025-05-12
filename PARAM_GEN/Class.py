import numpy as np
import os
from Functions import *
from typing import Iterable

class Input:
    def __init__(self, path):
        try :
            os.remove(path)
        except FileNotFoundError:
            pass
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

    def set_mesh(self, mesh):
        self.mesh = mesh
    
    def set_BC(self, BC_list):
        self.BC_list = BC_list

    def set_materials(self, mat_list):
        self.mat_list = mat_list

    def set_receivers(self, file, isamp, field, AtNode, extra):
        self.rec_dic = {}
        self.rec_dic['file'] = file
        self.rec_dic['isamp'] = isamp
        self.rec_dic['field'] = field
        self.rec_dic['AtNode'] = AtNode
        self.rec_dic['extra'] = extra
    
    def set_snapshot(self, itd, fields, components, ps=False, bin=False):
        self.snap_dic = {}
        self.snap_dic['itd'] = itd
        self.snap_dic['fields'] = fields
        self.snap_dic['components'] = components
        self.snap_dic['ps'] = ps
        self.snap_dic['bin'] = bin
    
    def write_file(self):
        self.write_general_parameters()
        self.write_mesh()
        self.write_BC()
        self.write_materials()
        self.write_time_scheme()
        self.write_receivers()
        self.write_snapshot()

    def write_from_dictionnary(self, target_dic):
        input_file = open(self.path, 'a')
        params = target_dic.keys()
        for param in params:
            if target_dic[param] != None :
                if type(target_dic[param]) is str:
                    input_file.write(f" {param}='{target_dic[param]}',")
                elif type(target_dic[param]) is bool:
                    if target_dic[param] :
                        input_file.write(f" {param}=T,")
                    else :
                        input_file.write(f" {param}=F,")
                elif isinstance(target_dic[param],STF) :
                    input_file.write(f" {param}='{target_dic[param].kind}',")
                else :
                    if isinstance(target_dic[param], Iterable):
                        input_file.write(f" {param}=")
                        for val in target_dic[param] :
                            if type(val) is float :
                                mantissa, exponent = get_scientific_components(val)
                                input_file.write(f"{mantissa}d{exponent},")
                            else :
                                input_file.write(f"{val},")

                    else :
                        if type(target_dic[param]) is float :
                            mantissa, exponent = get_scientific_components(target_dic[param])
                            input_file.write(f" {param}={mantissa}d{exponent},")
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
        input_file.write("\n&GENERAL")
        input_file.close()
        self.write_from_dictionnary(self.general_dic)

    def write_mesh(self):
        input_file = open(self.path, 'a')
        input_file.write("\n")
        input_file.write("\n #---------- Build the mesh ----------")
        input_file.write("\n")
        input_file.write(f"\n&MESH_DEF method='{self.mesh.method}' /")
        if self.mesh.method == 'LAYERED':
            input_file.write("\n&MESH_LAYERED")
        elif self.mesh.method == 'MESH2D':
            input_file.write("\n&MESH_MESH2D")
        input_file.close()
        self.write_from_dictionnary(self.mesh.mesh_dic)

    def write_BC(self):
        input_file = open(self.path, 'a')
        input_file.write("\n")
        input_file.write("\n #---------- Boundary conditions ----------")
        input_file.close()
        for bc in self.BC_list:
            input_file = open(self.path, 'a')
            input_file.write("\n")
            if isinstance(bc.tags, Iterable):
                input_file.write(f"\n&BC_DEF tags=")
                for t in bc.tags:
                    input_file.write(f"{t},")
                input_file.write(f" kind='{bc.kind}' /")
            else :
                input_file.write(f"\n&BC_DEF tag={bc.tags}, kind='{bc.kind}' /")
            if bc.kind == 'DIRNEU':
                input_file.write("\n&BC_DIRNEU")
            input_file.close()
            self.write_from_dictionnary(bc.BC_dic)
            for param in bc.BC_dic.keys():
                if isinstance(bc.BC_dic[param],STF):
                    if bc.BC_dic[param].kind=='TAB':
                        input_file = open(self.path, 'a')
                        input_file.write(f"\n&STF_TAB")
                        input_file.close()
                        self.write_from_dictionnary(bc.BC_dic[param].stf_dic)

    def write_materials(self):
        input_file = open(self.path, 'a')
        input_file.write("\n")
        input_file.write("\n #---------- Material parameters ----------")
        input_file.close()
        for m in self.mat_list:
            input_file = open(self.path, 'a')
            input_file.write("\n")
            input_file.write(f"\n&MATERIAL tag={m.tag}, kind='{m.kind}' /")
            if m.kind == 'ELAST':
                input_file.write("\n&MAT_ELASTIC")
            elif m.kind == 'IWAN':
                input_file.write("\n&MAT_IWAN")
            elif m.kind == 'VISLA':
                input_file.write("\n&MAT_VISLA")
            input_file.close()
            self.write_from_dictionnary(m.mat_dic)

    def write_time_scheme(self):
        input_file = open(self.path, 'a')
        input_file.write("\n")
        input_file.write("\n #---------- Time scheme settings ----------")
        input_file.write("\n")
        input_file.write("\n&TIME")
        input_file.close()
        self.write_from_dictionnary(self.time_scheme_dic)

    def write_receivers(self):
        input_file = open(self.path, 'a')
        input_file.write("\n")
        input_file.write("\n #---------- Receivers ----------")
        input_file.write("\n")
        input_file.write("\n&REC_LINE")
        input_file.close()
        self.write_from_dictionnary(self.rec_dic)

    def write_snapshot(self):
        input_file = open(self.path, 'a')
        input_file.write("\n")
        input_file.write("\n #---------- Snapshot output settings ----------")
        input_file.write("\n")
        input_file.write("\n&SNAP_DEF")
        input_file.close()
        self.write_from_dictionnary(self.snap_dic)
            


class Material():
    def __init__(self, tag, kind, **kwargs):
        """
        | Available materials | Parameters |
        |------------------|------------|
        |       ELAST     | rho, cp, cs        |
        |       IWAN      | rho, cp, cs, Nspr, gref        |
        |       VISLA     | rho, cp, cs, Qp, Qs, fr        |
        """
        self.tag = tag
        self.kind = kind
        self.mat_dic = {}
        for key, val in kwargs.items():
            self.mat_dic[key] = val
       
       
class Mesh():
    def __init__(self, method, *kwargs):
        """
        | Available Meshing | Parameters |
        |------------------|------------|
        |       LAYERED     | xlim, zmin, nx, file        |
        |       MESH2D     | file    |
        """
        self.method = method
        self.mesh_dic = {}
        for key, val in kwargs.items():
            self.mesh_dic[key] = val


class BC():
    def __init__(self, tags, kind, **kwargs):
        """
        | Available BC | Parameters |
        |------------------|------------|
        |       PERIOD     | None        |
        |       DIRNEU     | h, v, hstf, vstf, borehole     |
        """
        self.tags = tags
        self.kind = kind
        self.BC_dic = {}
        for key, val in kwargs.items():
            self.BC_dic[key] = val


class SRC():
    def __init__(self, stf, mechanism, coord, file=None):
        """
        | Parameters | Options |
        |------------------|------------|
        | Signal types | TAB, GAUSSIAN |
        | Mechanism    | WAVE         |
        """
        self.stf = stf
        self.mechanism = mechanism
        self.coord = coord
        self.file = file
        self.src_dic = {}


class STF():
    def __init__(self, kind, **kwargs):
        """
        | Available sources | Parameters |
        |------------------|------------|
        |       TAB     | file        |
        |       GAUSSIAN     | ampli, f0, onset      |
        """
        self.kind = kind
        self.stf_dic = {}
        for key, val in kwargs.items():
            self.stf_dic[key] = val


    

        