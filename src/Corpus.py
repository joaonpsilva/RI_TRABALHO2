from pandas import read_csv



class CorpusReader():

    def __init__(self, csvfile, chunkSize=10000):
        self.fileIterator = read_csv(csvfile, chunksize=chunkSize, iterator=True)

    def getNextChunk(self):
        try:
            chunk = self.fileIterator.get_chunk()
        except StopIteration:
            return None

        chunk = chunk.dropna(subset=['abstract'])   #drop empty abstract
        chunk = chunk[['doi', 'title', 'abstract']] #keep only these fields

        return chunk.values
