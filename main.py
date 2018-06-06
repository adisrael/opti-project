from gurobipy import *
import random
import sys

# Run on Mac OSX: time(gurobi.sh entrega-2.py) in the folder containing file

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

    # Tiempo en minutos
    # T = [i + 1 for i in range(7 * 6)] si usamos intervalos de 10 min
    T = [i + 1 for i in range(7 * 60)]  # si dejamos el original

    # Equipos
    # 10 colegios en total
    E = [i + 1 for i in range(10)]  

    # Conjunto de dias en un mes en los que se puede jugar partidos(Sabado y Domingo intercalado).
    # A = [i + 1 for i in range(8)]
    A = [i + 1 for i in range(2)]

    # P_d: Cantidad de partidos de liga del deporte d, con l in L.
    # por ahora 3 a 5 partidos por deporte por liga
    P_d = [4,4,3,3,5,5,5,5,3,3]

    # n_d: personas por equipo en el deporte d in D
    n_d = [22, 22, 13, 13, 13, 13, 15, 15, 16, 16]

    # duracion del partido del deporte d in D
    t_d = [120, 120, 90, 90, 70, 70, 90, 90, 80, 80]

    # cantidad de vehiculos por equipo e
    veh_e = [11, 11, 9, 9, 9, 9, 8, 8, 10, 10]

    # bonificacion para los deportes, 100 para todos
    b_d = [100 for i in range(10)]

    # minimo de partidos del deporte d in D
    minp_d = 1

    # cantidad maxima de espectadores en la cancha c in C
    emax_c = [100, 100, 60, 20, 20]

    # capacidad maxima del camarin
    mc = 20

    # capacidad maxima del estacionamiento
    mveh = 100

    # cantidad de buses que caben en el estacionamiento
    mbus = 10

    # si en la cancha c se puede jugar el deporte d = 1, 0 e.o.c.
    s_cd = [[1, 1, 0, 0, 0, 0, 0, 0, 0, 0],  # 1 -> Futbol
            [0, 0, 1, 1, 0, 0, 1, 1, 1, 1],  # 2 -> Gimnasio: Futsal, Volley, Basquet
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],  # 3 -> Handbol
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1],  # 4 -> Fuera1: Basquet,Volley
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1]]  # 5 -> Fuera2: Basquet,Volley

    # q_ed = [[0 for i in range(50)] for i in range(10)]  # original

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

    # si el equipo e comienza a jugar contra el equipo o en la cancha c, el deporte d, en el minuto t del dia a
    X_coedta = m.addVars(C, E, E, D, T, A, vtype=GRB.BINARY, name="x")

    # Si el equipo e llega en bus en el tiempo t en el dia a
    B_eta = m.addVars(E, T, A, vtype=GRB.BINARY, name="b")

    # Si el equipo e llega en vehiculos en el tiempo t en el dia a
    V_eta = m.addVars(E, T, A, vtype=GRB.BINARY, name="v")

    # FUNCION OBJETIVO
    m.setObjective(quicksum((quicksum(
        X_coedta[cancha, equipoo, equipoe, deporte, minuto, dia] * (1 / 2) for dia in A for minuto in T for cancha in C
        for equipoe in E for equipoo in E if equipoo != equipoe) - minp_d) * b_d[deporte - 1] for deporte in D),
                   GRB.MAXIMIZE)

    # Restriccion 1: Los ultimos partidos de un dia deben terminar antes del cierre de canchas
    m.addConstrs(
        (X_coedta[cancha, equipoO, equipoE, deporte, minuto, dia]*minuto + t_d[deporte-1] <= 4 * 60 for equipoE in E for equipoO in E if equipoE != equipoO for cancha in C for dia in A for minuto in T
         for deporte in D), 'C1')

    # Restriccion 2: Se puede jugar en una cancha si esta lo permite
    m.addConstrs(
        (X_coedta[cancha, equipoO, equipoE, deporte, minuto, dia] <= s_cd[cancha-1][deporte-1] * q_ed[deporte-1][
        equipoE-1] * q_ed[deporte-1][equipoO-1] for equipoE in E for equipoO in E if equipoE != equipoO for cancha in C for deporte in D
        for minuto in T for dia in A), "c3")

    # Restriccion 4: Cada equipo puede jugar como maximo una vez al dia
    m.addConstrs(
        (quicksum(X_coedta[cancha, equipoO, equipoE, deporte, minuto, dia] for cancha in C for deporte in D for minuto in T)
        <= 1 for equipoE in E for equipoO in E if equipoE != equipoO for dia in A), "c4")

    # Restriccion 5: Se debera jugar como minimo un partido por liga durante el mes
    m.addConstrs(
        (quicksum(X_coedta[cancha, equipoO, equipoE, deporte, minuto, dia] for cancha in C for equipoE in E for equipoO in E
        if equipoE != equipoO for minuto in T for dia in A) <= 1 for deporte in D), "c5")

    # Restriccion 6: Si un equipo juega, tiene parte de los estacionamientos ocupados (autos y buses)
    m.addConstrs(
        (B_eta[equipo, minuto, dia] <= X_coedta[cancha, equipoO, equipoE, deporte, minuto, dia]
        for equipo in E for cancha in C for equipoE in E for equipoO in E if equipoE != equipoO
        for deporte in D for minuto in T for dia in A), "c61")
    m.addConstrs(
        (V_eta[equipo, minuto, dia] <= X_coedta[cancha, equipoO, equipoE, deporte, minuto, dia]
        for equipo in E for cancha in C for equipoE in E for equipoO in E if equipoE != equipoO
        for deporte in D for minuto in T for dia in A), "c62")

    # Restriccion 7: Cada equipo esta coordinado en llegar solo en bus o en auto
    m.addConstrs(
        (V_eta[equipo, minuto, dia] + B_eta[equipo, minuto, dia] <= 1
        for equipo in E for minuto in T for dia in A), "c7")

    # Restriccion 8: No. de autos estacionados no puede superar capacidad max de estacionamientos
    m.addConstrs(
        (quicksum(V_eta[equipo, minuto, dia] for equipo in E) <= mveh
        for minuto in T for dia in A), "c8")

    # Restriccion 9: No. de buses estacionados no puede superar capacidad max de estacionamientos
    m.addConstrs(
        (quicksum(B_eta[equipo, minuto, dia] for equipo in E) <= mbus
        for minuto in T for dia in A), "c9")

    # Restriccion 10: Ctdad. de jugadores que usan los camarines tiene que ser menor a su capacidad maxima para H y M
    m.addConstrs(
        (quicksum(X_coedta[cancha, equipoO, equipoE, deporte, minuto, dia] * n_d[deporte-1] for cancha in C for equipoE in E for equipoO in E
        if equipoE != equipoO for minuto in T for dia in A) <= 2 * mc for deporte in D if deporte % 2 != 0), "c101")
    m.addConstrs(
        (quicksum(X_coedta[cancha, equipoO, equipoE, deporte, minuto, dia] * n_d[deporte-1] for cancha in C for equipoE in E for equipoO in E
        if equipoE != equipoO for minuto in T for dia in A) <= 2 * mc for deporte in D if deporte % 2 == 0), "c102")

    # Restriccion 11: Ctdad. de espectadores para c/partido no debe superar capacidad max de c/cancha
    m.addConstrs(
        (quicksum(V_eta[equipo, minuto, dia] for equipo in E) * 2 * n_d[deporte-1] <= emax_c[cancha-1]
        for cancha in C for minuto in T for dia in A for deporte in D), "c11")

    # m.addConstrs((quicksum(a_rpt[punto, producto, tiempo] for punto in R for producto in S) >= 1 for tiempo in T), "c9")

    # Optimizar
    m.optimize()

    status = m.status

    print('Status:', status)

    if status == GRB.Status.INF_OR_UNBD or status == GRB.Status.INFEASIBLE or status == GRB.Status.UNBOUNDED:
        print('The model cannot be solved because it is infeasible or unbounded')
        exit(1)

    if status != GRB.Status.OPTIMAL:
        print('Optimization was stopped with status %d' % status)
        exit(0)

    if status == GRB.Status.OPTIMAL or status == 2:
        with open('results.txt', 'w') as archivo:
            # Por si queremos poner el archivo resultados los valores de algunos parametro importantes
            # archivo.write(str(G_p) + '\r\n')
            # archivo.write(str(V) + '\r\n')
            # archivo.write(str(D) + '\r\n')
            # archivo.write(str(len(T)) + '\r\n')

            for v in m.getVars():
                print(v.varName, v.x)
                archivo.write('{}, {} \r\n'.format(v.varName, v.x))

            print('Obj:', m.objVal)
            archivo.write('\nObj: {} \r\n'.format(m.objVal))

        with open('cons.txt', 'w') as const_file:
            for c in m.getConstrs():
                const_file.write('{}, {} \r\n'.format(c.constrName, c.slack))


    # print(len(m.getVars()), len(m.getConstrs()))

except GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e) + '-' + str(e.message))

# except: # catch *all* exceptions
#    e = sys.exc_info()
#    print("Error: {}".format(str(e)))
