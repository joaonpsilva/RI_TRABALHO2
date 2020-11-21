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

    def __init__(self,tokenizer, k1=1.2, b=0.75):
        super().__init__(tokenizer)
        self.k1 = k1
        self.b = b
        self.docLength = {}
        self.avdl = 0

    def build_idf(self):
        for term, valList in self.invertedIndex.items():
            valList[0] = log10(self.docID/valList[0])


    def index(self, corpusreader):
        super().index(corpusreader)
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

    def score(self, query):
        queryTokens = self.tokenizer.process(query)
        
        doc_scores = {}
        for term in queryTokens:

            if term not in self.invertedIndex:
                continue

            idf = self.invertedIndex[term][0]
            for doc in self.invertedIndex[term][1]:

                score = idf * (((self.k1 + 1) * doc.score) / 
                    (self.k1 * ((1-self.b) + self.b*(self.docLength[doc.docID] / self.avdl)) + doc.score))

                if doc.docID in doc_scores:
                    doc_scores[doc.docID] += score
                else:
                    doc_scores[doc.docID] = score

        bestDocs = heapq.nlargest(10, doc_scores.items(), key=lambda item: item[1])

        return [self.idMap[docid] for docid, score in bestDocs]
    
    def read_file(self, file="../Index.txt"):
        self.docLength={}
        super().read_file(file)
        self.avdl = sum(self.docLength.values())

    def buildPostingList(self, line):
        postingList = []
        for values in line[1:]:
            docid = int(values.split(":")[0])
            tf = int(values.split(":")[1])
            postingList.append(Posting(docid, tf))

            if docid in self.docLength:
                self.docLength[docid] += tf
            else:
                self.docLength[docid] = tf
        
        return postingList
        


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-tokenizer", type=int, default=2, choices=[1, 2], help="tokenizer")
    parser.add_argument("-c", type=str, default="../metadata_2020-03-27.csv", help="Corpus file")
    args = parser.parse_args()

    corpusreader = CorpusReader(args.c)
    if args.tokenizer == 1:
        tokenizer = Tokenizer1()
    else:
        tokenizer = Tokenizer2()

    #CREATE INDEXER
    indexer = BM25_Indexer(tokenizer)
    
    #GET RESULTS
    t1 = time.time()
    indexer.index(corpusreader)
    t2 = time.time()

    print('seconds: ', t2-t1)
    print("Total memory used by program: ", process.memory_info().rss)
    
    keyList = list(indexer.invertedIndex.keys())
    print('Vocabulary size: ', len(keyList))

    indexer.write_to_file()

    #QUERY

    query = input("Query: ")
    print(indexer.score(query))

