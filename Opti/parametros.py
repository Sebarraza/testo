'''
Conjuntos y parametros para el modelo
'''

from random import choice, randint
from collections import defaultdict
from pandas import DataFrame, read_excel

def carga_datos(nombre = ''):
    temp = []
    with open(nombre, mode= 'r') as archivo:
        for line in archivo:
            l = line.strip('\n')
            if l == '':
                continue
            l = l.split(';')
            temp.append(l)
    return temp


def Conjuntos():
    # Tamanos primero
    CONJ = {}

    arreglo = carga_datos(nombre='csvs/size_conjuntos.csv')
    for fila in arreglo:
        if fila[0] == 'conjuntos':
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
        cam_por_prod,
        cam_CENABAST,
        dias
    )
#-----------------------------------------------------------------------------
# PARAMETROS

def Parametros(productores = [], medicamentos = [], centros = [], dias= []):
    arreglo = carga_datos('csvs/constantes.csv')
    for fila in arreglo:
        nombre, valor = (fila[0], fila[2])
        if nombre == 'Nombre':
            continue
        elif nombre == 'capacidad camion CENABAST':
            vol_camion_CENABAST = int(valor)
        elif nombre == 'costo arriendo bodega':
            costo_bodega = int(valor)
        elif nombre == 'vol por bodega':
            vol_bodega = int(valor)
        elif nombre == 'tiempo de trabajo del camion':
            horario_camion = int(valor)

    # Volumen y duracion del medicamento
    vol_med = {}
    dur_med = {}
    # Costo var del camion por productor
    costo_trans_medic_bodega = {}
    arreglo = carga_datos('csvs/medicamentos.csv')
    for fila in arreglo:
        nombre, valores = (fila[0], fila[1:])
        if nombre == 'Nombre':
            continue
        elif nombre == 'volumen':
            for med, vol in zip(medicamentos, valores):
                if ',' in vol:
                    u,d = vol.split(',')
                    vol = '.'.join((u,d))
                vol_med[med] = float(vol)
        elif nombre == 'duracion':
            for med, tiempo in zip(medicamentos, valores):
                dur_med[med] = int(tiempo)
        elif 'productor' in nombre:
            costo_trans_medic_bodega[nombre] = {}
            for med, costo in zip(medicamentos, valores):
                if costo == '':
                    costo_trans_medic_bodega[nombre][med] = None
                else:
                    costo_trans_medic_bodega[nombre][med] = int(costo)

    # Bodega a centro
    costo_tran_bod_centro = {}
    tiempo_tran_bod_centro = {}
    # Inter centros
    tiempo_entre_centros = {}
    costo_entre_centros = {}
    arreglo = carga_datos('csvs/tiempo y costo por centro.csv')
    for fila in arreglo:
        tipo, origen, valores = (fila[0], fila[1], tuple(fila[2:]))
        if tipo == 'tipo':
            continue
        elif tipo == 'tiempo':
            if origen == 'bodega':
                for centro, tiempo in zip(centros, valores):
                    if ',' in tiempo:
                        u,d = tiempo.split(',')
                        tiempo= '.'.join((u,d))
                    tiempo_tran_bod_centro[centro] = float(tiempo)
            elif 'centro' in origen:
                tiempo_entre_centros[origen] = {}
                for centro, tiempo in zip(centros, valores):
                    if ',' in tiempo:
                        u,d = tiempo.split(',')
                        tiempo= '.'.join((u,d))
                    if centro == origen:
                        tiempo = '0'
                    tiempo_entre_centros[origen][centro] = float(tiempo)
        elif tipo == 'costo':
            if origen == 'bodega':
                for centro, costo in zip(centros, valores):
                    if ',' in costo:
                        u,d = costo.split(',')
                        costo= '.'.join((u,d))
                    costo_tran_bod_centro[centro] = float(costo)
            elif 'centro' in origen:
                costo_entre_centros[origen] = {}
                for centro, costo in zip(centros, valores):
                    if ',' in costo:
                        u,d = costo.split(',')
                        costo= '.'.join((u,d))
                    if centro == origen:
                        costo = '0'
                    costo_entre_centros[origen][centro] = float(costo)

    # Demanda:
    # Este es muy denso como para hacerlo asi, probablemente va a tener que hacerse
    # un archivo a lo txt o csv con estos datos
    # SPOILER: el csv que me pasaron era exactamente esto, asique lo dejo asi
    demanda = {}
    temp = defaultdict(list)
    arreglo = carga_datos('csvs/demandas.csv')
    for fila in arreglo:
        med, dia, valores= (fila[0], fila[1], fila[2:])
        if med == 'med':
            continue
        s = med.strip('med')
        med = 'medicamento'+s
        t = []
        t.append(dia)
        t.extend(valores)
        temp[med].append(t)
        
    for key, value in temp.items():
        demanda[key] = {}
        for indice, d in enumerate(dias):
            demanda[key][d] = {}
            valores = value[indice][1:]
            for b, valor in zip(centros, valores):
                demanda[key][d][b] = int(valor)


    costo_fijo_cam = {}
    vol_cam = {}
    min_prod = {}
    cd_prod = {}
    arreglo = carga_datos('csvs/vol y costo fijo por prod.csv')
    for fila in arreglo:
        nombre, valores = (fila[0], fila[2:])
        if nombre == 'nombres':
            continue
        elif nombre == 'vol camion':
            for p, vol in zip(productores, valores):
                vol_cam[p] = int(vol)
        elif nombre == 'costo fijo':
            for p, costo in zip(productores, valores):
                costo_fijo_cam[p] = int(costo)
        elif nombre == 'vol min':
            for p, vol in zip(productores, valores):
                min_prod[p] = int(vol)
        elif nombre == 'cd prod':
            for p, cd in zip(productores, valores):
                cd_prod[p] = int(cd)

    # Conjunto de medicamentos por productor
    med_prod = {}
    for p in productores:
        medics = costo_trans_medic_bodega[p]
        med_prod[p] = []
        for m in medicamentos:
            if medics[m] == None:
                continue
            else:
                med_prod[p].append(m)

    inicial_bodega = {}
    inicial_centro = defaultdict(dict)
    arreglo = carga_datos('csvs/inv inicial.csv')
    for fila in arreglo:
        medi, lugar, valor = tuple(fila)
        if medi == 'med':
            continue
        if lugar == 'bodega':
            inicial_bodega[medi] = int(valor)
        elif 'centro' in lugar:
            inicial_centro[medi][lugar] = int(valor)

    vol_almacen_centro = {}
    arreglo = carga_datos('csvs/vol centros.csv')
    for fila in arreglo:
        centro, vol = tuple(fila)
        if centro == 'centro':
            continue
        vol_almacen_centro[centro] = int(vol)


    return {
        'demandas': demanda,
        'costo tran bod centro': costo_tran_bod_centro,
        'tiempo tran bod centro': tiempo_tran_bod_centro,
        'vol almacen centro': vol_almacen_centro,
        'tiempo entre centros': tiempo_entre_centros,
        'costo entre centros': costo_entre_centros,
        'vol camion': vol_cam,
        'vol camion CENABAST': vol_camion_CENABAST,
        'horario camion': horario_camion,
        'costo bodega': costo_bodega,
        'vol bodega': vol_bodega,
        'vol med': vol_med,
        'dur med': dur_med,
        'costo tran medic bodega': costo_trans_medic_bodega,
        'costo fijo camion': costo_fijo_cam,
        'M GRANDE': 100200300400,
        'inicial centro': inicial_centro,
        'inicial bodega': inicial_bodega,
        'prod cd': cd_prod,
        'min prod': min_prod
    }, med_prod

if __name__ == "__main__":
    print('se ejecuta el main')