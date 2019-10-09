from gurobipy import GRB, Model, quicksum
from random import choice, randint
import parametros as PARA

#-----------------------------------------------------------------------------
# CONJUNTOS

productores, centros, medicamentos, cam_por_prod, cam_CENABAST,\
dias = PARA.Conjuntos()

#-----------------------------------------------------------------------------
# PARAMETROS

params, med_prod = PARA.Parametros(productores= productores, centros= centros,
medicamentos= medicamentos, dias= dias)

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
                trans_entre_centro[m][c][a][b] = {}
                for d in dias:
                    trans_entre_centro[m][c][a][b][d] = model.addVar(vtype= GRB.CONTINUOUS, name=f'trans_centro_{m}_{c}_{a}_{b}_{d}')
# u: camion va desde bodega al centro b el dia d
bodega_a_centro = {}
for c in cam_CENABAST:
    bodega_a_centro[c] = {}
    for b in centros:
        bodega_a_centro[c][b] = {}
        for d in dias:
            bodega_a_centro[c][b][d] = model.addVar(vtype= GRB.BINARY, name=f'bodega_a_{b}_{c}_{d}')
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

obj1 = quicksum(quicksum(quicksum((cam_a_bodega[p][c][d] * params['costo fijo camion'][p]) +\
    quicksum(med_trans_prod[m][p][c][d] * params['costo tran medic bodega'][p][m] for m in med_prod[p]) \
    for c in cam_por_prod[p]) for p in productores) for d in dias)

obj2 = arrienda

obj3 = quicksum(quicksum(quicksum( (centro_a_bodegas[c][b][d] + bodega_a_centro[c][b][d])\
* params['costo tran bod centro'][b] + quicksum(entre_centro[c][b][a][d] * params['costo entre centros'][b][a]\
 for a in centros)  for b in centros) for c in cam_CENABAST) for d in dias)

model.setObjective(obj1 + obj2 + obj3, GRB.MINIMIZE)

#-----------------------------------------------------------------------------
# Restricciones

# Restr 1 y 2
for d in dias:
    for p in productores:
        for c in cam_por_prod[p]:
            # restr 1
            model.addConstr(
                quicksum(med_trans_prod[m][p][c][d] for m in med_prod[p])
                <= cam_a_bodega[p][c][d], f'restr01_{c}_{p}_{d}'
                )
            # restr 2
            model.addConstr(
                quicksum(med_trans_prod[m][p][c][d] for m in med_prod[p])
                * params['vol med'][m] <= params['vol camion'][p], f'restr02_{c}_{p}_{d}'
            )

# restr 3
for indice, d in enumerate(dias):
    for m in medicamentos:
        if indice == 0:
            model.addConstr(
                almacen_bodega[m][d] == params['inicial bodega'][m] + 
                quicksum(quicksum(med_trans_prod[m][p][c][d] for c in cam_por_prod[p]) for p in productores) +
                quicksum(quicksum(trans_centro_bodega[m][c][b][d] - med_bodega_centro[m][c][b][d] for c in cam_CENABAST) for b in centros),
                f'restr03_{m}_{d}'
            )
        elif indice == len(medicamentos) - 1:
            model.addConstr(
                almacen_bodega[m][d] == 0,
                f'restr03_{m}_{d}'
            )
        else:
            anterior = dias[indice-1]
            model.addConstr(
                almacen_bodega[m][d] == almacen_bodega[m][anterior] + 
                quicksum(quicksum(med_trans_prod[m][p][c][d] for c in cam_por_prod[p]) for p in productores) +
                quicksum(quicksum(trans_centro_bodega[m][c][b][d] - med_bodega_centro[m][c][b][d] for c in cam_CENABAST) for b in centros),
                f'restr03_{m}_{d}'
            )

