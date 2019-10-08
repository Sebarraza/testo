from gurobipy import GRB, Model, quicksum
from random import choice, randint
import parametros as PARA

#-----------------------------------------------------------------------------
# CONJUNTOS

productores, centros, medicamentos, med_por_prod, cam_por_prod,\
cam_CENABAST, dias = PARA.Conjuntos()

#-----------------------------------------------------------------------------
# PARAMETROS


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
vencidos = {} # DELETE
almacen_bodega = {}
for m in medicamentos:
    vencidos[m] = {} # DELETE
    almacen_bodega[m] = {}
    for d in dias:
        vencidos[m][d] = model.addVar(vtype= GRB.CONTINUOUS, name=f'vencidos_{m}_{d}') # DELETE
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