from math import log10

class Posting:

    def __init__(self, docID, score):
        self.docID = docID
        self.score = score

    def __repr__(self):
        return str(self.docID)