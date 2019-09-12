# Wikipedia-Search-Engine

## Step 1 : Installing Requirements

Since I use an external stemmer, you must install "stemming" module for python using pip (Mentioned in requirements.txt)

## Step 2 : Parsing the Data

To parse the data, run the file "Indexer.py"
To run the file, the syntax is "python3 Indexer.py <path-to-dump-file> <path-to-index>"
It'll parse the whole dump and file the index files in the 'IndexFiles' directory located in <path-to-index>.
It also creates the document to title mapping file named 'id-title.txt' in the current directory which will be used by the search module later.
(NOTE : As of current code, it pushes the index to disk for every 25000 documents encountered. This can be changed by changing the value of 'Doc_Limit' variable in the code)

## Step 3 : Merging the Indexes and Creating Secondary Indexes

To merge the individual index files and create the secondary index, run the file "IndexMerger.py"
There isn't any need for command line arguments. It takes the index files from 'IndexFiles' directory and populates the 'Final_Index' directory with indexes of given chunk size and creates a secondary index named 'secondaryIndex.txt' in the same folder.
(NOTE : As of the current code, the chunk size is kept 100000. This can be changed by changing the value of 'chunkSize' variable in the code)

## Step 4 : Running the Search Engine

To search for queries, run the file 'Search.py'. It loads the index from 'Final_Index' (both primary and secondary).
It also uses the file 'id-title.txt' (which must be in the working directory) to display titles corresponding to the docIDs.
After it loads up, it gives the user a prompt to enter the query. After that the result of query is displayed. (top K results).
The format of result is:<br/>
	*************
	> Page-Title1
	> Page-Title2
	.
	.
	.
	> Page-Title10
	*************
	<Time Taken for the Query>

To specify normal queries, type them normally. For Field Queries, follow the format:
	f1:<query> f2:<query> ...
	where f1,f2 are fields : t - title, b - body, r - references, i - infobox, c - categories, e - external links
