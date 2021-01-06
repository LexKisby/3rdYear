#takes script then assembles into common words

script = """The purpose of the exercise is to produce a program to losslessly encode a tex file. The only way to have better performance than pre-existing techniques is to leverage the specificity of the task to tex files. 
\question*{Idea 1}
Fundamentally, if I cannot beat the performance of a library that can implement a basic zip compression function, like that of the Zipfile library, then that will be the default implementation. The library can utilise deflate, bzip2 and LZMA compression methods, and given there is no time aspect to the task, the one with typically the best compression ratios would be used.\\

\question*{Idea 2}
That said, this is not a very interesting approach to the problem. Given the nature of a tex file, there are some assumptions that can be made. The majority of such a file should be in sensible english, and not a stream of random letters. Such a format lends itself well to contextual compression, and PPM is a suitable candidate to effectively compress text data. At present I have found one such library capable of ppm but this relies on a C backend and a C compiler to be installed on the machine so this goes a bit beyond the requirements of the task. This leaves the only way to utilise PPM as a personal implementation.

\question*{Idea 3}
Beyond the basic connection of sensible english to a contextual compression algorithm, other details of a tex file include the nature of the layout, with regularly occurring commands like \verb|\section| and \verb|\item|. Moreover, we can conclude things like every \verb|\begin| command will have a corresponding \verb|\end| command. We would also expect for every open bracket, parenthesis or brace to have a corresponding closing bracket, parenthesis or brace, but that is not always the case, as shown here). Although such a circumstance is probably very rare, and checking for such an event is very easy, I feel it would be easy to get carried away, and be misguided from more useful features. A simple solution for the first point, however, regarding \verb|\begin| and \verb|\end| statements is having a heap that stores the associated parameter like \texttt{enumerate} or \texttt{document} and then popping that parameter again whenever the \verb|\end| codeword is read.

\question*{Idea 4}
Perhaps in the wrong order, but the next point again refers to the prior discussed commands in latex, and given the more regular use of some commands over others, and given the limited number of commands that would exist in a document. An entirely uneducated guess on my behalf would be that a typical document uses less than 30 unique commands, at present it is 14 in this document. Converting these commands to a huffman tree would mean in this case that those 30 commands are expressed in at most 6 bits, converting possibly 5 or 6 bytes into 0.75 bytes, loosely a 6x compression ratio. That said, the tree itself would need to be stored, unless a pre defined dictionary is used based on the typical use case, and this is kept with the encoder and decoder instead. Searching online for the most commonly used 256 commands would produce a dictionary with codes at most around 8 bits long, but given how unlikely a tex file spanning more than 256 commands is, it may be more apt to have a set dictionary for the most prevalent 64 commands, and then append a custom dictionary as required for repeated code in a tex file that is not included in the pre set dictionary, as I expect if someone was to use a rarer command, they may use it repeatedly, particularly if the user is proficient with latex and implements custom commands. Such a dynamic dictionary would have to be appended to the compressed file, costing storage. Then the rest of the encoding that does not appear in the dictionary is encoded according to some other method.

\question*{Idea 5}
Having loosely fiddled with the pre-existing compression programs that exist to determine a sort of baseline for performance, the LZMA solution used by zipfile is the best compressor I have so far tested, compared to the python library solutions for deflate and bzip2, as well as the 7zip implementation of PPMd. For a 200KB dummy tex file, they all completed essentially instantly, which is nice even if not relevant. LZMA produced an incredibly compressed file, on an order of 60x compression ratio, though the dummy file was an approx. 30KB file with repeated contents. Regardless, with plenty of repetition the LZMA algorithm performs excellently. A second test with a more realistic dummy file led to a different conclusion, with bzip2 taking the crown, although the dummy passage was generated with zero repetition, which LZMA may be able to capitalise better on. Either way, LZMA performed strongly, and outperformed the contextual PPMd decisively. Moreover, given the speed of the"
The zebra finch (Poephila guttata) is a sexually dimorphic, social estrildid native to the grasslands of Australia. They are opportunistic, year-round breeders which nest in colonies of variable size. Zebra finches form permanent pair bonds and both sexes share the responsibilities of nest building, incubation and rearing of young (Walter, 1973). Morris (1954), however, reported that although both sexes pick up and nibble on fragments of material, males collect most of the nesting material.

The scientific name of the research organism must be stated the first time the organism is mentioned in any of the sections. Thereafter, within each section, either the common name or the abbreviated scientific name can be used.

Studies on the effects of colored plastic leg bands on pair formation show that male zebra finches spend more time sitting next to females wearing black or pink leg bands than females wearing light blue leg bands. The same studies indicate that females spend more time sitting next to males wearing red leg bands than males wearing light green bands. In both male and female, orange leg bands (which are similar to natural leg color) proved to be of intermediate preference (Burley, 1981 and 1982).

The first paragraphs of the introduction provide background information from preliminary or other published studies. This is used to develop the hypothesis or purpose of the experiment and to provide the rationale or reason for conducting the experiment.

The purpose of this study was to test whether or not this preference for certain colors of leg bands generalizes to preference for certain colors of nesting material. It was hypothesized that zebra finches would collect more red or black material than light green, with collection of orange being intermediate.

This paragraph specifically states the purpose of the experiment. It also states the hypothesis the author developed based on background reading and observations.


METHODS

The zebra finches used in this study were in three colonies in the lab of Dr. J.R. Baylis at the University of Wisconsin, Madison. Each colony contained between thirty and forty individual birds of both sexes, a variety of ages and several plumage types. All animals wore colored leg bands for individual identification and all had been exposed to grass, green embroidery floss and white dog fur as nesting material previous to this study. The colonies were housed in separate rooms, each approximately 17m3 and each contained eight artificial nest boxes. All behavioral observations were made from outside the colony rooms through one-way mirrors.

The methods begin by indicating where the research organisms were obtained.

Specific examples about the organisms are included, e.g. number of organisms, sexes, ages, and morphology.

Previous exposure to colored nest material is described. How organisms were housed, including specific dimensions of cages, etc. and the physical conditions of light and temperature, is also included.

Red, black, orange and light green DMC four-ply cotton embroidery floss was cut into 2.5 cm pieces. During each trial, twenty-five pieces of each color were separated and spread out over the floor of the colony. After the birds had been exposed to the material for a total of two hours, any remaining strands of floss on the floor were collected. The number of strands of each color was counted. It was assumed all other strands (not on the floor) had been used in nest construction. Data from the three colonies were pooled and an X2 goodness-of-fit test was used to determine whether the number of strands of each color used in nest construction different from an expected ratio of 1:1:1:1 (which would indicate no preference).

The types of test materials used are described in detail, as are the methods.

Description of methods includes assumptions made and type of analysis to be performed on the data.

 

RESULTS

More green material was removed by the finches than red, more red than black and more black than orange. The ratio between material of different colors used in nest construction differed significantly from the expected 1:1:1:1 (X2=63.44, df=3, p<.005). When colors were compared in pairs, the difference between values for green and red were not significantly different (X2=117, df=1, p>.5). However, the values for black and orange were significantly different (X2=36.38, df=1, p<.005).

 

The author interprets the data for the reader in text form. The author does not expect the reader to interpret the results from a table of data, but instead provides his/her interpretation for the reader.

DISCUSSION

The discussion provides an explanation of what the results mean relative to the original purpose and/or hypothesis stated in the introduction.

The results from these experiments suggest that zebra finches do in fact have color preferences with regard to nesting material. Contrary to the predictions made by generalizing Burley’s studies (1981, 1982), however, the zebra finches used in this study preferred green, red or black nesting material to orange. These results are similar to those of Collias and Collias (1981) who showed that weaver birds preferred green nesting material.

 

Results are compared to those from other studies. Plausible reasons/hypotheses are proposed to explain the results.

It is possible that zebra finches prefer green material to red, black and orange because green is more similar to the color of the grasses commonly used as nesting material in their natural environment. This interpretation, however, does not explain the preference for red and black materials over orange.

Limitations to the proposed hypotheses are also provided.

Alternatively, it is possible that the strong preference shown for green material may be a result of imprinting on the color of the nests they grew up in. It has been shown, for example, that parental plumage color has a strong effect on mate selection in male (but not female) zebra finches (Walter, 1973). All of the birds used in this study have been exposed to grass, green embroidery floss and white dog fur in nests. If as suggested by Morris (1954) males collect most of the nesting material, imprinting could have a strong effect on the numbers of colored strands collected in this study. This hypothesis could be tested by raising zebra finches in nests containing different colors of nesting materials and testing them in adulthood for preference in nest material color. When setting up this experiment, it was noted that zebra finches seem particularly apprehensive about new objects placed in the colony. It is also possible, therefore, that the preference for green nest material was simply due to its familiarity.

Alternative hypotheses are also provided, and evidence from literature is given in support of the alternate hypothesis.

 

Future studies are proposed to help further knowledge in the area.

REFERENCES

 
Burley, N. 1981 Sex-ratio manipulation and selection for attractiveness. Science 211: 721-722.

Burley, N. 1982 Influence of colour-banding on the nonspecific preference of zebra finches. Anim. Behav. 30: 444-445.

(Additional references deleted for brevity.)

All references cited in the body of the paper are listed alphabetically by last name of the first author. Only references cited in the body of the paper are listed here.

See the Introductory Biology 151-152 manual for complete information on how to reference supporting literature both in the body of the paper and in the reference list.
"""
script = script.lower()
script = script.replace("\n", " ")
script = script.replace(".", "")

dic = {}
words = script.split(" ")

for word in words:
    if word in dic:
        continue
    dic[word] = script.count(word)

for k,v in sorted(dic.items(), key=lambda p:p[1], reverse=True):
    if (len(k)) == 3:
        print(k, v)

print(script.count("\\"))