import Segedfv as sfv
import math
from datetime import datetime
from functools import wraps


# ez pedig egy dekorátor, ami kiírja, mennyi idő alatt fut le egy függvényhívás, a Sudoku megoldáshoz hasznos
def ido(fgv):
    '''
    kidekorál egy függvényt azzal, hogy mennyi idő volt, amíg lefutott
    '''

    def wrapper(*args, **kwargs):
        start = datetime.now()

        hivas = fgv(*args, **kwargs)

        vege = datetime.now()

        print("Futási idő: ", vege - start)

        return hivas

    return wrapper


class Sudoku:
    '''
    ez a Sudokuk osztálya
    '''

    #minden Sudokut egy 9x9-es ,,listák egy listában,, szimbolizál
    def __init__(self, mezok=[[0 for i in range(9)] for i in range(9)]):

        self.mezok = mezok

        beirt_mezok = {}
        for i in range(9):
            for j in range(9):
                if mezok[i][j] != 0:
                    beirt_mezok[9 * i + j + 1] = mezok[i][j]

        self.beirt_mezok = beirt_mezok

    #a gyakorlatról lopva
    def __str__(self):

        allapot = " +" + 9 * "---+" + "\n"
        for i in range(9):
            sor = "|"
            for j in range(9):
                sor += f" {self.mezok[i][j]} |"
            allapot += f" {sor} \n +" + 9 * "---+" + "\n"

        return str(allapot)

    def uj_ertekek(self, mezok, ertekek):
        '''
        kézzel meg lehet adni pár új értéket
        '''
        for i in range(len(mezok)):
            sor = math.ceil(mezok[i] / 9) - 1
            oszlop = mezok[i] % 9 - 1
            self.mezok[sor][oszlop] = ertekek[i]
            self.beirt_mezok[mezok[i]] = ertekek[i]
        return self

    @ido
    def megold_K(self, k, gen=sfv.L_best):
        '''
        megoldja a Sudokut úgy, hogy mindig k mezőre emlékszik csak, a gen függvény generálja neki az L listát
        '''
        L = gen(k)
        beirt_mezok = self.beirt_mezok.copy()

        #végigmegyünk az L elemein, ha nem tudtunk elemet beírni, vagy már ki van töltve a Sudoku, akkor végeztünk
        verbose = True
        while verbose and len(beirt_mezok) != 81:
            verbose = False
            for l in L:
                #végigmegyünk az l-eken, futtatjuk az ujmezot
                uj_mezok = sfv.ujmezo(beirt_mezok, l)
                #ha 0-t ad vissza, akkor nem megoldható a Sudokunk
                if uj_mezok == 0:
                    print("Nem lehet megoldani")
                    return self
                #amúgy beírjuk a kitalált elemeket
                for mezo in uj_mezok:
                    x, y = sfv.valtozobol_mezo(mezo)
                    beirt_mezok[x] = y
                #ha volt kitalált elem, akkor True-ra állítjuk, hogy ne lépjen ki a while ciklusból
                if uj_mezok != []:
                    verbose = True

        #ha kilépett, de nem találta ki az összes mezőt, akkor nem tudja megoldani erre a k-ra ezt a Sudokut
        if len(beirt_mezok) != 81:
            print("Nem tudja megoldani")

        self.beirt_mezok = beirt_mezok
        Sudoku.uj_ertekek(self, list(beirt_mezok.keys()), list(beirt_mezok.values()))

        return self