# restr 4
for d in dias:
    for c in cam_CENABAST:
        for b in centros:
            model.addConstr(
                quicksum(med_bodega_centro[m][c][b][d] for m in medicamentos) 
                <= bodega_a_centro[c][b][d] * params['M GRANDE'], f'restr04_{b}_{c}_{d}'
            )

# restr 5
for d in dias:
    for c in cam_CENABAST:
        model.addConstr(quicksum(bodega_a_centro[c][b][d] for b in centros) == 1,
        f'restr05_{c}_{d}')

# restr 6
for d in dias:
    for c in cam_CENABAST:
        for b in centros:
            model.addConstr(
                quicksum(med_bodega_centro[m][c][b][d] * params['vol med'][m] for m in medicamentos)
                <= params['vol camion CENABAST'], f'restr06_{b}_{c}_{d}'
            )

# restr 7 y 8
for d in dias:
    for c in cam_CENABAST:
        for b in centros:
            for a in centros:
                if a == b:
                    continue
                # restr 7
                model.addConstr(
                    quicksum(trans_entre_centro[m][c][b][a][d] for m in medicamentos)
                    <= entre_centro[c][b][a][d] * params['M GRANDE'], f'restr07_{b}_{a}_{c}_{d}'
                )
                # restr 8
                model.addConstr(
                    quicksum(trans_entre_centro[m][c][b][a][d] * params['vol med'][m] for m in medicamentos)
                    <= params['vol camion CENABAST'], f'restr08_{b}_{a}_{c}_{d}'
                )

# restr 9
for indice, d in enumerate(dias):
    for b in centros:
        for m in medicamentos:
            if indice == 0:
                model.addConstr(
                    almacen_centro[m][b][d] == params['inicial centro'][m][b] +
                    quicksum(med_bodega_centro[m][c][b][d] + 
                    quicksum(trans_entre_centro[m][c][b][a][d] - trans_entre_centro[m][c][a][b][d] for a in centros) -
                    trans_centro_bodega[m][c][b][d] for c in cam_CENABAST) - 
                    params['demandas'][b][m][d], f'restr09_{m}_{b}_{d}'
                )
            elif indice == len(dias) - 1:
                model.addConstr(
                    almacen_centro[m][b][d] == 0, f'restr09_{m}_{b}_{d}'
                )
            else:
                anterior = dias[indice - 1]
                model.addConstr(
                    almacen_centro[m][b][d] == almacen_centro[m][b][anterior] +
                    quicksum(med_bodega_centro[m][c][b][d] + 
                    quicksum(trans_entre_centro[m][c][b][a][d] - trans_entre_centro[m][c][a][b][d] for a in centros) -
                    trans_centro_bodega[m][c][b][d] for c in cam_CENABAST) - 
                    params['demandas'][b][m][d], f'restr09_{m}_{b}_{d}'
                )

# restr 10
for b in centros:
    for d in dias:
        model.addConstr(
            quicksum(almacen_centro[m][b][d] * params['vol med'][m] for m in medicamentos)
            <= params['vol almacen centro'][b], f'restr10_{b}_{d}'
        )

# restr 11
for b in centros:
    for d in dias:
        for c in cam_CENABAST:
            model.addConstr(
                quicksum(trans_centro_bodega[m][c][b][d] for m in medicamentos)
                <= centro_a_bodegas[c][b][d] * params['M GRANDE'],
                f'restr11_{b}_{d}'
            )

# restr 12
for d in dias:
    for c in cam_CENABAST:
        model.addConstr(
            quicksum(centro_a_bodegas[c][b][d] for b in centros) == 1,
            f'restr12_{c}_{d}'
        )

# restr 13
for b in centros:
    for d in dias:
        for c in cam_CENABAST:
            model.addConstr(
                quicksum(trans_centro_bodega[m][c][b][d] * params['vol med'][m] for m in medicamentos)
                <= params['vol camion CENABAST'], f'restr13_{c}_{b}_{d}'
            )

