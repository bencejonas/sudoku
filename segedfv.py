import math
import pulp as pl
import random
import itertools as it


# segédfüggvények:


def txt_bemenet(txt):
    '''
    txt-t Sudoku bemenetnek megfelelő listává konvertál
    '''
    fajl = open(txt, "rt").read().replace("\n", " ").split(" ")
    mezok = []
    i = 0
    for j in range(9):
        sor = []
        while fajl[i] != '':
            sor.append(int(fajl[i]))
            i += 1
        i += 1
        mezok.append(sor)
    return mezok


# a változók 0-tól 728-ig lesznek számozva, a mezők 1-től 81-ig, a rajtuk lévő értékek 1-től 9-ig

def valtozobol_mezo(n):
    '''
    változót konvertál mezővé és értékke
    '''
    x = math.floor(n / 9) + 1
    y = n % 9 + 1
    return x, y


def mezobol_valtozo(x, y=1):
    '''
    mezőt és értéket konvertál változóvá
    '''
    return (x - 1) * 9 + y - 1


def ujmezo(beirt_mezok, l):
    '''
    az l listában lévő mezőkből megnézi, mit lehet egyértelműen kitalálni
    '''

    seged1 = pl.LpProblem(name="seged1")

    idx1 = [i for i in range(9 ** 3)]
    M1 = pl.LpVariable.dicts(name="segéd1_mező",
                             indexs=idx1,
                             lowBound=0,
                             upBound=1,
                             cat=pl.LpBinary)

    rules = []
    for i in range(81):
        rules.append([j + 9 * i for j in range(9)])
    for i in range(9):
        for j in range(9):
            rules.append([9 * k + 81 * j + i for k in range(9)])
    for i in range(9):
        for j in range(9):
            rules.append([81 * k + 9 * j + i for k in range(9)])
    for i in range(9):
        for j in [0, 3, 6, 27, 30, 33, 54, 57, 60]:
            rules.append([9 * k + 9 * j + i for k in [0, 1, 2, 9, 10, 11, 18, 19, 20]])

    for i in rules:
        seged1 += pl.lpSum(M1[j] for j in i) == 1

    for i in l:
        if i in beirt_mezok.keys():
            j = mezobol_valtozo(i, beirt_mezok[i])
            seged1 += M1[j] == 1

    if seged1.solve() != 1:
        return 0

    seged1_ertekek = [0 for i in range(729)]
    for i in idx1:
        seged1_ertekek[i] = pl.value(M1[i])
        ##eddig tart az első sudoku megoldása

    ##most megoldok még egyet, azzal a célfüggvénnyel, hogy minél több különbözzön

    seged2 = pl.LpProblem(name="seged2")  # vagy pl.LpMinimize (ez a default)

    idx2 = [i for i in range(729)]
    M2 = pl.LpVariable.dicts(name="segéd2_mező",
                             indexs=idx2,
                             lowBound=0,
                             upBound=1,
                             cat=pl.LpBinary)

    rules = []
    for i in range(81):
        rules.append([j + 9 * i for j in range(9)])
    for i in range(9):
        for j in range(9):
            rules.append([9 * k + 81 * j + i for k in range(9)])
    for i in range(9):
        for j in range(9):
            rules.append([81 * k + 9 * j + i for k in range(9)])
    for i in range(9):
        for j in [0, 3, 6, 27, 30, 33, 54, 57, 60]:
            rules.append([9 * k + 9 * j + i for k in [0, 1, 2, 9, 10, 11, 18, 19, 20]])

    for i in rules:
        seged2 += pl.lpSum(M2[j] for j in i) == 1

    for i in l:
        if i in beirt_mezok.keys():
            j = mezobol_valtozo(i, beirt_mezok[i])
            seged2 += M2[j] == 1

    seged2 += pl.lpSum(M2[i] * seged1_ertekek[i] for i in idx2)

    seged2.solve()

    gyanus = []
    for i in range(729):
        x, y = valtozobol_mezo(i)
        if x not in beirt_mezok.keys() and seged1_ertekek[i] == 1 and pl.value(M2[i]) == seged1_ertekek[i]:
            gyanus.append(i)

    # most pedig megnézem, a gyanúsak között, melyikek vehetnek fel más értéket is

    biztos = []
    for gyanu in gyanus:
        seged3 = pl.LpProblem(name="seged3")  # vagy pl.LpMinimize (ez a default)

        idx3 = [i for i in range(729)]
        M3 = pl.LpVariable.dicts(name="segéd3_mező",
                                 indexs=idx3,
                                 lowBound=0,
                                 upBound=1,
                                 cat=pl.LpBinary)

        rules = []
        for i in range(81):
            rules.append([j + 9 * i for j in range(9)])
        for i in range(9):
            for j in range(9):
                rules.append([9 * k + 81 * j + i for k in range(9)])
        for i in range(9):
            for j in range(9):
                rules.append([81 * k + 9 * j + i for k in range(9)])
        for i in range(9):
            for j in [0, 3, 6, 27, 30, 33, 54, 57, 60]:
                rules.append([9 * k + 9 * j + i for k in [0, 1, 2, 9, 10, 11, 18, 19, 20]])

        for i in rules:
            seged3 += pl.lpSum(M3[j] for j in i) == 1

        for i in l:
            if i in beirt_mezok.keys():
                j = mezobol_valtozo(i, beirt_mezok[i])
                seged3 += M3[j] == 1

        seged3 += M3[gyanu] == 0

        if seged3.solve() != 1:
            biztos.append(gyanu)

    return biztos


