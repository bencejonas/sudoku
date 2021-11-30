import segedfv as sfv
from Sudokuclass import Sudoku
pelda1 = Sudoku(sfv.txt_bemenet("s01a.txt"))
print(pelda1)

Sudoku.megold_K(pelda1,25)
print(pelda1)