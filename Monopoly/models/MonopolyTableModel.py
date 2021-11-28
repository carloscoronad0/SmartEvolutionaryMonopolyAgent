import pandas as pd
import numpy as np
import Monopoly.controllers.SquareCreator as Sc

MONOPOLY_SQUARES = "Monopoly/MonopolySquares.csv"


class MonopolyTable:
    def __init__(self):
        self.squares = [] # All squares 

    def load_squares(self):
        df = pd.read_csv(MONOPOLY_SQUARES, index_col='spaces')
        added_in_dic = []

        property_dic = {}
        properties = []
        streets = []

        property_counter = 0
        street_counter = 0

        for i in range(0, len(df['type'])):
            element_type = df['type'][i]
            name = df['name'][i]

            if element_type == 'street':
                data = (name, i, element_type, property_counter, int(df['cost'][i]), int(df['mortgage'][i]), int(df['rent_0'][i]), 
                    street_counter, df['color'][i], int(df['house_price'][i]))
                component = self.load_square(Sc.create_street, data)
                properties.append(component)
                streets.append(component)

                if added_in_dic.__contains__(df['color'][i]) == False:
                    property_dic[(df['color'][i])] = []
                    added_in_dic.append(df['color'][i])

                property_dic[df['color'][i]].append(property_counter)
                property_counter += 1
                street_counter += 1

            elif element_type == 'railroad':
                data = (name, i, element_type, property_counter, int(df['cost'][i]), int(df['mortgage'][i]), int(df['rent_0'][i]))
                properties.append(self.load_square(Sc.create_railroad, data))

                if added_in_dic.__contains__(element_type) == False:
                    property_dic[element_type] = []
                    added_in_dic.append(element_type)

                property_dic[element_type].append(property_counter)
                property_counter += 1

            elif element_type == 'utility':
                data = (name, i, element_type, property_counter, int(df['cost'][i]), int(df['mortgage'][i]), int(df['rent_0'][i]))
                properties.append(self.load_square(Sc.create_utility, data))

                if added_in_dic.__contains__(element_type) == False:
                    property_dic[element_type] = []
                    added_in_dic.append(element_type)

                property_dic[element_type].append(property_counter)
                property_counter += 1
                
            elif element_type == 'community':
                data = (name, i, element_type)
                self.load_square(Sc.create_community, data)
                
            elif element_type == 'tax':
                data = (name, i, element_type, int(df['rent_0'][i]))
                self.load_square(Sc.create_tax, data)

            elif element_type == 'chance':
                data = (name, i, element_type)
                self.load_square(Sc.create_chance, data)

            elif element_type == 'jail-visit':
                data = (name, i, element_type)
                self.load_square(Sc.create_jail_visit, data)

            elif element_type == 'parking':
                data = (name, i, element_type)
                self.load_square(Sc.create_parking, data)

            elif element_type == 'go':
                data = (name, i, element_type)
                self.load_square(Sc.create_go, data)

        return (df, properties, streets, property_dic)

    def load_square(self, func, data):
        (square, component) = func(data)
        self.squares.append(square)
        return component
