from Corpus import CorpusReader
from Tokenizer1 import Tokenizer1
from Tokenizer2 import Tokenizer2
import time
import heapq
import argparse
import os
import psutil
import pickle

process = psutil.Process(os.getpid())


class Indexer():
    def __init__(self, corpus, tokenizer):
        self.corpusreader = corpus
        self.tokenizer = tokenizer
        self.idMap = {}
        self.invertedIndex = {}
        self.docID = 0
        self.idMapFile = "idMapFile.pickle"

        with open(self.idMapFile, 'wb') as f:  # Init or clean file
            pickle.dump({}, f)

    def hasEnoughMemory(self):
        return True

    def idMapToDisk(self):
        with open(self.idMapFile, 'rb') as f:
            content = pickle.load(f)

        content.update(self.idMap)

        with open(self.idMapFile, 'wb') as f:
            pickle.dump(content, f)

        self.idMap = {}

    def addTokensToIndex(self, tokens):
        for word in tokens:  # Iterate over token of documents

            if word not in self.invertedIndex:
                self.invertedIndex[word] = [1, [self.docID]]
            else:
                if self.docID != self.invertedIndex[word][1][
                    -1]:  # check if word did not happen previously in same doc.
                    self.invertedIndex[word][1].append(self.docID)
                    self.invertedIndex[word][0] += 1

    def index(self):

        count = 0
        while self.hasEnoughMemory():

            data = self.corpusreader.getNextChunk()
            if data is None:
                print("Finished")
                break

            for document in data:  # Iterate over Chunk of documents
                doi, title, abstract = document[0], document[1], document[2]
                self.idMap[self.docID] = doi  # map ordinal id used in index to real id

                tokens = self.tokenizer.process(title, abstract)

                self.addTokensToIndex(tokens)

                self.docID += 1

            count += self.docID  # Write id map tp disk
            if count >= 10000:
                self.idMapToDisk()
                count = 0

        self.idMapToDisk()  # id map not needed, free memory

    def write_to_file(self, file="Index.txt"):
        print("Writing to {}".format(file))
        # Apagar o ficheiro caso ele exista
        try:
            os.remove(file)
        except OSError:
            pass

        # Abrir o ficheiro em "append" para adicionar linha a linha (em vez de uma string enorme)
        f = open(file, "a")

        for term, values in self.invertedIndex.items():
            string = ('{}:{}'.format(term, values[0]))
            for posting in values[1]:
                string += (';{}:{}'.format(posting.docID, posting.score))
            string += "\n"
            f.write(string)

        print("File {} created".format(file))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-tokenizer", type=int, choices=[1, 2], required=True, help="tokenizer")
    parser.add_argument("-f", type=str, default="all_sources_metadata_2020-03-13.csv", help="text")
    args = parser.parse_args()

    corpusreader = CorpusReader(args.f)
    if args.tokenizer == 1:
        tokenizer = Tokenizer1()
    else:
        tokenizer = Tokenizer2()

    # CREATE INDEXER
    indexer = Indexer(corpusreader, tokenizer)

    # GET RESULTS
    t1 = time.time()
    indexer.index()
    t2 = time.time()

    print('seconds: ', t2 - t1)
    print("Total memory used by program: ", process.memory_info().rss)

    keyList = list(indexer.invertedIndex.keys())
    print('Vocabulary size: ', len(keyList))

    lessUsed = heapq.nsmallest(10, indexer.invertedIndex.items(), key=lambda item: (item[0], item[1][0]))
    print("First 10 terms with 1 doc freq: ", [i[0] for i in lessUsed])

    mostUsed = heapq.nlargest(10, indexer.invertedIndex.items(), key=lambda item: item[1][0])
    print("Higher doc freq: ", [(i[0], i[1][0]) for i in mostUsed])
