from math import log10

class Posting:

    def __init__(self, docID, occur = 1):
        self.docID = docID
        self.occur = occur
        self.tf = None

    def countOccur(self):
        self.occur += 1
    
    def calcTermFreq(self):
        self.tf = 1 + log10(self.occur)
        return self.tf
    
    def normalize(self, doc_length):
        self.tf /= doc_length

    def __repr__(self):
        return str(self.docID)



        '''tokens = sorted(tokens)
        token_length = len(tokens)
        doc_length=0
        postings = []   #list of pointer to created postings (update with normalization)

        for i in range(0 , token_length):  #Iterate over token of documents
            
            word = tokens[i]

            if word not in self.invertedIndex:  #word didnt exist in invertedInddex
                posting = Posting(self.docID)
                self.invertedIndex[word] = [1, [posting]]
                postings.append(posting)
            else:
                posting = self.invertedIndex[word][1][-1]
                if self.docID != posting.docID:  #word did not happen previously in same doc.
                    posting = Posting(self.docID)
                    self.invertedIndex[word][1].append(posting)
                    postings.append(posting)
                    self.invertedIndex[word][0] += 1
                
                else:                           #word occurred previously in doc
                    posting.countOccur()

            if i == token_length-1 or word!=tokens[i+1]:
                doc_length += posting.calcTermFreq() ** 2
        
        doc_length = sqrt(doc_length)
        for post in postings:
            post.normalize(doc_length)'''