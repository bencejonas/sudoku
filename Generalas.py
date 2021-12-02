import pulp as pl
import Segedfv as sfv
import random
import math

##itt generálunk nehezen megoldhatót, mivel a megoldásunk abból indul ki, hogy minél mező ismert egy 3x3-asban,
##annál jobb, ezért úgy generálunk, hogy az ismert mezőt legyenk minél jobban szétosztva a különböző 3x3-asok között
##megoldunk egy üres Sudokut(egy mezőt random mindig kitöltetünk, különben folyton ua a mo.-t kapnánk)
##ezután addig vesszük el sorban a mezőket, amíg még megoldható, a lényeg, hogy mindig másik 3x3-asból vesszük el,
##hogy minél jobban szét legyen osztva

def nehez_gen():
    '''
    megad egy nagy K-ra megoldható Sudokut
    '''

    ##megoldok egy Sudokut, aminek 1 mezője van kitöltve
    seged1 = pl.LpProblem(name="seged1")

    idx1 = [i for i in range(9 ** 3)]
    M1 = pl.LpVariable.dicts(name="segéd1_mező",
                             indexs=idx1,
                             lowBound=0,
                             upBound=1,
                             cat=pl.LpBinary)

    szabaly = []
    for i in range(81):
        szabaly.append([j + 9 * i for j in range(9)])
    for i in range(9):
        for j in range(9):
            szabaly.append([9 * k + 81 * j + i for k in range(9)])
    for i in range(9):
        for j in range(9):
            szabaly.append([81 * k + 9 * j + i for k in range(9)])
    for i in range(9):
        for j in [0, 3, 6, 27, 30, 33, 54, 57, 60]:
            szabaly.append([9 * k + 9 * j + i for k in [0, 1, 2, 9, 10, 11, 18, 19, 20]])

    for szabaly in szabaly:
        seged1 += pl.lpSum(M1[j] for j in szabaly) == 1

    seged1.solve()
    ##eddig tart az első sudoku megoldása

    ##elmentem egy listába a kapott értékeket
    seged1_ertekek = [0 for i in range(729)]
    for i in idx1:
        seged1_ertekek[i] = pl.value(M1[i])

        ##létrehozunk egy listát, ami tartalmazza, hogy melyik 3x3asban melyik változónak az értéke 1
    harmasok = [[] for i in range(9)]
    for i in range(729):
        if pl.value(M1[i]) == 1:
            harmasok[sfv.melyik_3as(i)].append(i)

    ##ezeket megkeverem
    for i in range(9):
        random.shuffle(harmasok[i])

    ##megkeverve berakom őket sorban egy listába, tehát úgy lesznek benne elemek, hogy az 3x3-asból egy változó,
    ##aztán a másodikból, stb a 9.-ig, és ez elölről
    sorban = []
    for i in range(9):
        for j in harmasok:
            sorban.append(j[i])

    ##először kiveszek összvissz egy ismert mezőt
    ismert = sorban[1:]
    ##az utolso jelöli azt, hogy ezt szeretném legközelebb törölni
    utolso = ismert[0]
    ##ha az ismetlesek száma a lista hossza lesz, az azt jelenti, hogy akármit vettünk ki, úgy már nem megoldható
    ismetles = 0

    ##most megoldok még egyet, azzal a célfüggvénnyel, hogy minél több különbözzön, ha ua.-t kapom, akkor megpróbálok még egy mezőt törölni
    egyedi = True
    while egyedi:
        seged2 = pl.LpProblem(name="seged2")  # vagy pl.LpMinimize (ez a default)

        idx2 = [i for i in range(729)]
        M2 = pl.LpVariable.dicts(name="segéd2_mező",
                                 indexs=idx2,
                                 lowBound=0,
                                 upBound=1,
                                 cat=pl.LpBinary)

        szabalyok = []
        for i in range(81):
            szabalyok.append([j + 9 * i for j in range(9)])
        for i in range(9):
            for j in range(9):
                szabalyok.append([9 * k + 81 * j + i for k in range(9)])
        for i in range(9):
            for j in range(9):
                szabalyok.append([81 * k + 9 * j + i for k in range(9)])
        for i in range(9):
            for j in [0, 3, 6, 27, 30, 33, 54, 57, 60]:
                szabalyok.append([9 * k + 9 * j + i for k in [0, 1, 2, 9, 10, 11, 18, 19, 20]])

        for szabaly in szabalyok:
            seged2 += pl.lpSum(M2[j] for j in szabaly) == 1

        for i in ismert:
            seged2 += M2[i] == 1

        seged2 += pl.lpSum(M2[i] * seged1_ertekek[i] for i in idx2)

        seged2.solve()

        ##ha nem 81 a cél, vagyis nem egyértelmű a mo., akkor visszarakom az utolsó kivett mezőt
        if pl.value(seged2.objective) != 81:
            ismert.append(utolso)

            ##ha most fordult elő először, akkor a ,,mentett,, legyen a most ismert mezők
            if ismetles == 0:
                mentett = ismert[:]
            ##növeljük az ism
            ismetles += 1
            ##frissítem az utolsó elemet, majd törlöm az ismertből
            utolso = ismert[0]
            ismert.remove(ismert[0])
            ##ha már minden elemet töröltünk egyszer, akkor ebből már nem lehet törölni, visszaadjuk ezt
            if ismetles == len(mentett):
                egyedi = False

        ##ha még így is megoldható, akkor az ismétlés 0, és törlünk még egy elemet
        else:
            ismetles = 0
            utolso = ismert[0]
            ismert.remove(ismert[0])

    ##visszaadom listaként a kapott Sudokut
    Sudoku = [[0, 0, 0, 0, 0, 0, 0, 0, 0] for i in range(9)]
    for i in mentett:
        x, y = sfv.valtozobol_mezo(i)
        Sudoku[math.ceil(x / 9) - 1][x % 9 - 1] = y

    return Sudoku