# restr 14 , 15 y 16
for d in dias:
    for c in cam_CENABAST:
        for b in centros:
            # restr 14
            model.addConstr(
                bodega_a_centro[c][b][d] + quicksum(entre_centro[c][b][a][d] for a in centros)
                <= 1, f'restr14_{b}_{c}_{d}'
            )
            # restr 15
            model.addConstr(
                centro_a_bodegas[c][b][d] + quicksum(entre_centro[c][a][b][d] for a in centros)
                <= 1, f'restr15_{b}_{c}_{d}'
            )
            # restr 16
            model.addConstr(
                bodega_a_centro[c][b][d] + quicksum(entre_centro[c][b][a][d] for a in centros)
                == centro_a_bodegas[c][b][d] + quicksum(entre_centro[c][a][b][d] for a in centros),
                f'restr16_{b}_{c}_{d}'
            )

# restr 17
for d in dias:
    for c in cam_CENABAST:
        model.addConstr(
            quicksum(bodega_a_centro[c][b][d] * params['tiempo tran bod centro'][b] +
            quicksum(entre_centro[c][b][a][d] * params['tiempo entre centros'][b][a] for a in centros) +
            centro_a_bodegas[c][b][d] * params['tiempo tran bod centro'][b] for b in centros)
            <= params['horario camion'],
            f'restr17_{c}_{d}'
        )

# restr 18
for d in dias:
    model.addConstr(
        quicksum(almacen_bodega[m][d] * params['vol med'][m] for m in medicamentos)
        <= params['vol bodega'] * arrienda, f'restr18_{d}'
    )

# restr 19
for indice, d in enumerate(dias):
    for b in centros:
        for m in medicamentos:
            if indice == 0:
                model.addConstr(
                    params['inicial centro'][m][b] >= params['demandas'][b][m][d],
                    f'restr19_{m}_{b}_{d}'
                )
            else:
                anterior = dias[indice - 1]
                model.addConstr(
                    almacen_centro[m][b][anterior] >= params['demandas'][b][m][d],
                    f'restr19_{m}_{b}_{d}'
                )

# restr 20
for m in medicamentos:
    for indice, d in enumerate(dias[:len(dias) - params['dur med'][m]]):
        model.addConstr(
            almacen_bodega[m][d] + quicksum(almacen_centro[m][b][d] for b in centros)
            <= quicksum(quicksum(params['demandas'][b][m][i] for b in centros) \
                for i in dias[indice: indice + params['dur med'][m]]),
                f'restr20_{m}_{d}'
        )

# restr 21
for m in medicamentos:
    for indice, d in enumerate(dias[:len(dias) - params['dur med'][m]]):
        for b in centros:
            model.addConstr(
                almacen_centro[m][b][d] <= quicksum(params['demandas'][b][m][i] \
                    for i in dias[indice+1: indice + params['dur med'][m]]),
                    f'restr21_{b}_{m}_{d}'
            )

# restr 22
for p in productores:
    for indice, d in enumerate(dias[:len(dias) - params['prod cd'][p]]):
        model.addConstr(
            quicksum(quicksum(cam_a_bodega[p][c][i] for c in cam_por_prod[p]) \
                for i in dias[indice : indice + params['prod cd'][p]])
            == 1, f'restr22_{p}_{d}'
        )

# restr extra para evitar transportes de un centro al mismo
for d in dias:
    for c in cam_CENABAST:
        for b in centros:
            for a in centros:
                if b == a:
                    model.addConstr(entre_centro[c][b][a][d] == 0,
                    f'rest_extra_{b}_{a}_{c}_{d}')

#-----------------------------------------------------------------------------
model.update()
print('Modelo version 1.0')
model.optimize()

model.printAttr("X")

print('\n------------------------------------------------------------\n')
#for constr in model.getConstrs():
#    print(cosntr, constr.getAttr("slack"))


#-----------------------------------------------------------------------------

print('GG')