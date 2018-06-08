# from gurobipy import *
from gurobipy import Model
from gurobipy import quicksum
from gurobipy import GRB
from gurobipy import GurobiError
# import random
# import sys

# Run on Mac OSX: time(gurobi.sh main.py) in the folder containing file

try:
    # Mencionar modelo (aqui va cualquier nombre
    m = Model('decision')

    # Definicion de parametros

    # Deportes
    D = {1: 'Futbol hombre',
         2: 'Futbol mujer',
         3: 'Futsal hombre',
         4: 'Futsal mujer',
         5: 'Handbol hombre',
         6: 'Handbol mujer',
         7: 'Voleibol hombre',
         8: 'Voleibol mujer',
         9: 'Basquetbol hombre',
         10: 'Basquetbol mujer'}

    # Canchas
    C = [1, 2, 3, 4, 5]
    # 1 -> Futbol
    # 2 -> Gimnasio: Futsal, Volley, Basquet
    # 3 -> Handbol
    # 4 -> Fuera1: Basquet,Volley
    # 5 -> Fuera2: Basquet,Volley

    # Bloques de Tiempo
    T = [i + 1 for i in range(4)]

    # Equipos
    # 10 colegios en total
    E = [i + 1 for i in range(10)]

    # Conjunto de dias en un mes en los que se puede jugar partidos(Sabado y Domingo intercalado).
    A = [i + 1 for i in range(8)]
    # A = [i + 1 for i in range(16)]

    # P_d: Cantidad de partidos de liga del deporte d, con l in L.
    # por ahora 3 a 5 partidos por deporte por liga
    P_d = [4, 4, 3, 3, 5, 5, 5, 5, 3, 3]

    # n_d: personas por equipo en el deporte d in D
    n_d = [22, 22, 13, 13, 13, 13, 15, 15, 16, 16]

    # duracion del partido del deporte d in D
    t_d = [120, 120, 90, 90, 70, 70, 90, 90, 80, 80]

    # cantidad de vehiculos por equipo e
    veh_e = [11, 11, 9, 9, 9, 9, 8, 8, 10, 10]

    # bonificacion para los deportes, 100 para todos
    b_d = [100 for i in range(len(D))]

    # minimo de partidos del deporte d in D
    minp_d = [1 for d in range(len(D))]

    # cantidad maxima de espectadores en la cancha c in C
    emax_c = [200, 200, 120, 80, 80]
    # emax_c = [200, 200, 200, 200, 200]

    # capacidad maxima del camarin
    # mc = 20
    mc = 40

    # capacidad maxima del estacionamiento
    mveh = 100
    # mveh = 300

    # cantidad de buses que caben en el estacionamiento
    mbus = 2
    # mbus = 100

    #Costo de contratar un bus
    cb_d = [10000, 10000, 6000, 6000, 6000, 6000, 7000, 7000, 8000, 8000]

    #Presupuesto disponible para cada liga para los buses
    pres_d = [100000, 90000, 70000, 60000, 70000, 60000, 80000, 70000, 90000, 80000]

    # si en la cancha c se puede jugar el deporte d = 1, 0 e.o.c.
    s_cd = [[1, 1, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 -> Futbol
            [0, 0, 1, 1, 0, 0, 1, 1, 1, 1],  # 2 -> Gimnasio: Futsal, Volley, Basquet
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # 3 -> Handbol
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1],  # 4 -> Fuera1: Basquet,Volley
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1]]  # 5 -> Fuera2: Basquet,Volley

    # Puros 1s para probar que las canchas no sean el problema
    # s_cd = [[1 for i in range(10)] for i in range(5)]

    # q_ed = [[0 for i in range(len(E))] for i in range(len(D))]  # original
    # q_ed = [[1 for i in range(len(E))] for i in range(len(D))]

    # i = 0
    # j = 5
    # for lista in q_ed:
    #     lista[i:j] = [1] * 5
    #     i += 5
    #     j += 5

    # for i in range(10):
    #     print(random.sample([0, 1, 0, 1, 0, 1, 0, 1, 0, 1], 10))

    # si el equipo e juega el deporte d = 1, 0 e.o.c.
    q_ed = [[1, 0, 1, 0, 1, 1, 0, 1, 0, 0],  # si usamos 10 equipos
            [1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
            [1, 1, 0, 0, 0, 1, 0, 1, 0, 1],
            [0, 1, 1, 0, 0, 1, 0, 0, 1, 1],
            [1, 0, 1, 0, 1, 1, 1, 0, 0, 0],
            [1, 0, 1, 0, 1, 1, 1, 0, 0, 0],
            [1, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 1, 0, 0, 1, 1, 0, 1, 0, 1],
            [0, 1, 1, 0, 0, 1, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 1, 0, 1, 0]]

    # Crear variables
    # u_eca = m.addVars(E, C, A, vtype=GRB.CONTINUOUS, lb=0.0, ub=GRB.INFINITY, name="u")

    print("parametros listos")

    # si el equipo e comienza a jugar contra el equipo o en la cancha c, el deporte d, en el minuto t del dia a
    X_coedta = m.addVars(C, E, E, D, T, A, vtype=GRB.BINARY, name="x")

    # Si el equipo e llega en bus en el tiempo t en el dia a
    B_eta = m.addVars(E, T, A, vtype=GRB.BINARY, name="b")

    # Si el equipo e llega en vehiculos en el tiempo t en el dia a
    V_eta = m.addVars(E, T, A, vtype=GRB.BINARY, name="v")

    print("variables listas")

    # FUNCION OBJETIVO
    m.setObjective(quicksum((quicksum(
        X_coedta[cancha, equipoo, equipoe, deporte, bloque, dia]/2
        for dia in A for bloque in T for cancha in C for equipoe in E
        for equipoo in E if equipoo != equipoe) - minp_d[deporte - 1]) * b_d[deporte - 1]
                            for deporte in D), GRB.MAXIMIZE)

    print("FO lista")

    # Restriccion 1: Solo se puede jugar un partido en un bloque de tiempo t en cada cancha.
    m.addConstrs(
        (quicksum(X_coedta[cancha, equipoo, equipoe, deporte, bloque, dia]/2 for equipoe in E for equipoo in E if equipoo != equipoe for deporte in D) <= 1 for cancha in C for bloque in T for dia in A ), 'C1')

    print("R1 lista")

    # Restriccion 2: Se puede jugar en una cancha si esta lo permite y los equipos juegan los respectivos deportes
    m.addConstrs(
        (X_coedta[cancha, equipoO, equipoE, deporte, bloque, dia]
         <= s_cd[cancha-1][deporte-1] * q_ed[deporte-1][equipoE-1] * q_ed[deporte-1][equipoO-1] for equipoE in E for equipoO in E if equipoE != equipoO for cancha in C for deporte in D
         for bloque in T for dia in A), "C2")

    print("R2 lista")

    # Restriccion 3: Cada equipo puede jugar como maximo una vez al dia
    m.addConstrs(
        (quicksum(X_coedta[cancha, equipoO, equipoE, deporte, bloque, dia] for cancha in C for deporte in D for bloque in T)
         <= 1 for equipoE in E for equipoO in E if equipoE != equipoO for dia in A), "C3")

    print("R3 lista")

    # Restriccion 4: Se debera jugar como minimo un partido por liga durante el mes
    m.addConstrs(
        (quicksum(X_coedta[cancha, equipoO, equipoE, deporte, bloque, dia] for cancha in C for equipoE in E for equipoO in E
        if equipoE != equipoO for bloque in T for dia in A) >= 1 for deporte in D), "C4")

    print("R4 lista")

    # Restriccion 5: Si un equipo juega, tiene parte de los estacionamientos ocupados (autos y buses), de lo contrario no llega
    m.addConstrs(
        (quicksum(X_coedta[cancha, equipo, equipoo, deporte, bloque, dia] for deporte in D for cancha in C for equipoo in E if equipo != equipoo) == B_eta[equipo, bloque, dia] + V_eta[equipo, bloque, dia]
         for bloque in T for dia in A for equipo in E), "C5")

    print("R5 lista")

    # Restriccion 6: No. de autos estacionados en un bloque t no puede superar capacidad max de estacionamientos
    m.addConstrs(
        (quicksum(V_eta[equipo, bloque, dia] * veh_e[equipo-1] * q_ed[deporte-1][equipo-1] for equipo in E) <= mveh
        for bloque in T for dia in A for deporte in D), "C6")
    print("R6 lista")

#    m.addConstrs(
#        (quicksum(V_eta[equipo, bloque, dia] * veh_e[equipo-1] * q_ed[deporte-1][equipo-1] for equipo in E) >= 10
#        for bloque in T for dia in A for deporte in D), "C66")
#    print("R66 lista")


    # Restriccion 7: No. de buses estacionados no puede superar capacidad max de buses
    m.addConstrs(
        (quicksum(B_eta[equipo, bloque, dia] * q_ed[deporte-1][equipo-1] for equipo in E) <= mbus
        for bloque in T for dia in A for deporte in D), "C7")

    print("R7 lista")

    # Restriccion 7-2 : Presupuesto que hay para contratar buses

    m.addConstrs(
        (quicksum(B_eta[equipo, bloque, dia] * q_ed[deporte-1][equipo-1] * cb_d [deporte-1] for equipo in E for dia in A for bloque in T) <= pres_d[deporte-1]
        for deporte in D), "C77")

    print("R77 lista")

    # Restriccion 8: Ctdad. de jugadores que usan los camarines tiene que ser menor a su capacidad maxima para H y M
    m.addConstrs(
        (quicksum(X_coedta[cancha, equipoO, equipoE, deporte, bloque, dia] * n_d[deporte-1] for cancha in C for equipoE in E for equipoO in E
        if equipoE != equipoO for bloque in T for dia in A) <= 2 * mc for deporte in D if deporte % 2 != 0), "C81")
    m.addConstrs(
        (quicksum(X_coedta[cancha, equipoO, equipoE, deporte, bloque, dia] * n_d[deporte-1] for cancha in C for equipoE in E for equipoO in E
        if equipoE != equipoO for bloque in T for dia in A) <= 2 * mc for deporte in D if deporte % 2 == 0), "C82")

    print("R8 lista")

    # Restriccion 9: Ctdad. de espectadores para c/partido no debe superar capacidad max de c/cancha
    m.addConstrs(
        (quicksum(V_eta[equipo, bloque, dia] * n_d[deporte-1] * q_ed[deporte-1][equipo-1] for equipo in E) * 2 <= emax_c[cancha-1]
        for cancha in C for bloque in T for dia in A for deporte in D), "C9")

    print("R9 lista")

    # Restriccion 10: Si equipo e juega con o, o juega con e.

    m.addConstrs(
            (X_coedta[cancha, equipoO, equipoE, deporte, bloque, dia] == X_coedta[cancha, equipoE, equipoO, deporte, bloque, dia] for cancha in C for deporte in D for bloque in T for equipoE in E for equipoO in E if equipoE != equipoO for dia in A), "C10"
        )

    # m.addConstrs((quicksum(a_rpt[punto, producto, tiempo] for punto in R for producto in S) >= 1 for tiempo in T), "c9")

    # m.addConstrs((X_coedta[cancha, equipo, equipo, deporte, bloque, dia] == 0 for cancha in C for equipo in E for bloque in T for dia in A for deporte in D), "C10")
    print("R10 lista")
    # Optimizar
    m.optimize()

    print("Num Vars: ", len(m.getVars()))
    print("Num Restricciones: ", len(m.getConstrs()))

    status = m.status

    print('Status:', status)

    if status != GRB.Status.OPTIMAL:
        print('Optimization was stopped with status %d' % status)
        # exit(0)

    if status == GRB.Status.INF_OR_UNBD:
        print('The model cannot be solved because it is infeasible or unbounded')

    if status == GRB.Status.INFEASIBLE:
        print("Model is INFEASIBLE")

    if status == GRB.Status.UNBOUNDED:
        print('Model is UNBOUNDED')
        # exit(1)

    if status == GRB.Status.OPTIMAL or status == 2:

        with open('results.txt', 'w') as archivo:
            # Por si queremos poner el archivo resultados los valores de algunos parametro importantes
            # archivo.write(str(G_p) + '\r\n')
            # archivo.write(str(V) + '\r\n')
            # archivo.write(str(D) + '\r\n')
            # archivo.write(str(len(T)) + '\r\n')

            print('Obj:', m.objVal)
            archivo.write('\nObj: {} \r\n'.format(m.objVal))

            archivo.write("\nVariables No 0\n")

            for v in m.getVars():
                if v.x != 0.0:
                    archivo.write('{}, {} \r\n'.format(v.varName, v.x))

            archivo.write("\nTodas las Vars\n")

            for v in m.getVars():
                # print(v.varName, v.x)
                archivo.write('{}, {} \r\n'.format(v.varName, v.x))

        with open('cons.txt', 'w') as const_file:
            for c in m.getConstrs():
                const_file.write('{}, {} \r\n'.format(c.constrName, c.slack))

except GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e) + '-' + str(e.message))

# except: # catch *all* exceptions
#    e = sys.exc_info()
#    print("Error: {}".format(str(e)))
