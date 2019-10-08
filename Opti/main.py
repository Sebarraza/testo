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

model = Model('Plan Entregas CENABAST')

# X: unidades transportadas de medicamento desde el productor
med_trans_prod = {}
for m in medicamentos:
    med_trans_prod[m] = {}
    for p in productores:
        med_trans_prod[m][p] = {}
        for c in cam_por_prod[p]:
            med_trans_prod[m][p][c] = {}
            for d in dias:
                med_trans_prod[m][p][c][d] = model.addVar(vtype= GRB.CONTINUOUS, name=f'trans_{m}_{p}_{c}_{d}')
# Y: camion prod p va a bodega dia d
cam_a_bodega = {}
for p in productores:
    cam_a_bodega[p] = {}
    for c in cam_por_prod[p]:
        cam_a_bodega[p][c] = {}
        for d in dias:
            cam_a_bodega[p][c][d] = model.addVar(vtype= GRB.BINARY, name=f'a_bodega_{p}_{c}_{d}')
# Z: Unidades vencidas del medicamento m el dia d
# W: Unidades almacenadas de med m en bodega el dia d
vencidos = {}
almacen_bodega = {}
for m in medicamentos:
    vencidos[m] = {}
    almacen_bodega[m] = {}
    for d in dias:
        vencidos[m][d] = model.addVar(vtype= GRB.CONTINUOUS, name=f'vencidos_{m}_{d}')
        almacen_bodega[m][d] = model.addVar(vtype= GRB.CONTINUOUS, name=f'almacen_bodega_{m}_{d}')
# Beta: N Bodegas a arrendar
arrienda = model.addVar(vtype= GRB.CONTINUOUS, name='bodegas a arrendar')
# u: camion va desde bodega al centro b el dia d
bodega_a_centro = {}
for c in cam_CENABAST:
    bodega_a_centro[c] = {}
    for b in centros:
        bodega_a_centro[c][b] = {}
        for d in dias:
            bodega_a_centro[c][b][d] = model.addVar(vtype= GRB.BINARY, name=f'bodega_a_{b}_{c}_{d}')
# r: med transportado de bodega al centro b el dia d
med_bodega_centro = {}
for m in medicamentos:
    med_bodega_centro[m] = {}
    for c in cam_CENABAST:
        med_bodega_centro[m][c] = {}
        for b in centros:
            med_bodega_centro[m][c][b] = {}
            for d in dias:
                med_bodega_centro[m][c][b][d] = model.addVar(vtype= GRB.CONTINUOUS, name=f'med_{m}_{c}_{b}_{d}')
# q: unidades de med almacenadas en centro b el dia d
almacen_centro = {}
for m in medicamentos:
    almacen_centro[m] = {}
    for b in centros:
        almacen_centro[m][b] = {}
        for d in dias:
            almacen_centro[m][b][d] = model.addVar(vtype= GRB.CONTINUOUS, name=f'almacen_centro_{b}_{m}_{d}')
# p: camion c va del centro a al b el dia d
entre_centro = {}
for c in cam_CENABAST:
    entre_centro[c] = {}
    for a in centros:
        entre_centro[c][a] = {}
        for b in centros:
            if a == b:
                continue
            entre_centro[c][a][b] = {}
            for d in dias:
                entre_centro[c][a][b][d] = model.addVar(vtype= GRB.BINARY, name=f'cam_{c}_{a}_{b}_{d}')
# o: unidades de med transportadas por el camion del centro a al centro b el dia d
trans_entre_centro = {}
for m in medicamentos:
    trans_entre_centro[m] = {}
    for c in cam_CENABAST:
        trans_entre_centro[m][c] = {}
        for a in centros:
            trans_entre_centro[m][c][a] = {}
            for b in centros:
                if a == b:
                    continue
                trans_entre_centro[m][c][a][b] = {}
                for d in dias:
                    trans_entre_centro[m][c][a][b][d] = model.addVar(vtype= GRB.CONTINUOUS, name=f'trans_centro_{m}_{c}_{a}_{b}_{d}')
# f: camion va desde centro b a bodegas el dia d
centro_a_bodegas = {}
for c in cam_CENABAST:
    centro_a_bodegas[c] = {}
    for b in centros:
        centro_a_bodegas[c][b] = {}
        for d in dias:
            centro_a_bodegas[c][b][d] = model.addVar(vtype= GRB.BINARY, name=f'cen_a_bodega_{c}_{b}_{d}')
# h: Unidad trans de med m por el camion c desde centro b a bodegas el dia d
trans_centro_bodega = {}
for m in medicamentos:
    trans_centro_bodega[m] = {}
    for c in cam_CENABAST:
        trans_centro_bodega[m][c] = {}
        for b in centros:
            trans_centro_bodega[m][c][b] = {}
            for d in dias:
                trans_centro_bodega[m][c][b][d] = model.addVar(vtype= GRB.CONTINUOUS, name=f'tran_cen_bodega_{m}_{c}_{b}_{d}')

#-----------------------------------------------------------------------------
# Funcion Objetivo
model.update()

print('GG')