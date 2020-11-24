# RI ASSIGNEMT 2

João Silva 88813  
Bernardo Rodrigues 88835

## Run

Inside src/:

Main File Weighted_Indexer.py  
Main Options:  
 - -i [indexer] -> (tfidf, bm25)
 - -out [outFile] -> save inv. index to file and a Map with the ids to cordId
 - -l [File] -> Load inv. index from file saved with last option
 - --query -> Flag to process queries.relevance.filtered.txt (-relevance to change queries relevance file)

### EXAMPLES:  

Save index to file:  
$python3 Weighted_Indexer.py -i tfidf --query -out ../models/tfidfIndex.txt

Load index from file:  
$python3 Weighted_Indexer.py -i bm25 --query -l ../models/bm25Index.txt

### Results:

If --query is present the program will output the 50 better results for each query as well as the topics requested in 2.2 for 10, 20, 50 results. This last results can also be found in results/ folder for bm25 and tfidf ( results are rewritten everytime --query is flaged)

time:

TFI-IDF:
 - Indexing Time:  13.400408744812012
 - Loading from file Time:  4.624469757080078

BM25:
 - Indexing Time:  12.474901914596558
 - Loading from file Time:  4.624469757080078


