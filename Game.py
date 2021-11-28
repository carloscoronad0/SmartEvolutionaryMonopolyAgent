import numpy as np
import Monopoly.models.BoardComponents as BCs

from Monopoly.models.BankModel import Bank
from Monopoly.models.MonopolyTableModel import MonopolyTable
from Monopoly.models.PlayerModel import Player

MTable = MonopolyTable()
(properties_data, property_list, street_list, property_dic) = MTable.load_squares()

bank = Bank(property_list, street_list, property_dic, properties_data)
player1 = Player(1, 1500, None)
player2 = Player(2, 1500, None)

bank.buy_property_transaction(0, player1)
bank.buy_property_transaction(2, player1)
print(player1.properties)

print("\n-------------------------------------------------\n")

bank.buy_property_transaction(1, player1)
print(player1.properties)

print("\n-------------------------------------------------\n")

(valid, args) = bank.improve_property_transaction([0,1], player1)
print(valid)
print(args)
print(player1.properties)

print("\n-------------------------------------------------\n")

bank.buy_property_transaction(4, player2)
print(player2.properties)
print("\n-------------------------------------------------\n")

(valid, args) = bank.improve_property_transaction([3], player2)
print(valid)
print(args)
print(player2.properties)

print("\n-------------------------------------------------\n")

(valid, args) = bank.unimprove_property_transaction([1], player1)
print(valid)
print(args)
print(player1.properties)

print("\n-------------------------------------------------\n")
print("Mortgaging")
print("\n-------------------------------------------------\n")

(valid, args) = bank.mortgage_transaction([0], player1)
print(valid)
print(args)
print(player2.properties)

print("\n-------------------------------------------------\n")
print("Free from mortgage")
print("\n-------------------------------------------------\n")
(valid, args) = bank.free_mortgage_transaction([0], player1)
print(valid)
print(args)
print(player2.properties)

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

# a = np.array(MTable.property_dic['yellow'][1])
# print(a)