# ez még nincs kész, tulajdonképpen ennek a kitalálása a feladat lényege

##eddig ez a legjobb
def L_best(K):
    '''
    Megad egy effektív L listát.
    '''
    L = []

    szamok = [i for i in range(1, 82)]

    sor = [[1 + k + i * 9 for k in range(9)] for i in range(9)]

    oszlop = [[i + 1 + k * 9 for k in range(9)] for i in range(9)]

    harmas = [[] for i in range(9)]
    harmas[0] = [i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[1] = [3 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[2] = [6 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[3] = [27 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[4] = [30 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[5] = [33 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[6] = [54 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[7] = [57 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[8] = [60 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]

    kapcsolatok = [[1, 2, 3, 6, 4, 5, 7, 8],  # első hármasé
                   [0, 2, 4, 7, 3, 5, 6, 8],  # második hármasé
                   [0, 1, 5, 8, 4, 3, 7, 6],  # harmadik hármasé
                   [0, 6, 4, 5, 1, 7, 2, 8],  # negyedik hármasé
                   [3, 5, 1, 7, 0, 2, 6, 8],  # ötödik hármasé
                   [3, 4, 2, 8, 1, 7, 0, 6],  # hatodik hármasé
                   [0, 3, 7, 8, 4, 1, 5, 2],  # hetedik hármasé
                   [6, 8, 1, 4, 3, 5, 0, 2],  # nyolcadik hármasé
                   [6, 7, 2, 5, 4, 1, 3, 0]]  # kilencedik hármasé

    # az L listában 81 lista lesz, mindegy mezőhöz tartozik 1, amiben lévő mezők alapján szeretnénk őt kitalálni
    # tehát futtatunk 81-szer egy ciklust
    for i in szamok:
        # először belerakjuk magát a mezőt, hátha ismerjük alapból
        l = [i]

        # belerakjuk a mezőket az ő 3x3-asából, az ,,hanyadik,,
        hanyadik = -1
        for j in range(9):
            if i in harmas[j]:
                hanyadik = j
                for k in harmas[j]:
                    if k not in l:
                        l.append(k)
        for j in sor[math.ceil(i / 9) - 1]:
            if j not in l:
                l.append(j)

        for j in oszlop[(i - 1) % 9]:
            if j not in l:
                l.append(j)

        if K < 21:
            L.append(l[:K])

        else:

            kapcs = 0
            while K - len(l) > 8:
                j = kapcsolatok[hanyadik][kapcs]
                for k in harmas[j]:
                    if k not in l:
                        l.append(k)
                kapcs += 1

            m = K - len(l)

            if m != 0:
                for j in harmas[kapcsolatok[hanyadik][kapcs]][:m]:
                    if j not in l:
                        l.append(j)

                while len(l) != K:
                    j = random.randint(1, 81)
                    if j not in l:
                        l.append(j)

            L.append(l)

    return L


def L_comb(k):
    '''
    Megad egy effektív L listát kombinációk segítségével.
    '''
    L = []

    db = k // 9
    m = k % 9

    # Meghatározzuk a sor, oszlop, 3x3 mezőket
    szamok = [i for i in range(1, 82)]

    sor = [[1 + k + i * 9 for k in range(9)] for i in range(9)]

    oszlop = [[i + 1 + k * 9 for k in range(9)] for i in range(9)]

    harmas = [[] for i in range(9)]
    harmas[0] = [i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[1] = [3 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[2] = [6 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[3] = [27 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[4] = [30 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[5] = [33 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[6] = [54 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[7] = [57 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[8] = [60 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]

    # Vesszük a sor, oszlop, 3x3 kombinációkat
    sorok = list(it.combinations(sor, db))
    oszlopok = list(it.combinations(oszlop, db))
    harmasok = list(it.combinations(harmas, db))

    for i in sorok:

        seged = []
        for j in i:
            for l in j:
                seged.append(l)
        if m != 0:
            if m == 1:
                seged2 = [x for x in szamok if x not in seged]

                for i in seged2:
                    plusszos = seged.copy()
                    plusszos.append(i)

                    if sorted(plusszos) not in L:
                        L.append(plusszos)

            else:
                seged2 = [x for x in szamok if x not in seged]
                seged3 = list(it.combinations(seged2, m))
        else:
            L.append(seged)

    for i in oszlopok:
        seged = []
        for j in i:
            for l in j:
                seged.append(l)

        if m != 0:
            if m == 1:
                seged2 = [x for x in szamok if x not in seged]
                for i in seged2:

                    plusszos = seged.copy()
                    plusszos.append(i)

                    if sorted(plusszos) not in L:
                        L.append(plusszos)

            else:
                seged2 = [x for x in szamok if x not in seged]
                seged3 = list(it.combinations(seged2, m))

        elif sorted(seged) not in L:
            L.append(seged)

    for i in harmasok:
        seged = []
        for j in i:
            for l in j:
                seged.append(l)

        if m != 0:
            if m == 1:
                seged2 = [x for x in szamok if x not in seged]
                for i in seged2:
                    plusszos = seged.copy()
                    plusszos.append(i)

                    if sorted(plusszos) not in L:
                        L.append(plusszos)

            else:
                seged2 = [x for x in szamok if x not in seged]
                seged3 = list(it.combinations(seged2, m))

        elif sorted(seged) not in L:
            L.append(seged)

    return L


def L_random(K):
    '''
    Megad egy effektív L listát, úgy hogy véletlenszeűen válassza ki a mezőket.
    '''
    L = []

    szamok = [i for i in range(1, 82)]

    if K < 17:
        return "Kérlek nagyobb K értéket adj meg."
    if (81 - K) <= 1:
        if K == 81:
            L = [i for i in range(1, 82)]
        else:
            for i in szamok:
                l = [j for j in szamok]
                l.remove(i)
                L.append(l)

    else:
        while len(L) != 300:
            seged = []
            while len(seged) != K:
                seged2 = random.randrange(1, 82)
                if seged2 not in seged:
                    seged.append(seged2)
            if seged not in L:
                L.append(sorted(seged))

    return L


def L_randomcomb(K):
    '''
    megad egy effektív L listát
    '''
    L = []

    db = K // 9
    m = K % 9

    szamok = [i for i in range(1, 82)]
    sor = [[1 + k + i * 9 for k in range(9)] for i in range(9)]

    oszlop = [[i + 1 + k * 9 for k in range(9)] for i in range(9)]

    harmas = [[] for i in range(9)]
    harmas[0] = [i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[1] = [3 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[2] = [6 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[3] = [27 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[4] = [30 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[5] = [33 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[6] = [54 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[7] = [57 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]
    harmas[8] = [60 + i for i in [1, 2, 3, 10, 11, 12, 19, 20, 21]]

    osszes = sor + oszlop + harmas

    komb = list(it.combinations(osszes, db))

    for i in komb:
        l = []
        for j in i:
            for k in j:
                if k not in l:
                    l.append(k)
        while len(l) < K:
            j = random.randrange(1, 82)
            if j not in l:
                l.append(j)

        L.append(l)

    return L

