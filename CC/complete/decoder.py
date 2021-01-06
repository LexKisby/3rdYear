# decoder file

import os
import sys

import zipfile as zp 
import lzma 
import bz2file

f = sys.argv[1]
f = f[:-3]
inputf = f + ".lz"
decodedf = f + "-decoded.tex"
tempf = f + ".txt"

with zp.ZipFile(inputf,"r") as zip_ref:
    zip_ref.extract(tempf)

#get dictionary
dictionary = {}

def preplist(name):
    f = open(name, "r")
    fs = f.read()
    fs = fs.replace(" ", "")
    fs = fs.split("\n")
    return fs

wordlist = preplist("words.txt")
englishlist = preplist("english.txt")
wordlist.extend(englishlist)
wordlist = sorted(wordlist, key=len, reverse=True)
counter = 1

def add_to_dictionary(d, ws, c):
    for w in ws:
        if w in d:
            print("repeated: " + w)
            continue
        d[w] = c
        d[c] = w
        c += 1
    return d, c

dictionary, counter = add_to_dictionary(dictionary, wordlist, counter)

def decode(string, dictionary):
    #assuming tex file has to have \begin{document}
    if string.count('\\begin{document}') > 0:
        return string
    else:
        sign = string[0]
        split = list(string)
        split[0] = ""
        index = 1
        while index < len(split):
            char = split[index]
            if char == sign:
                split[index] = ''
                nextchar = split[index + 1]
                insert = dictionary[ord(nextchar)]
                split[index + 1] = insert
                index += 2
            else:
                index += 1
        string = "".join(split)
        return string


#read in temp file
tempfile = open(tempf, "r") 
string = tempfile.read()

string = decode(string, dictionary)

final = open(decodedf, "w")
final.write(string)
final.close()