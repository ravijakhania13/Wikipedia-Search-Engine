import xml.sax
from nltk.corpus import stopwords 
from nltk import word_tokenize
import re
from nltk.stem import PorterStemmer
import timeit
import os
import sys
from collections import defaultdict
import re, string, unicodedata
import time
from bisect import bisect
from operator import itemgetter
from math import log10
from heapq import heapify, heappush, heappop

stop_words = set(stopwords.words('english')) 
id_to_title_mapping = dict()
Secondary_Index_Start_Words = list()
Stem_Words = {}
Total_Documents = 0
ps = PorterStemmer()

def tokenize(data): 
    global ps
    tokens = data.split()
    words = []
    for word in tokens:
        word = re.sub(r'[^\x00-\x7F]+','', word)
        if len(word) < 200 and word.isalnum() and word not in stop_words:
            if word in Stem_Words.keys():
                temp_word = Stem_Words[word]
            else:
                temp_word = ps.stem(word)
                Stem_Words[word] = temp_word
            if len(temp_word) > 2:
                words.append(temp_word)
    return words

def Normalize(query):
    query = query.lower()
    Reg_Exp = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',re.DOTALL)
    query = Reg_Exp.sub('',query)

    Reg_Exp = re.compile(r'{\|(.*?)\|}',re.DOTALL)
    query = Reg_Exp.sub('',query)

    Reg_Exp = re.compile(r'\[\[file:(.*?)\]\]',re.DOTALL)
    query = Reg_Exp.sub('',query)

    Reg_Exp = re.compile(r'{{v?cite(.*?)}}',re.DOTALL)
    query = Reg_Exp.sub('',query)

    Reg_Exp = re.compile(r'<(.*?)>',re.DOTALL)
    query = Reg_Exp.sub('',query)

    Reg_Exp = re.compile(r"[~`!@#$%\-\^=\*+{\[}\]\|\\<>\?]",re.DOTALL)
    query = Reg_Exp.sub('',query)

    Reg_Exp = re.compile(r'[.,;_()"/\']',re.DOTALL)
    query = Reg_Exp.sub('',query)

    query = tokenize(query)
    return query

def Normal_Query(query):
    Primary_Index_To_Words = dict(list())
    Word_To_Posting_List = dict()
    ID_Weight = dict()
    query = Normalize(query)

    for word in query:
        location = bisect(Secondary_Index_Start_Words,word)
        File_Path = "/home/ravi/IIIT/SEM3/IRE/Mini_Project/Phase2/2018201018/Final_Index/index" + str(location) + ".txt"

        if(File_Path in Primary_Index_To_Words):
            if(word not in Primary_Index_To_Words[File_Path]):
                Primary_Index_To_Words[File_Path].append(word)
        else:
            Primary_Index_To_Words[File_Path] = [word]

    for File_Path, Words in Primary_Index_To_Words.items():
        f = open(File_Path,"r")
        for line in f:
            line = line.rstrip('\n')
            Word, Posting_List = line.split('=',1)
            if (Word in Words):
                Word_To_Posting_List[Word] = Posting_List
        f.close()

        for Word in Words:
            if Word in Word_To_Posting_List:
                Posting_List = Word_To_Posting_List[Word].split(',')
                IDF = log10(Total_Documents/len(Posting_List))

                for Doc in Posting_List:
                    Doc_Id, Entries = Doc.split(":")
                    Tag_Freq = Entries.split("#")
                    Word_Specific_Weighted_Freq = 0
                    for Tag_Freq in Tag_Freq:
                        Tag = Tag_Freq[0]
                        Freq = int(Tag_Freq[1:])
                        if Tag == "t":
                            Word_Specific_Weighted_Freq += Freq*1000
                        elif Tag == "i" or Tag == "c" or Tag == "r" or Tag == "e":
                            Word_Specific_Weighted_Freq += Freq*50
                        elif Tag == "b":
                            Word_Specific_Weighted_Freq += Freq
                    
                    if Doc_Id in ID_Weight:
                        ID_Weight[Doc_Id] += float(log10(1+Word_Specific_Weighted_Freq))*float(IDF)
                    else:
                        ID_Weight[Doc_Id] = float(log10(1+Word_Specific_Weighted_Freq))*float(IDF)

        Word_To_Posting_List.clear()
    
    Primary_Index_To_Words.clear()
    ID_Weight = sorted(ID_Weight.items(), key=lambda x: x[1], reverse=True)

    if(len(ID_Weight) > 10):
        ID_Weight = ID_Weight[0:10]

    for Doc in ID_Weight:
        print(">  " + id_to_title_mapping[Doc[0]])

