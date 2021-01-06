dictionary = {}

x = list(range(0, 128))
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


counter = 0

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
i = 0
for word in dictionary:
    if type(word) == type(""):
        print(word, i)
        i += 1


