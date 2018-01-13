# FRES-Score-Calculation
Python program to calculate the FRES score of a book using NLTK

Following are the libraries/packages that need to be installed in order to successfully run this program:
a)	Gutenberg
b)	urllib
c)	BeautifulSoup
d)	Matplotlib

You can read about Flesch reading-ease test here: https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests

The program has an Agent that takes a long text sequence and returns the Flesch Reading Ease Score.
The Environment repeatedly sends texts to the Agent and receives FRES back. Environment reads books from the Project Gutenberg website using the Gutenberg package and reports for each book: the author, book title, FRES and corresponding School level.
