# encoder file

import os
import sys
import zipfile as zp
#installed as lzma## where ## is the python version
import lzma
import bz2file

f = sys.argv[1]
f = f[:-4] ##assuming given tex file
inf = f + ".tex"
encodedf =  f + ".lz"
tempf = f + ".txt"

#step 1 assemble dictionary
dictionary = {}


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
            i = indices[-1] + 1
        indices.append(string[i:].find(c) + i)
    return indices

def replace(string, word, replacement):
    #need to check that char before is not our signcode char
    SignIndices = IndicesOf(replacement[0], string)
    wordIndices = IndicesOf(word, string)
    temp = list(string)
    flag = False
    for i in range(len(wordIndices)):
        
        if (temp[wordIndices[i] - 1] == replacement[0][0]) and wordIndices[i] != 0:
            print("not replacing")
            continue
        else:
            flag = True
            #print("replacing:  " + word + " with  " + replacement)
            temp[wordIndices[i]] = replacement[0] + replacement[0] + replacement[0] + temp[wordIndices[i]]
            #if word == '\\usepackage':
                #print(wordIndices)
                #print(temp)
    output = "".join(temp)
    if flag: 
        #print(word)
        #print("\n" + output)
        output = output.replace(replacement[0] + replacement[0] + replacement[0] + word, replacement)
        #print("sorts to :")
        #print("\n" + output)
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
#print("\n\n" + out)

tempfile = open(tempf, "w")
tempfile.write(chr(signCode) + out)
tempfile.close()


#compare zippers with intermediate step
with zp.ZipFile('lzma.lz', 'w', zp.ZIP_LZMA) as myzip:
    myzip.write(tempf)
    if myzip.testzip() is not None:
        print("failed")
with zp.ZipFile('deflate.lz', 'w', zp.ZIP_DEFLATED, compresslevel=9) as myzip2:
    myzip2.write(tempf)
with zp.ZipFile("normal.lz", "w", zp.ZIP_BZIP2, compresslevel=9) as myzip3:
    myzip3.write(tempf)
#compare without
with zp.ZipFile('lzma2.lz', 'w', zp.ZIP_LZMA) as myzip:
    myzip.write(inf)
    if myzip.testzip() is not None:
        print("failed")
with zp.ZipFile('deflate2.lz', 'w', zp.ZIP_DEFLATED, compresslevel=9) as myzip2:
    myzip2.write(inf)
with zp.ZipFile("normal2.lz", "w", zp.ZIP_BZIP2, compresslevel=9) as myzip3:
    myzip3.write(inf)


#compare sizes
size = {
tempf: os.path.getsize(tempf),
'lzma.lz':os.path.getsize('lzma.lz'),
'deflate.lz':os.path.getsize('deflate.lz'),
'normal.lz':os.path.getsize('normal.lz'),
'lzma2.lz':os.path.getsize('lzma2.lz'),
'deflate2.lz':os.path.getsize('deflate2.lz'),
'normal2.lz':os.path.getsize('normal2.lz')
}
size = sorted(size.items(), key=lambda item: item[1])
print(size)
os.remove(size[1][0])
os.remove(size[2][0])
os.remove(size[3][0])
os.remove(size[4][0])
os.remove(size[5][0])
os.remove(size[6][0])

output = open(encodedf, "wb")
final = open(size[0][0], "rb")
output.write(final.read())
output.close()
final.close()
os.remove(size[0][0])


