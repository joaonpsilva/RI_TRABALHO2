import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("-tokenizer", type=int, default=2, choices=[1, 2], help="tokenizer")
parser.add_argument("-f", type=str, default="../all_sources_metadata_2020-03-13.csv", help="text")
parser.add_argument("-l", type=str, help="Load Inverted Index")
parser.add_argument("-i", type=str, choices=['bm25', 'tfidf'], required=True)
parser.add_argument("-out", type=str, help="Output file to save Inverted Index")
args = parser.parse_args()


#TOKENIZER
if args.tokenizer == 1:
    from Tokenizer1 import Tokenizer1
    tokenizer = Tokenizer1()
else:
    from Tokenizer2 import Tokenizer2
    tokenizer = Tokenizer2()

#INDEXER
if args.i == 'bm25':
    from BM25_Indexer import BM25_Indexer
    indexer = BM25_Indexer(tokenizer)
else:
    from Tf_Idf_Indexer import Tf_idf_Indexer
    indexer = Tf_idf_Indexer(tokenizer)

if (args.l != None):    #LOAD INV IND FROM FILE
    t1 = time.time()
    indexer.read_file(args.l)
    t2 = time.time()
    print('Loading Time: ', t2-t1)

else:                   #BUILD INV IND FROM CORPUS
    from Corpus import CorpusReader
    corpusreader = CorpusReader(args.f)
    t1 = time.time()
    indexer.index(corpusreader)
    t2 = time.time()
    print('Indexing Time: ', t2-t1)

# QUERY
query = input("Query: ")
print(indexer.score(query))

if (args.out != None):
    #savefile
    indexer.write_to_file(args.out)
