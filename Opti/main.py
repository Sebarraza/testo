from gurobipy import GRB, Model, quicksum
from random import choice, randint
import parametros as PARA

#-----------------------------------------------------------------------------
# CONJUNTOS

# Productores, cantidad dada por parametros.py
# LISTA DE STRINGS
productores = []
for x in range(1, PARA.CONJ['n prod']+1):
    productores.append(f'productor{x}')
# Centros, cantidad dada por parametros.py
# LISTA DE STRINGS
centros = []
for x in range(1, PARA.CONJ['n centros']+1):
    centros.append(f'centro{x}')
# Medicamentos, cantidad dada por parametros.py
# LISTA DE STRINGS
medicamentos = []
for x in range(1, PARA.CONJ['n medicamentos']+1):
    medicamentos.append(f'medicamento{x}')
# Medicamentos por productor, queda a mi criterio
# Con repeticion y cada productor una cantidad aleatoria dada por parametros.py
# DICCIONARIO -> PRODUCTOR(str) : MEDICAMENTOS(set)
med_por_prod = {}
for prod in productores:
    n = randint(*PARA.CONJ['rango medic prod'])
    temp = set()
    while len(temp) <= n:
        temp.add(choice(medicamentos))
    med_por_prod[prod] = temp
# Camiones disponibles por productor p
# Tiene una cantidad aleatoria de camiones dada por parametros.py
# DICCIONARIO -> PRODUCTOR(str) : CAMION(str)
cam_por_prod = {}
for prod in productores:
    n = randint(*PARA.CONJ['rango cam prod'])
    temp = []
    for x in range(1,n+1):
        temp.append(f'camion_{x}_{prod}')
    cam_por_prod[prod] = temp
# Camiones disponibles para CENABAST
# Tiene una cantidad aleatoria dada por parametros.py
cam_CENABAST = []
n = randint(*PARA.CONJ['rango cam CENABAST'])
for x in range(1, n+1):
    cam_CENABAST.append(f'camion_{x}_CENABAST')
# Dias a planificar
dias = []
for x in range(1, PARA.CONJ['n dias']+1):
    dias.append(f'dia{x}')
#-----------------------------------------------------------------------------
# PARAMETROS

# Volumen y duracion del medicamento
vol_med = {}
dur_med = {}
for med in medicamentos:
    n = randint(*PARA.PARAS['rango vol med'])
    vol_med[med] = n
    m = randint(*PARA.PARAS['rango dur med'])
    dur_med[med] = m
# costo fijo y capacidad de camion del productor
# mas costo variable por transporte del medicamento
costo_trans_medic_bodega = {}
costo_fijo_camion = {}
vol_camion = PARA.PARAS['capacidad camion']
vol_camion_CENABAST = PARA.PARAS['capacidad camion CENABAST']
horario_camion = PARA.PARAS['tiempo de trabajo del camion']
for prod in productores:
    c_fijo = randint(*PARA.PARAS['rango costo fijo camion'])
    costo_trans_medic_bodega[prod] = {}
    for med in medicamentos:
        c_trans = randint(*PARA.PARAS['rango costo var medic a bodega'])
        costo_trans_medic_bodega[prod][med] = c_trans
    costo_fijo_camion[prod] = c_fijo
costo_bodega = PARA.PARAS['costo arriendo bodega']
vol_bodega = PARA.PARAS['vol por bodega']
costo_tran_bod_centro = {}
tiempo_tran_bod_centro = {}
vol_almacen_centro = {}
for centro in centros:
    n = randint(*PARA.PARAS['rango costo bodega a centro'])
    costo_tran_bod_centro[centro] = n
    t = randint(*PARA.PARAS['rango tiempo bodega a centro'])
    tiempo_tran_bod_centro[centro] = t
    v = randint(*PARA.PARAS['rango vol almacenamiento centro'])
    vol_almacen_centro[centro] = v
# Inter centros
tiempo_entre_centros = {}
costo_entre_centros = {}
for a in centros:
    tiempo_entre_centros[a] = {}
    costo_entre_centros[a] = {}
    for b in centros:
        if a == b:
            continue
        else:
            t = randint(*PARA.PARAS['rango tiempo entre centros'])
            c = randint(*PARA.PARAS['rango costo entre centros'])
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
            temp = randint(*PARA.DEMANDAS['rango temporal'])
            demanda[c][m][d] = temp

#-----------------------------------------------------------------------------
# VARIABLES

print('GG')