Diz (Dizzy) is a simple PPMC compressor. I figured the best way to learn about
PPM was to make a working program using it! As such, the code is written
primarily for simplicity and ease of change, so new ideas can be quickly tried.
Python was chosen because it supports these goals. Compressing text the length
of a novel takes a few seconds, which is good enough.


Diz is normally tested on frank.txt from Project Gutenberg at
http://www.gutenberg.org/ebooks/84. I like this because it's the first book
about future technology (SciFi) and because it represents a complete story.

Diz has also been tested on enwik8.txt from the Large Text Compression Benchmark
at http://mattmahoney.net/dc/textdata.html. Diz's performance is better on this
because it's longer length results in more accurate predictors. There is various
content inside mixed together though, and that can't help.

Diz is usually run using pypy, instead of Python, because it improves the speed
at least 3x. A common usage is

'pypy diz.py -t frank.txt' 

which produces frank.diz and 'Copy of frank.txt', and verifies the contents by
matching CRCs. Python 2.7 can be used instead. 

To run enwik8.txt try

'pypy diz.py -t -p enwik8.txt' 

which produces enwik8.diz and 'Copy of enwik8.txt', and verifies the contents by
matching CRCs. The '-p' displays progress by percent, useful for the long run.
It takes about 15 minutes on my old laptop to compress and another 15 minutes to
decompress.






As mentioned the code implements PPMC. Using the number of different symbols
divided by the number of symbols seen to estimate the escape seems overly
simple. There exist better schemes but I haven't found clear enough descriptions
for me to implement them. I wish there was something inbetween a one line of
code scheme and a several page scheme.

From what I can tell, there are two main challenges of the PPM method. The first
is figuring out which predictor to use. The simple method of PPMC uses a fixed
order depth, like four. But that's a crude average, which means it's rarely the
best one. A better system would keep more depth, but only use a predictor at a
depth that was likely to predict the outcome in as little information as
possible. Or even better, a couple of predictors could be used, and their
predictions blended/interpolated.

The second main issue is figuring out how to reduce the cost of escapes. This
seems to be the direction of most of the more advanced PPM schemes.

Ultimately it seems like PPM eventually starves for more information to make
better predictors. I say this because raising the order and charging nothing for
escapes quickly stops being useful. There simply aren't enough prior examples to
make good accurate predictions in a novel's length of text. Because the
predictors in PPM are exact, it takes too long to accumulate all the variations
need to make good predictions. It seems the future of PPM would be to take
advantage of 'related' predictors when the existing one doesn't seem that
helpful.





Trivia: I started this project initially to learn about arithmetic coders. I
liked them until I had to deal with underflow. The tracking of underflow digits
and reporting them just seems so ugly. I was hoping to find a way to make
only the encoder ugly to track them, and to just return the number (the ugliness
is that the encoder can't determine the number because the lower and upper
numbers straddle a number boudary, but eventually it does figure the number out,
and I wish that final number could just be passed to the decoder instead of
mirroring all of the ugliness in the decoder as well). So at this point I never
want to write another arithmetic coder again, or to somehow to be beaten into
thinking they're obvious and beautiful!

