from Indexer import Indexer
from Corpus import CorpusReader
from Tokenizer1 import Tokenizer1
from Tokenizer2 import Tokenizer2
from Posting import Posting
import time
import heapq
import argparse
import os
import psutil
from math import log10, sqrt
import collections

process = psutil.Process(os.getpid())

class BM25_Indexer(Indexer):

    def __init__(self, corpusreader, tokenizer, k1=1.2, b=0.75):
        super().__init__(corpusreader, tokenizer)
        self.k1 = k1
        self.b = b
        self.docLength = {}
        self.avdl = 0

    def build_idf(self):
        for term, valList in self.invertedIndex.items():
            valList[0] = log10(self.docID/valList[0])


    def index(self):
        super().index()
        self.build_idf()

    def addTokensToIndex(self, tokens):
        tokens = collections.Counter(tokens).most_common() #[(token, occur)]
        dl = sum([tf for term, tf in tokens])
        self.docLength[self.docID] = dl
        self.avdl += dl

        for token, tf in tokens:
            
            posting = Posting(self.docID, tf )

            if token not in self.invertedIndex:
                self.invertedIndex[token] = [1, [posting]]
            else:
                self.invertedIndex[token][1].append(posting)
                self.invertedIndex[token][0] += 1    

    def cos_Score(self, query):
        queryTokens = self.tokenizer.process(query)
        
        doc_scores = {}
        for term in queryTokens:

            idf = self.invertedIndex[term][0]
            for doc in self.invertedIndex[term][1]:

                score = idf * (((self.k1 + 1) * doc.score) / 
                    (self.k1 * ((1-self.b) + self.b*(self.docLength[doc.docID] / self.avdl)) + doc.score))

                if doc.docID in doc_scores:
                    doc_scores[doc.docID] += score
                else:
                    doc_scores[doc.docID] = score

        bestDocs = heapq.nlargest(10, doc_scores.items(), key=lambda item: item[1])
        return bestDocs


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-tokenizer", type=int, choices=[1,2], required=True, help="tokenizer")
    parser.add_argument("-f", type=str, default="all_sources_metadata_2020-03-13.csv", help="text")
    args = parser.parse_args()

    corpusreader = CorpusReader(args.f)
    if args.tokenizer == 1:
        tokenizer = Tokenizer1()
    else:
        tokenizer = Tokenizer2()

    #CREATE INDEXER
    indexer = BM25_Indexer(corpusreader, tokenizer)
    
    #GET RESULTS
    t1 = time.time()
    indexer.index()
    t2 = time.time()

    print('seconds: ', t2-t1)
    print("Total memory used by program: ", process.memory_info().rss)
    
    keyList = list(indexer.invertedIndex.keys())
    print('Vocabulary size: ', len(keyList))

    #QUERY

    query = input("Query: ")
    print(indexer.cos_Score(query))

