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

stop_words = set(stopwords.words('english')) 
InvertedIndex = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
Stem_Words = {}
Inverted_Index_File_No = 1
Doc_Limit = 25000
f2 = ""
ps = PorterStemmer()

def remove_non_ascii(words):
    new_words = []
    for word in words:
        new_word = word.strip().encode('utf-8')
        new_words.append(new_word)
    return new_words

def to_lowercase(data):
    data = data.lower()
    return data

def remove_urls(data):
    Reg_Exp = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',re.DOTALL)
    data = Reg_Exp.sub('',data)
    return data

def remove_css(data):
    Reg_Exp = re.compile(r'{\|(.*?)\|}',re.DOTALL)
    data = Reg_Exp.sub('',data)
    return data

def remove_file(data):
    Reg_Exp = re.compile(r'\[\[file:(.*?)\]\]',re.DOTALL)
    data = Reg_Exp.sub('',data)
    return data

def remove_cite(data):
    Reg_Exp = re.compile(r'{{v?cite(.*?)}}',re.DOTALL)
    data = Reg_Exp.sub('',data)
    return data

def remove_punctuation(data):
    Reg_Exp = re.compile(r'[.,;_()"/\']',re.DOTALL)
    data = Reg_Exp.sub('',data)
    return data

def remove_junk(data):
    Reg_Exp = re.compile(r"[~`!@#$%\-\^=\*+{\[}\]\|\\<>\?]",re.DOTALL)
    data = Reg_Exp.sub('',data)
    return data

def remove_tags(data):
    Reg_Exp = re.compile(r'<(.*?)>',re.DOTALL)
    data = Reg_Exp.sub('',data)
    return data

def Fetch_Categories(data):
    data = re.findall(r'\[\[category:(.*?)\]\]',data,flags=re.MULTILINE)
    return data

def Fetch_Infobox(data):
    data = re.findall(r'{{infobox(.*?)}}',data,flags=re.DOTALL)
    return data

def Fetch_References(data):
    data = re.findall(r'== ?references ?==(.*?)==',data,flags=re.DOTALL)
    return data

def Fetch_External_Links(data):
    copy_data = []
    Index = 0
    try:
        Index = text.index('==external links==')
        Index += 20
    except:
        pass
    
    if(Index):
        copy_data = data[Index:]
        copy_data = re.findall(r'\*\[(.*?)\]',copy_data,flags=re.MULTILINE)
    return copy_data,Index

def remove_infobox(data):
    Reg_Exp = re.compile(r'{{infobox(.*?)}}',re.DOTALL)
    data = Reg_Exp.sub('',data)
    return data

def remove_references(data):
    Reg_Exp = re.compile(r'== ?references ?==(.*?)==',re.DOTALL)
    data = Reg_Exp.sub('',data)
    return data

def remove_curly_stmt(data):
    Reg_Exp = re.compile(r'{{(.*?)}}',re.DOTALL)
    data = Reg_Exp.sub('',data)
    return data

def remove_stopwords(words):
    new_words = []
    for word in words:
        if word not in stopwords.words('english'):
            new_words.append(word)
    return new_words

def stem_words(words):
    PS = PorterStemmer()
    stems = []
    for word in words:
        stem = PS.stem(word)
        stems.append(stem)
    return stems

def normalize(data):
    data = to_lowercase(data)
    data = remove_urls(data)
    data = remove_css(data)
    data = remove_file(data)
    data = remove_cite(data)
    data = remove_tags(data)
    return data

def Insert_To_Inverted_Index(data, doc_id, tag):
    for word in data:
        word = re.sub(r'[^\x00-\x7F]+','', word)
        if len(word) > 2 and len(word) < 200:
            if(word in InvertedIndex):
                if(doc_id in InvertedIndex[word]):
                    if(tag in InvertedIndex[word][doc_id]):
                        InvertedIndex[word][doc_id][tag] += 1
                    else:
                        InvertedIndex[word][doc_id][tag] = 1
                else:
                    InvertedIndex[word][doc_id] = {tag:1}
            else:
                InvertedIndex[word] = dict({doc_id:{tag:1}})

def tokenize(data): 
    global ps
    tokens = data.split()
    words = []
    # remove all tokens that are not alphanumeric
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

