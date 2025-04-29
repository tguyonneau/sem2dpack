from Class import *
from Functions import *

def Volvi_Elast():
    layers = [7, 13, 34, 23.5, 50, 59, 10, 103.5]
    m1 = Material(1,'ELAST')
    m1.set_properties(rho=2050., cp=1500., cs=130.)
    m2 = Material(2,'ELAST')
    m2.set_properties(rho=2150., cp=1500., cs=200.)
    m3 = Material(3,'ELAST')
    m3.set_properties(rho=2075., cp=1650., cs=300.)
    m4 = Material(4,'ELAST')
    m4.set_properties(rho=2100., cp=2050., cs=450.)
    m5 = Material(5,'ELAST')
    m5.set_properties(rho=2155., cp=2450., cs=600.)
    m6 = Material(6,'ELAST')
    m6.set_properties(rho=2200., cp=2550., cs=700.)
    m7 = Material(7,'ELAST')
    m7.set_properties(rho=2500., cp=3500., cs=1250.)
    bed = Material(8,'ELAST')
    bed.set_properties(rho=2600., cp=4500., cs=2600.)
    mat_list = [m1, m2, m3, m4, m5, m6, m7, bed]
    return np.array(mat_list), np.array(layers)

def Volvi():
    layers = [7, 13, 34, 23.5, 50, 59, 10, 103.5]
    m1 = Material(1,'VISLA')
    m1.set_properties(rho=2050., cp=1500., cs=130., Qs=15., Qp=75., fr=1)
    m2 = Material(2,'VISLA')
    m2.set_properties(rho=2150., cp=1500., cs=200., Qs=20., Qp=75., fr=1)
    m3 = Material(3,'VISLA')
    m3.set_properties(rho=2075., cp=1650., cs=300., Qs=30., Qp=83., fr=1)
    m4 = Material(4,'VISLA')
    m4.set_properties(rho=2100., cp=2050., cs=450., Qs=40., Qp=103., fr=1)
    m5 = Material(5,'VISLA')
    m5.set_properties(rho=2155., cp=2450., cs=600., Qs=60., Qp=123., fr=1)
    m6 = Material(6,'VISLA')
    m6.set_properties(rho=2200., cp=2550., cs=700., Qs=70., Qp=140., fr=1)
    m7 = Material(7,'VISLA')
    m7.set_properties(rho=2500., cp=3500., cs=1250., Qs=100., Qp=200., fr=1)
    bed = Material(8,'VISLA')
    bed.set_properties(rho=2600., cp=4500., cs=2600., Qs=50000., Qp=50000., fr=1)
    mat_list = [m1, m2, m3, m4, m5, m6, m7, bed]
    return np.array(mat_list), np.array(layers)