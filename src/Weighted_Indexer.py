import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("-tokenizer", type=int, default=2, choices=[1, 2], help="tokenizer")
parser.add_argument("-c", type=str, default="../metadata_2020-03-27.csv", help="Corpus file")
parser.add_argument("-l", type=str, help="Load Inverted Index")
parser.add_argument("-i", type=str, choices=['bm25', 'tfidf'], required=True, help="Indexer")
parser.add_argument("-out", type=str, help="Output file to save Inverted Index")
parser.add_argument("--query",action="store_true" , help="Process Queries")
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


#INV_INDEX
if (args.l != None):    #LOAD INV IND FROM FILE
    t1 = time.time()
    indexer.read_file(args.l)
    t2 = time.time()
    print('Loading Time: ', t2-t1)

else:                   #BUILD INV IND FROM CORPUS
    from Corpus import CorpusReader
    corpusreader = CorpusReader(args.c)
    t1 = time.time()
    indexer.index(corpusreader)
    t2 = time.time()
    print('Indexing Time: ', t2-t1)

# PROCESS QUERIES
if (args.query):
    import xml.etree.ElementTree as ET
    root = ET.parse('../queries.txt.xml').getroot()

    for entrie in root.findall('topic'):
        number = entrie.get('number')
        query = entrie.find('query').text

        print(indexer.score(query))
        break
    
#SAVE INDEX
if (args.out != None):
    indexer.write_to_file(args.out)
