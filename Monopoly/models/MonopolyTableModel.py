import pandas as pd
import Monopoly.controllers.SquareCreator as Sc

MONOPOLY_SQUARES = "Monopoly/MonopolySquares.csv"


class MonopolyTable:
    def __init__(self):
        self.squares = [] # All squares 
        self.properties = [] # Just properties

        self.data = None # Where all the csv data is going to be stored
        self.load_squares() # Load squares into the lists

    def load_squares(self):
        df = pd.read_csv(MONOPOLY_SQUARES, index_col='spaces')
        self.data = df

        property_counter = 0
        street_counter = 0

        for i in range(0, len(df['type'])):
            type = df['type'][i]
            name = df['name'][i]

            if type == 'street':
                data = (name, i, type, property_counter, int(df['cost'][i]), int(df['mortgage'][i]), int(df['rent_0'][i]), 
                    street_counter, df['color'][i], int(df['house_price'][i]))
                self.properties.append(self.load_square(Sc.create_street, data))
                property_counter += 1
                street_counter += 1

            elif type == 'railroad':
                data = (name, i, type, property_counter, int(df['cost'][i]), int(df['mortgage'][i]), int(df['rent_0'][i]))
                self.properties.append(self.load_square(Sc.create_railroad, data))
                property_counter += 1

            elif type == 'utility':
                data = (name, i, type, property_counter, int(df['cost'][i]), int(df['mortgage'][i]), int(df['multiplier_0'][i]))
                self.properties.append(self.load_square(Sc.create_utility, data))
                property_counter += 1
                
            elif type == 'community':
                data = (name, i, type)
                self.load_square(Sc.create_community, data)
                
            elif type == 'tax':
                data = (name, i, type, int(df['rent_0'][i]))
                self.load_square(Sc.create_tax, data)

            elif type == 'chance':
                data = (name, i, type)
                self.load_square(Sc.create_chance, data)

            elif type == 'jail-visit':
                data = (name, i, type)
                self.load_square(Sc.create_jail_visit, data)

            elif type == 'parking':
                data = (name, i, type)
                self.load_square(Sc.create_parking, data)

            elif type == 'go':
                data = (name, i, type)
                self.load_square(Sc.create_go, data)


    def load_square(self, func, data):
        (square, component) = func(data)
        self.squares.append(square)
        return component