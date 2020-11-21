import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("-tokenizer", type=int, default=2, choices=[1, 2], help="tokenizer")
parser.add_argument("-c", type=str, default="../metadata_2020-03-27.csv", help="Corpus file")
parser.add_argument("-l", type=str, help="Load Inverted Index")
parser.add_argument("-i", type=str, choices=['bm25', 'tfidf'], required=True, help="Indexer")
parser.add_argument("-out", type=str, help="Output file to save Inverted Index")
parser.add_argument("--query", action="store_true", help="Process Queries")
args = parser.parse_args()


# Retorna um dicionario com formato {numero_da_query : [lista de docs relevantes]}
def getRelevantDocs():
    queries_relevance = open("../queries.relevance.txt", "r")  # File with the relevant queries
    Lines = queries_relevance.readlines()
    docs_relevance = {}

    for line in Lines:
        line = line.split()
        if line[0] in docs_relevance:
            docs_relevance[line[0]].append(line[1])
        else:
            docs_relevance[line[0]] = [line[1]]

    return docs_relevance


def calculatePrecision(retrieved_docs, relevantList):
    interseption = list(set(retrieved_docs) & set(relevantList))
    precision = len(interseption) / len(retrieved_docs)
    return precision


def calculateRecall(retrieved_docs, relevantList):
    interseption = list(set(retrieved_docs) & set(relevantList))
    recall = len(interseption) / len(relevantList)
    return recall


def calculateF_Measure(precision, recall):
    return (2 * precision * recall) / (precision + recall)


def calculateAveragePrecision(retrieved_docs, relevantList):
    averagePrecision = 0
    ret_docs = []
    relevantCount = 0
    for doc in retrieved_docs:
        ret_docs.append(doc)
        if doc in relevantList:
            averagePrecision += calculatePrecision(ret_docs, relevantList)
            relevantCount += 1

    averagePrecision = averagePrecision / relevantCount
    return averagePrecision

    # TOKENIZER


def calculateMean(valores):
    precision = 0
    recall = 0
    f_measure = 0
    avgPrecision = 0
    latecy = 0
    size = len(valores.keys())
    for key in valores.keys():
        precision += valores[key]["precision"]
        recall += valores[key]["recall"]
        f_measure += valores[key]["f-measure"]
        avgPrecision += valores[key]["average Precision"]
        latecy += valores[key]["latecy"]

    precision /= size
    recall /= size
    f_measure /= size
    avgPrecision /= size
    latecy /= size

    return {"precision": precision, "recall": recall, "f-measure": f_measure, "average Precision": avgPrecision,
            "latecy": latecy}


if args.tokenizer == 1:
    from Tokenizer1 import Tokenizer1

    tokenizer = Tokenizer1()
else:
    from Tokenizer2 import Tokenizer2

    tokenizer = Tokenizer2()

# INDEXER
if args.i == 'bm25':
    from BM25_Indexer import BM25_Indexer

    indexer = BM25_Indexer(tokenizer)
else:
    from Tf_Idf_Indexer import Tf_idf_Indexer

    indexer = Tf_idf_Indexer(tokenizer)

# INV_INDEX
if args.l is not None:  # LOAD INV IND FROM FILE
    t1 = time.time()
    indexer.read_file(args.l)
    t2 = time.time()
    print('Loading Time: ', t2 - t1)

else:  # BUILD INV IND FROM CORPUS
    from Corpus import CorpusReader

    corpusreader = CorpusReader(args.c)
    t1 = time.time()
    indexer.index(corpusreader)
    t2 = time.time()
    print('Indexing Time: ', t2 - t1)

# PROCESS QUERIES
valores = {}  # dicionario de dicionario com formato {numero_da_query : {precision: valor , recall:valor , ...}
relevant_docs = getRelevantDocs()  # dicionario com formato {numero_da_query : [lista de docs relevantes]}

if args.query:
    import xml.etree.ElementTree as ET

    root = ET.parse('../queries.txt.xml').getroot()

    for size in [10, 20, 50]:
        for entrie in root.findall('topic'):
            number = entrie.get('number')
            query = entrie.find('query').text

            print(number, ' - ', query)

            start_time = time.time()
            retrieved_docs = indexer.score(query, size)
            print(indexer.score(query, size))

            valores[number] = {}  # inicializar o dicionario nested

            valores[number]["latecy"] = (time.time() - start_time)
            precision = valores[number]["precision"] = calculatePrecision(retrieved_docs, relevant_docs[number])
            recall = valores[number]["recall"] = calculateRecall(retrieved_docs, relevant_docs[number])
            valores[number]["f-measure"] = calculateF_Measure(precision, recall)
            valores[number]["average Precision"] = calculateAveragePrecision(retrieved_docs, relevant_docs[number])

        valores["mean"] = calculateMean(valores)

        # Guardar os valores no respetivo dicionario
        if size == 10:
            valores10 = dict(valores)   # sem o dict ia copiar a referencia
        elif size == 20:
            valores20 = dict(valores)
        else:
            valores50 = dict(valores)

    # Print da tabela
    # print(valores)
    from prettytable import PrettyTable

    for size in [10, 20, 50]:
        if size == 10:
            valores = valores10
        elif size == 20:
            valores = valores20
        elif size == 50:
            valores = valores50
        t = PrettyTable(['Query', 'Precision', 'Recall', 'F-Measure', 'Average Precision', 'Latency'])
        print("Query size: {}".format(size))
        for key in valores:
            t.add_row([key, valores[key]["precision"], valores[key]["recall"], valores[key]["f-measure"],
                       valores[key]["average Precision"], valores[key]["latecy"]])

        print(t)

# SAVE INDEX
if args.out is not None:
    indexer.write_to_file(args.out)
