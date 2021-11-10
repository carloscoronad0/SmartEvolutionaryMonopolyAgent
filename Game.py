from Monopoly.models.MonopolyTableModel import MonopolyTable
import numpy as np
import Monopoly.models.BoardComponents as p


MT = MonopolyTable()
# print(MT.properties[0].name)
# print(MT.properties[6].street_color)
# print("---------------------------------------")

# for i in range(0, len(MT.squares)):
#    print(MT.squares[i].board_component.name)

# print("---------------------------------------")

# for i in range(0, len(MT.properties)):
#    print(MT.properties[i])

# import numpy as np

# def proving_numpy(arr: np.ndarray) -> np.ndarray:
#     c = np.where(arr == 3)
#     return c

# a = np.array([3,1,2,3,1,2,1,2,3,3,4,1])
# print(a)

a = np.array(MT.properties)
print(a)