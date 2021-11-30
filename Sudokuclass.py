import segedfv as sfv
import math
from datetime import datetime

#Dekorator
def ido(func):
    def wrapper(*args, **kwargs):
        start = datetime.now()

        func(*args, **kwargs)

        end = datetime.now()

        print("Futási idő: ", end - start)

        return func(*args, **kwargs)

    return wrapper

class Sudoku:
    '''
    ez a Sudokuk osztálya
    '''

    def __init__(self, mezok=[[0 for i in range(9)] for i in range(9)]):

        '''
        minden Sudokut egy 9x9-es ,,listák egy listában,, szimbolizál
        '''

        self.mezok = mezok

        beirt_mezok = {}
        for i in range(9):
            for j in range(9):
                if mezok[i][j] != 0:
                    beirt_mezok[9 * i + j + 1] = mezok[i][j]

        self.beirt_mezok = beirt_mezok

    def __str__(self):

        '''
        a gyakorlatról lopva
        '''

        allapot = " +" + 9 * "---+" + "\n"
        for i in range(9):
            sor = "|"
            for j in range(9):
                sor += f" {self.mezok[i][j]} |"
            allapot += f" {sor} \n +" + 9 * "---+" + "\n"

        return str(allapot)

    def uj_ertekek(self, mezok, ertekek):
        for i in range(len(mezok)):
            sor = math.ceil(mezok[i] / 9) - 1
            oszlop = mezok[i] % 9 - 1
            self.mezok[sor][oszlop] = ertekek[i]
            self.beirt_mezok[mezok[i]] = ertekek[i]
        return self

    @ido
    def megold_K(self, k, gen = sfv.L_best):
        '''
        megoldja a Sudokut úgy, hogy mindig k mezőre emlékszik csak
        '''
        L = gen(k)
        beirt_mezok = self.beirt_mezok.copy()

        verbose = True
        while verbose:
            verbose = False
            for l in L:
                uj_mezok = sfv.ujmezo(beirt_mezok, l)
                if uj_mezok == 0:
                    return "Nem lehet megoldani"
                for mezo in uj_mezok:
                    x, y = sfv.valtozobol_mezo(mezo)
                    beirt_mezok[x] = y
                if uj_mezok != []:
                    verbose = True

        if len(beirt_mezok) != 81:
            return "Nem tudja megoldani"

        self.beirt_mezok = beirt_mezok
        Sudoku.uj_ertekek(self, list(beirt_mezok.keys()), list(beirt_mezok.values()))

        return self