def Tag_Query(query):
    Primary_Index_To_Words = dict(list())
    Word_To_Posting_List = dict()
    Word_To_Tag = dict(list())
    ID_Weight = dict()

    query = query.split(" ")
    for Tag_word in query:
        Tag, word = Tag_word.split(":")
        words = Normalize(word)
        if Tag == "title":
            Tag = "t"
        elif Tag == "body":
            Tag = "b"
        elif Tag == "infobox":
            Tag = "i"
        elif Tag == "category":
            Tag = "c"
        elif Tag == "ref":
            Tag = "r"
        else:
            Tag = "e"

        for word in words:
            if(word in Word_To_Tag):
                Word_To_Tag[word].append(Tag)
            else:
                Word_To_Tag[word] = [Tag]

            location = bisect(Secondary_Index_Start_Words,word)

            File_Path = "/home/ravi/IIIT/SEM3/IRE/Mini_Project/Phase2/2018201018/Final_Index/index" + str(location) + ".txt"
        
            if(File_Path in Primary_Index_To_Words):
                if(word not in Primary_Index_To_Words[File_Path]):
                    Primary_Index_To_Words[File_Path].append(word)
            else:
                Primary_Index_To_Words[File_Path] = [word]
    
    for File_Path, Words in Primary_Index_To_Words.items():
        f = open(File_Path,"r")
        for line in f:
            line = line.rstrip('\n')
            Word, Posting_List = line.split('=',1)
            if (Word in Words):
                Word_To_Posting_List[Word] = Posting_List
        f.close()


        for Word in Words:
            if Word in Word_To_Posting_List:
                Posting_List = Word_To_Posting_List[Word].split(',')
                IDF = log10(Total_Documents/len(Posting_List))

                for Doc in Posting_List:
                    Doc_Id, Entries = Doc.split(":")
                    Tag_Freq = Entries.split("#")
                    Word_Specific_Weighted_Freq = 0
                    for Tag_Freq in Tag_Freq:
                        Tag = Tag_Freq[0]
                        Freq = int(Tag_Freq[1:])
                        if Tag in Word_To_Tag[Word]:
                            if Tag == "t":
                                Word_Specific_Weighted_Freq += Freq*1000
                            elif Tag == "i" or Tag == "c" or Tag == "r" or Tag == "e":
                                Word_Specific_Weighted_Freq += Freq*50
                            elif Tag == "b":
                                Word_Specific_Weighted_Freq += Freq
                        else:
                            Word_Specific_Weighted_Freq += Freq
                    
                    if Doc_Id in ID_Weight:
                        ID_Weight[Doc_Id] += float(log10(1+Word_Specific_Weighted_Freq))*float(IDF)
                    else:
                        ID_Weight[Doc_Id] = float(log10(1+Word_Specific_Weighted_Freq))*float(IDF)

        Word_To_Posting_List.clear()
    
    Primary_Index_To_Words.clear()
    ID_Weight = sorted(ID_Weight.items(), key=lambda x: x[1], reverse=True)

    if(len(ID_Weight) > 10):
        ID_Weight = ID_Weight[0:10]

    for Doc in ID_Weight:
        print(id_to_title_mapping[Doc[0]])


def main():
    global Total_Documents
    path_to_index = "/home/ravi/IIIT/SEM3/IRE/Mini_Project/Phase2/2018201018/Final_Index"
    print("Storing Id to Title mapping....")
    try:
        f = open("./id-title.txt","r")
        for line in f:
            line = line.rstrip('\n')
            ID, Title = line.split('==',1)
            id_to_title_mapping[ID] = Title
            Total_Documents += 1
        f.close()
    except Exception as e:
        print ("Can not find the Title and Document ID Mapping File.")
        print(e)
        sys.exit(1)
    print("Done")
    print("")
    print("Storing secondary index....")
    try:
        f = open(path_to_index + "/secondaryIndex.txt","r")
        for line in f:
            Secondary_Index_Start_Words.append(line.split(' ')[0])
        f.close()
    except:
        print ("Can not find the Inverted_Index File.")
        sys.exit(1)
    print("Done")
    print("")
    while True:
        query = input("Enter your query: ")
        print("**************************")
        start = timeit.default_timer()
        if ":" not in query:
            try:
                Normal_Query(query)
                stop = timeit.default_timer()
                print("**************************")
                print ("Query Took ",stop-start," seconds.")
            except Exception as e:
                print(e)
                print ("Some Error Occurred! Try Again")
        else:
            try:
                Tag_Query(query)
                stop = timeit.default_timer()
                print("**************************")
                print ("Query Took ",stop-start," seconds.")
            except Exception as e:
                print(e)
                print ("Some Error Occurred! Try Again")
        print("")
if __name__ == '__main__':
    main()
