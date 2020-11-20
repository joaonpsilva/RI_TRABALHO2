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


class Tf_idf_Indexer(Indexer):

    def __init__(self, tokenizer):
        super().__init__(tokenizer)

    def build_idf(self):
        for term, valList in self.invertedIndex.items():
            valList[0] = log10(self.docID / valList[0])

    def index(self,corpusreader):
        super().index(corpusreader)
        self.build_idf()

    def addTokensToIndex(self, tokens):
        tokens = collections.Counter(tokens).most_common()  # [(token, occur)]

        token_weights = {term: 1 + log10(occur) for term, occur in tokens}

        doc_length = sqrt(sum([score ** 2 for score in token_weights.values()]))

        for token, score in token_weights.items():

            score /= doc_length
            posting = Posting(self.docID, score)

            if token not in self.invertedIndex:
                self.invertedIndex[token] = [1, [posting]]
            else:
                self.invertedIndex[token][1].append(posting)
                self.invertedIndex[token][0] += 1

    def score(self, query):
        queryTokens = collections.Counter(self.tokenizer.process(query)).most_common()  # [(token, occur)]

        for t in queryTokens:  # remove terms that are not indexed
            if t[0] not in self.invertedIndex:
                queryTokens.remove(t)

        query_weights = {term: ((1 + log10(occur)) * self.invertedIndex[term][0])
                         for term, occur in queryTokens}

        query_length = sqrt(sum([score ** 2 for score in query_weights.values()]))

        doc_scores = {}
        for term, termScore in query_weights.items():
            termScore /= query_length

            for doc in self.invertedIndex[term][1]:
                if doc.docID in doc_scores:
                    doc_scores[doc.docID] += doc.score * termScore
                else:
                    doc_scores[doc.docID] = doc.score * termScore

        bestDocs = heapq.nlargest(10, doc_scores.items(), key=lambda item: item[1])
        return bestDocs


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-tokenizer", type=int, default=2, choices=[1, 2], help="tokenizer")
    parser.add_argument("-f", type=str, default="../all_sources_metadata_2020-03-13.csv", help="text")
    args = parser.parse_args()

    corpusreader = CorpusReader(args.f)
    if args.tokenizer == 1:
        tokenizer = Tokenizer1()
    else:
        tokenizer = Tokenizer2()

    # CREATE INDEXER
    indexer = Tf_idf_Indexer(tokenizer)

    # GET RESULTS
    t1 = time.time()
    indexer.index(corpusreader)
    t2 = time.time()

    print('seconds: ', t2 - t1)
    print("Total memory used by program: ", process.memory_info().rss)

    keyList = list(indexer.invertedIndex.keys())
    print('Vocabulary size: ', len(keyList))

    # QUERY
    query = input("Query: ")
    print(indexer.score(query))