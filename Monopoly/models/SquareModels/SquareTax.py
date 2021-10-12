from Monopoly.models.SquareModels.Square import Square
from Monopoly.models.Properties import BoardComponent


class TaxSquare(Square):
    def __init__(self, tax: BoardComponent):
        super().__init__(tax)

    def action(self):
        print("Proving action")
