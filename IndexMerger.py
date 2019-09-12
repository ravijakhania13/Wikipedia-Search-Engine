import os,sys
import timeit
import glob
from collections import defaultdict
from heapq import heapify, heappush, heappop

folderToStore = "/home/ravi/IIIT/SEM3/IRE/Mini_Project/Phase2/2018201018/Final_Index/"
indexFileCount = 1
chunkSize = 100000

indexFiles = glob.glob("./IndexFiles/[0-9]*.txt")
indexFiles.sort()
currentRowOfFile = dict()
completedFiles = [0] * len(indexFiles)
heap_list = list()
word_map = dict()
filePointers = dict()
LineCount = 0
invertedIndex = defaultdict()

start = timeit.default_timer()


for i in range(len(indexFiles)):
	try:
		filePointers[i] = open(indexFiles[i],"r")
	except:
		print ("Could Open Files: ")

	currentRowOfFile[i] = filePointers[i].readline().strip().split("=")

	while currentRowOfFile[i][0] and currentRowOfFile[i][0] in heap_list:
		word_map[currentRowOfFile[i][0]] += "," + currentRowOfFile[i][1]
		currentRowOfFile[i] = filePointers[i].readline().strip().split("=")

	if currentRowOfFile[i][0]:
		heappush(heap_list,currentRowOfFile[i][0])
		word_map[currentRowOfFile[i][0]] = currentRowOfFile[i][1]
	# else:
	# 	indexFiles.remove(indexFiles[i])
	# 	filePointers.remove(filePointers[i])

fileName = folderToStore + "/index" + str(indexFileCount) + ".txt"
fp = open(fileName,"w")

fileName_secondary_index = folderToStore + "/secondaryIndex.txt"
fps = open(fileName_secondary_index,"w")

while len(heap_list) > 0:
	LineCount += 1
	word = heappop(heap_list)
	toWrite = word + "=" + word_map[word] + "\n"
	fp.write(toWrite)			
	word_map.pop(word)

	if(LineCount == 1):
		toWrite = word + " " + fileName + "\n"
		fps.write(toWrite)

	for i in range(len(indexFiles)):
		if currentRowOfFile[i][0] == word:

			currentRowOfFile[i] = filePointers[i].readline().strip().split("=")

			while currentRowOfFile[i][0] and currentRowOfFile[i][0] in heap_list:
				word_map[currentRowOfFile[i][0]] += "," + currentRowOfFile[i][1]
				currentRowOfFile[i] = filePointers[i].readline().strip().split("=")

			if currentRowOfFile[i][0]:
				heappush(heap_list,currentRowOfFile[i][0])
				word_map[currentRowOfFile[i][0]] = currentRowOfFile[i][1]
			# else:
			# 	indexFiles.remove(indexFiles[i])
			# 	filePointers.remove(filePointers[i])

	if LineCount == chunkSize:
		LineCount = 0
		indexFileCount += 1
		fp.close()
		fileName = folderToStore + "index" + str(indexFileCount) + ".txt"
		fp = open(fileName,"w")

stop = timeit.default_timer()

print ("Time for Merging:",stop-start," seconds.")
mins = float(stop-start)/float(60)
print ("Time for Merging:",mins," Minutes.")
hrs = float(mins)/float(60)
print ("Time for Merging:",hrs," Hours.")
print ("Check the External File(s) Now!")
