# encoder file

import os
import sys
import zipfile as zp
import lzma
import bz2file

f = sys.argv[1]
encodedf =  f + ".lz"
tempf = f + ".temp"

#step 1 assemble dictionary
dictionary = {}

x = list(range(1, 128))
for n in range(len(x)):
    x[n] = chr(int(bin(x[n]), 2))

#read in words from english.txt and words.txt
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

#step 2 take in og file
ogf = open(f+".tex", "r")
lines = ogf.read()
ogf.close()

#step 3 check no special symbols.
def getSignCode(string):
    sign = chr(1)
    count = string.count(sign)
    c = 1
    while count > 0:
        c += 1
        count = string.count(chr(c))
    return c
    
signCode = getSignCode(lines)
print("signcode: " + str(signCode) + chr(signCode))

#replace stuff in lines with dictionary swaps
def IndicesOf(c, string):
    count = string.count(c)
    indices = []
    while len(indices) < count:
        i = 0
        if len(indices) != 0:
            i = indices[-1]
        indices.append(string[i:].find(c))
    return indices

def replace(string, word, replacement):
    #need to check that char before is not our signcode char
    SignIndices = IndicesOf(replacement[0], string)
    wordIndices = IndicesOf(word, string)
    temp = list(string)
    for i in range(len(wordIndices)):
        if temp[wordIndices[i] - 1] == replacement[0]:
            print("not replacing")
            continue
        else:
            print("replacing:  " + word + " with  " + replacement)
            temp[wordIndices[i]] = replacement[0] + replacement[0] + replacement[0] + temp[wordIndices[i]]
    output = "".join(temp)
    output = output.replace(replacement[0] + replacement[0] + replacement[0] + word, replacement)
    return output


def Dictionary_replace(dic, string, signCode):
    for word in dic:
        if type(word) == type(""):
            replacement = chr(signCode) + chr(dic[word])
            #print("sc:  " + chr(signCode))
            #print("w:  " + word + " " + chr(dic[word]))
            string = replace(string, word, replacement)
    return string



out = Dictionary_replace(dictionary, lines, signCode)
print(out)

tempf = open(tempf, "w")
tempf.write(chr(signCode) + out)
tempf.close()

#compare zippers
with zp.ZipFile('lzma.lz', 'w', zp.ZIP_LZMA) as myzip:
    myzip.write(tempf)
    if myzip.testzip() is not None:
        print("failed")

with zp.ZipFile('deflate.lz', 'w', zp.ZIP_DEFLATED) as myzip2:
    myzip2.write(tempf)

with zp.ZipFile("normal.lz", "w", zp.ZIP_BZIP2) as myzip3:
    myzip3.write(tempf)

#compare sizes
lzmaSize = os.path.getSize('lzma.lz')
deflateSize = os.path.getSize('deflate.lz')
normalSize = os.path.getSize('normal.lz')
