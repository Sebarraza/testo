'''
Parametros para el modelo
'''
# Parametros para la construccion de conjuntos
CONJ = {
    'n prod': 5,
    'n centros': 10,
    'n medicamentos': 30,
    'n dias': 60,
    'rango medic prod': (7, 11),
    'rango cam prod': (5, 15),
    'rango cam CENABAST': (20, 30)
}

PARAS = {
    'rango vol med': (2, 4),
    'rango dur med': (14, 21),
    'rango costo fijo camion': (5, 15),
    'rango costo var medic a bodega': (2, 6),
    'rango costo bodega a centro': (5, 15),
    'rango tiempo bodega a centro': (30, 60),
    'rango vol almacenamiento centro': (30, 45),
    'rango tiempo entre centros': (20, 80),
    'rango costo entre centros': (7, 11),
    'capacidad camion': 15,
    'capacidad camion CENABAST': 20,
    'tiempo de trabajo del camion': 300,
    'costo arriendo bodega': 20,
    'vol por bodega': 30,
    'M GRANDE': 100200300400
}

DEMANDAS = {
    'rango temporal': (0,20)
}

if __name__ == "__main__":
    print('se ejecuta el main')