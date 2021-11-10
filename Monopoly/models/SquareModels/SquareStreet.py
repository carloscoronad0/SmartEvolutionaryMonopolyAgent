from Monopoly.models.SquareModels.Square import Square
from Monopoly.models.BoardComponents import BoardComponent


class SquareStreet(Square):
    def __init__(self, street_property: BoardComponent):
        super().__init__(street_property)

    def action(self):
        pass
