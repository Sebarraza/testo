'''
Parametros para el modelo
'''

from random import choice, randint

def carga_datos(nombre = ''):
    temp = []
    with open(nombre) as archivo:
        for line in archivo:
            l = line.strip('\n')
            if l == '':
                continue
            l = l.split(';')
            temp.append(l)
    return temp


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

def Conjuntos():
    # Tamanos primero
    CONJ = {
        'rango medic prod': (7, 11),
    }

    arreglo = carga_datos(nombre='size_conjuntos.csv')
    for fila in arreglo:
        if fila[0] == 'Conjuntos':
            continue
        else:
            CONJ[fila[0]] = int(fila[2])

    # Productores, cantidad dada por parametros.py
    # LISTA DE STRINGS
    productores = []
    for x in range(1, CONJ['n prod']+1):
        productores.append(f'productor{x}')
    # Centros, cantidad dada por parametros.py
    # LISTA DE STRINGS
    centros = []
    for x in range(1, CONJ['n centros']+1):
        centros.append(f'centro{x}')
    # Medicamentos, cantidad dada por parametros.py
    # LISTA DE STRINGS
    medicamentos = []
    for x in range(1, CONJ['n medicamentos']+1):
        medicamentos.append(f'medicamento{x}')
    # Medicamentos por productor, queda a mi criterio
    # Con repeticion y cada productor una cantidad aleatoria dada por parametros.py
    # DICCIONARIO -> PRODUCTOR(str) : MEDICAMENTOS(set)
    med_por_prod = {}
    for prod in productores:
        n = randint(*CONJ['rango medic prod'])
        temp = set()
        while len(temp) <= n:
            temp.add(choice(medicamentos))
        med_por_prod[prod] = temp
    # Camiones disponibles por productor p
    # Tiene una cantidad aleatoria de camiones dada por parametros.py
    # DICCIONARIO -> PRODUCTOR(str) : CAMION(str)
    cam_por_prod = {}
    for prod in productores:
        n = CONJ['cam prod']
        temp = []
        for x in range(1,n+1):
            temp.append(f'camion_{x}_{prod}')
        cam_por_prod[prod] = temp
    # Camiones disponibles para CENABAST
    # Tiene una cantidad aleatoria dada por parametros.py
    cam_CENABAST = []
    n = CONJ['cam CENABAST']
    for x in range(1, n+1):
        cam_CENABAST.append(f'camion_{x}_CENABAST')
    # Dias a planificar
    dias = []
    for x in range(1, CONJ['n dias']+1):
        dias.append(f'dia{x}')
    return (
        productores,
        centros,
        medicamentos,
        med_por_prod,
        cam_por_prod,
        cam_CENABAST,
        dias
    )
#-----------------------------------------------------------------------------
# PARAMETROS

def Parametros(productores = [], medicamentos = [], centros = [], dias= []):
    # Directos desde paramteros.py
    vol_camion = PARAS['capacidad camion']
    vol_camion_CENABAST = PARAS['capacidad camion CENABAST']
    horario_camion = PARAS['tiempo de trabajo del camion']
    costo_bodega = PARAS['costo arriendo bodega']
    vol_bodega = PARAS['vol por bodega']

    # Volumen y duracion del medicamento
    vol_med = {}
    dur_med = {}
    # Costo fijo y var del camion por productor
    costo_trans_medic_bodega = {}
    costo_fijo_camion = {}
    for m in medicamentos:
        # Volumen y duracion del medicamento
        vol = randint(*PARAS['rango vol med'])
        vol_med[m] = vol
        dur = randint(*PARAS['rango dur med'])
        dur_med[m] = dur
        # Costo fijo y variable de camiones del productor
        costo_trans_medic_bodega[m] = {}
        for p in productores:
            c_trans = randint(*PARAS['rango costo var medic a bodega'])
            costo_trans_medic_bodega[m][p] = c_trans
            if m == medicamentos[0]: # Costo fijo solo se define una vez
                c_fijo = randint(*PARAS['rango costo fijo camion'])
                costo_fijo_camion[p] = c_fijo

    # Bodega a centro
    costo_tran_bod_centro = {}
    tiempo_tran_bod_centro = {}
    vol_almacen_centro = {}
    # Inter centros
    tiempo_entre_centros = {}
    costo_entre_centros = {}
    for a in centros:
        # Bodega a centro
        n = randint(*PARAS['rango costo bodega a centro'])
        costo_tran_bod_centro[a] = n
        t = randint(*PARAS['rango tiempo bodega a centro'])
        tiempo_tran_bod_centro[a] = t
        v = randint(*PARAS['rango vol almacenamiento centro'])
        vol_almacen_centro[a] = v
        # Inter centros
        tiempo_entre_centros[a] = {}
        costo_entre_centros[a] = {}
        for b in centros:
            if a == b:
                continue
            else:
                t = randint(*PARAS['rango tiempo entre centros'])
                c = randint(*PARAS['rango costo entre centros'])
                tiempo_entre_centros[a][b] = t
                costo_entre_centros[a][b] = t
    # Demanda:
    # Este es muy denso como para hacerlo asi, probablemente va a tener que hacerse
    # un archivo a lo txt o csv con estos datos
    demanda = {}
    for c in centros:
        demanda[c] = {}
        for m in medicamentos:
            demanda[c][m] = {}
            for d in dias:
                temp = randint(*DEMANDAS['rango temporal'])
                demanda[c][m][d] = temp

    return (

    )

if __name__ == "__main__":
    print('se ejecuta el main')