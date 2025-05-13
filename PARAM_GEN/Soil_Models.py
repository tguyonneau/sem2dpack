from Class import *
from Functions import *

def Volvi_Elast():
    layers = [7, 13, 34, 23.5, 50, 59, 10, 103.5]
    m1 = Material(1,'ELAST', rho=2050., cp=1500., cs=130.)
    m2 = Material(2,'ELAST', rho=2150., cp=1500., cs=200.)
    m3 = Material(3,'ELAST', rho=2075., cp=1650., cs=300.)
    m4 = Material(4,'ELAST', rho=2100., cp=2050., cs=450.)
    m5 = Material(5,'ELAST', rho=2155., cp=2450., cs=600.)
    m6 = Material(6,'ELAST', rho=2200., cp=2550., cs=700.)
    m7 = Material(7,'ELAST', rho=2500., cp=3500., cs=1250.)
    bed = Material(8,'ELAST', rho=2600., cp=4500., cs=2600.)
    mat_list = [m1, m2, m3, m4, m5, m6, m7, bed]
    return np.array(mat_list), np.array(layers)

def Volvi():
    layers = [7, 13, 34, 23.5, 50, 59, 10, 103.5]
    m1 = Material(1,'VISLA', rho=2050., cp=1500., cs=130., Qs=15., Qp=75., fr=1)
    m2 = Material(2,'VISLA', rho=2150., cp=1500., cs=200., Qs=20., Qp=75., fr=1)
    m3 = Material(3,'VISLA', rho=2075., cp=1650., cs=300., Qs=30., Qp=83., fr=1)
    m4 = Material(4,'VISLA', rho=2100., cp=2050., cs=450., Qs=40., Qp=103., fr=1)
    m5 = Material(5,'VISLA', rho=2155., cp=2450., cs=600., Qs=60., Qp=123., fr=1)
    m6 = Material(6,'VISLA', rho=2200., cp=2550., cs=700., Qs=70., Qp=140., fr=1)
    m7 = Material(7,'VISLA', rho=2500., cp=3500., cs=1250., Qs=100., Qp=200., fr=1)
    bed = Material(8,'VISLA', rho=2600., cp=4500., cs=2600., Qs=50000., Qp=50000., fr=1)
    mat_list = [m1, m2, m3, m4, m5, m6, m7, bed]
    return np.array(mat_list), np.array(layers)

def Rome():
    layers = [10, 6, 16, 13.5, 10, 2.5, 7, 3, 2.5, 3, 2.5, 3, 2.5, 2.5, 16]
    m1 = Material(1,'VISLA', rho=1835., cp=490., cs=220., Qs=100., Qp=200., fr=1)
    m2 = Material(2,'VISLA', rho=1876., cp=523., cs=239., Qs=15., Qp=30., fr=1)
    m3 = Material(3,'VISLA', rho=1967., cp=1480., cs=260., Qs=100., Qp=200., fr=1)
    m4 = Material(4,'VISLA',rho=1957., cp=1760., cs=417., Qs=50., Qp=100., fr=1)
    m5 = Material(5,'VISLA', rho=1865., cp=1235., cs=212.5, Qs=35., Qp=70., fr=1)
    m6 = Material(6,'VISLA', rho=2141., cp=2560., cs=713., Qs=50., Qp=100., fr=1)
    m7 = Material(7,'VISLA', rho=2078., cp=2125., cs=545., Qs=35., Qp=70., fr=1)
    m8 = Material(8,'VISLA', rho=2078., cp=2379., cs=610., Qs=35., Qp=70., fr=1)
    m9 = Material(9,'VISLA', rho=2078., cp=2632.5, cs=675., Qs=35., Qp=70., fr=1)
    m10 = Material(10,'VISLA', rho=2078., cp=2886., cs=740., Qs=35., Qp=70., fr=1)
    m11 = Material(11,'VISLA', rho=2078., cp=3139.5, cs=805., Qs=5000., Qp=10000., fr=1)
    m12 = Material(12,'VISLA', rho=2078., cp=3393., cs=870., Qs=5000., Qp=10000., fr=1)
    m13 = Material(13,'VISLA', rho=2078., cp=3646.5, cs=935., Qs=5000., Qp=10000., fr=1)
    m14 = Material(14,'VISLA', rho=2078., cp=3900., cs=1000., Qs=5000., Qp=10000., fr=1)
    mat_list = [m1, m2, m3, m4, m5, m4, m6, m7, m8, m9, m10, m11, m12, m13, m14]
    return np.array(mat_list), np.array(layers)