def Data_Processing(data, docID, tag):
    global Inverted_Index_File_No
    data = data.lower()

    # Remove URL
    Reg_Exp = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',re.DOTALL)
    data = Reg_Exp.sub('',data)

    # Remove CSS
    Reg_Exp = re.compile(r'{\|(.*?)\|}',re.DOTALL)
    data = Reg_Exp.sub('',data)

    # Remove [[file
    Reg_Exp = re.compile(r'\[\[file:(.*?)\]\]',re.DOTALL)
    data = Reg_Exp.sub('',data)

    # Remove Cite
    Reg_Exp = re.compile(r'{{v?cite(.*?)}}',re.DOTALL)
    data = Reg_Exp.sub('',data)

    # Remove Tage
    Reg_Exp = re.compile(r'<(.*?)>',re.DOTALL)
    data = Reg_Exp.sub('',data)


    if(tag == 'title'):
        # Remove junk
        Reg_Exp = re.compile(r"[~`!@#$%\-\^=\*+{\[}\]\|\\<>\?]",re.DOTALL)
        data = Reg_Exp.sub('',data)

        # Remove punctuation
        Reg_Exp = re.compile(r'[.,;_()"/\']',re.DOTALL)
        data = Reg_Exp.sub('',data)
        data = tokenize(data)
        
        Insert_To_Inverted_Index(data,docID,"t")
    elif(tag == 'text'):
        # Fetch categories
        categories = []
        categories = re.findall(r'\[\[category:(.*?)\]\]',data,flags=re.MULTILINE)

        # Fetch infobox
        infobox = []
        infobox = re.findall(r'{{infobox(.*?)}}',data,flags=re.DOTALL)
        
        # Fetch references
        references = []
        references = re.findall(r'== ?references ?==(.*?)==',data,flags=re.DOTALL)
        
        # Fetch external_links
        external_links = []
        Index = 0
        try:
            Index = text.index('==external links==')
            Index += 20
        except:
            pass
        
        if(Index):
            external_links = data[Index:]
            external_links = re.findall(r'\*\[(.*?)\]',external_links,flags=re.MULTILINE)

        if(Index):
            data = data[0:Index - 20]

        Reg_Exp = re.compile(r'{{infobox(.*?)}}',re.DOTALL)
        data = Reg_Exp.sub('',data)

        Reg_Exp = re.compile(r'== ?references ?==(.*?)==',re.DOTALL)
        data = Reg_Exp.sub('',data)

        Reg_Exp = re.compile(r'{{(.*?)}}',re.DOTALL)
        data = Reg_Exp.sub('',data)

        Reg_Exp = re.compile(r'[.,;_()"/\']',re.DOTALL)
        data = Reg_Exp.sub('',data)

        Reg_Exp = re.compile(r"[~`!@#$%\-\^=\*+{\[}\]\|\\<>\?]",re.DOTALL)
        data = Reg_Exp.sub('',data)

        #Tokenizing, stemming, removing stop words and non ascii chaarters

        data = tokenize(data)
        Insert_To_Inverted_Index(data,docID,"b")

        categories = ' '.join(categories)
        categories = remove_punctuation(categories)
        categories = remove_junk(categories)
        categories = tokenize(categories)
        Insert_To_Inverted_Index(categories,docID,"c")

        references = ' '.join(references)
        references = remove_punctuation(references)
        references = remove_junk(references)
        references = tokenize(references)
        Insert_To_Inverted_Index(references,docID,"r")

        external_links = ' '.join(external_links)
        external_links = remove_punctuation(external_links)
        external_links = remove_junk(external_links)
        external_links = tokenize(external_links)
        Insert_To_Inverted_Index(external_links,docID,"e")

        for infoList in infobox:
            infoboxList = []
            infoboxList = re.findall(r'=(.*?)\|',infoList,re.DOTALL)
            infoboxList = ' '.join(infoboxList)
            infoboxList = remove_punctuation(infoboxList)
            infoboxList = remove_junk(infoboxList)
            infoboxList = tokenize(infoboxList)
            Insert_To_Inverted_Index(infoboxList,docID,"i")
        
        if docID % Doc_Limit == 0:
            f = open(indexpath+'/'+str(Inverted_Index_File_No)+'.txt',"w")
            for key,val in sorted(InvertedIndex.items()):
                key += "="
                for k,v in sorted(val.items()):
                    key += str(k) + ":"
                    for k1,v1 in v.items():
                        key = key + str(k1) + str(v1) + "#"
                    key = key[:-1]+","
                key = key[:-1]+"\n"
                f.write(key)
            f.close()
            InvertedIndex.clear()
            Stem_Words.clear()
            Inverted_Index_File_No += 1


class DataHandler( xml.sax.ContentHandler ):
    def __init__(self):
        self.DocId = 0
        self.CurrentData = ""
        self.title = ""
        self.id = ""
        self.text = ""
        self.id_flag = False

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "page":
            self.id_flag = True
            self.DocId += 1

    # Call when an elements ends
    def endElement(self, tag):
        global f2
        if self.CurrentData == "title":
            f2.write(str(self.DocId)+"=="+self.title+"\n")
            Data_Processing(self.title,self.DocId,"title")
        elif self.CurrentData == "id" and self.id_flag == True:
            self.id_flag = False
        elif self.CurrentData == "text":
            Data_Processing(self.text,self.DocId,"text")

        self.CurrentData = ""
        self.id = ""
        self.text = ""
        self.title = ""

    def characters(self, content):
        if self.CurrentData == "title":
            self.title = self.title + content
        elif self.CurrentData == "id" and self.id_flag == True:
            self.id = self.id + content
        elif self.CurrentData == "text":
            self.text = self.text + content

if ( __name__ == "__main__"):
    # global Inverted_Index_File_No
    dumpfile = sys.argv[1]
    indexpath = sys.argv[2]
    f2 = open('./id-title.txt',"w")
    
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # override the default ContextHandler
    start_time = time.time()
    Handler = DataHandler()
    parser.setContentHandler( Handler )

    parser.parse(dumpfile)

    f = open(indexpath+'/'+str(Inverted_Index_File_No)+'.txt',"w")
    for key,val in sorted(InvertedIndex.items()):
        key += "="
        for k,v in sorted(val.items()):
            key += str(k) + ":"
            for k1,v1 in v.items():
                key = key + str(k1) + str(v1) + "#"
            key = key[:-1]+","
        key = key[:-1]+"\n"
        f.write(key)

    f.close()
    f2.close()
    Inverted_Index_File_No += 1
    end_time = time.time()
    print(" time taken : ",end_time-start_time)