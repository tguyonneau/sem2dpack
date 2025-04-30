import numpy as np
import matplotlib.pyplot as plt

def get_scientific_components(number):
    if number == 0.0:
        return 0,0
    else :
        exponent = np.floor(np.log10(abs(number)))
        mantissa = number / 10 ** exponent
        return mantissa, int(exponent)
    
def generate_stations_grid(xlim, zlim, dx, dz):
    X = np.arange(xlim[0],xlim[1]+dx,dx)
    Z = np.arange(zlim[0],zlim[1]+dz,dz)
    Z_grid, X_grid  = np.meshgrid(Z,X)
    X_grid = X_grid.flatten()
    Z_grid = Z_grid.flatten()
    return X_grid, Z_grid

def preview_stations(X,Z):
    plt.scatter(X,Z,marker='v')
    plt.show()

def write_stations_file(path, X, Z):
    file = open(path, 'w+')
    for i in range(X.size):
        x = X[i]
        m_x, e_x = get_scientific_components(x)
        z = Z[i]
        m_z, e_z = get_scientific_components(z)
        file.write(f"{m_x}d{e_x}\t{m_z}d{e_z}\n")
    file.close()

def write_layers_file(path, mat_list, layers, n_z):
    file = open(path, 'w+')
    level = [0]
    for i in range(1,len(layers)):
        level.append(level[-1]-layers[i-1])
    for i in range(len(layers)):
        l = level[i]
        m_l, e_l = get_scientific_components(l)
        file.write(f"{m_l}d{e_l}\t{n_z[i]}\t{mat_list[i].tag}\n")
    file.close()