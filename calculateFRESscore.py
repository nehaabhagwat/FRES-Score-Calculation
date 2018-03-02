# baseline3.py
# Author: Neha Bhagwat

from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from gutenberg.query import get_etexts, get_metadata
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tree import Tree
from nltk.chunk import ne_chunk
from itertools import chain, groupby
from collections import defaultdict
import urllib2, urllib
import os
import json
from bs4 import BeautifulSoup
import random
from PIL import Image
import itertools
import subprocess
import time
import operator
try:
    import wikipedia
except ImportError as e:
    print "Library could not be imported. Web page will not be created"
import datetime
try:
    import matplotlib.pyplot as plt
except ImportError as e:
    print "Matplotlib could not be imported. Graphs will not be plotted"


NOUN_TAGS = ["NN", "NNS", "NNP", "NNPS"]
VERB_TAGS = ["VB", "VBD", "VBG", "VBP", "VBN", "VBP", "VBZ"]


class GoogleImageSearch:
    def __init__(self,location):
        self.location = location

    def download_image(self):
        keyword = self.location
        print "--------------------------Extracting image for " + str(self.location) + "--------------------------"
        image_type = "Image"
        keyword = keyword.split()
        keyword = '+'.join(keyword)
        url = "https://www.google.com/search?q=" + keyword + "&source=lnms&tbm=isch"
        # print url
        # DIR_PATH represents the path of the directory where the images will be stored
        DIR_PATH = "Pictures"
        header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
            }

        soup = BeautifulSoup(urllib2.urlopen(urllib2.Request(url, headers=header)), 'html.parser')

        ImagesList = []
        for a in soup.find_all("div", {"class": "rg_meta"}):
            link, type = json.loads(a.text)["ou"], json.loads(a.text)["ity"]
            ImagesList.append((link, type))
        # print "no of images is: " + str(len(ImagesList))
        dir_name = keyword.split('+')
        dir_name = '_'.join(dir_name)
        if not os.path.exists(DIR_PATH):
            os.mkdir(DIR_PATH)
        DIR_PATH = os.path.abspath(os.path.join(DIR_PATH, dir_name))

        if not os.path.exists(DIR_PATH):
            os.mkdir(DIR_PATH)
        num = random.randint(0,10)
        img, Type = ImagesList[num]
        try:
            req = urllib2.Request(img, headers={'User-Agent': header})
            raw_img = urllib2.urlopen(req).read()
            cntr = len([i for i in os.listdir(DIR_PATH) if image_type in i]) + 1
            if len(Type) == 0:
                f = open(str((os.path.join(DIR_PATH, image_type + "_" + str(cntr) + ".jpg"), 'wb')))
                print ("Image can be found at: " + str(os.path.join(DIR_PATH, image_type + "_" + str(cntr) + ".jpg")))
                # img_display = Image.open(str((os.path.join(DIR_PATH, image_type + "_" + str(cntr) + ".jpg")).encode('utf-8')))
                # img_display.show()
                # img_display.close()
            else:
                f = open(os.path.join(DIR_PATH, image_type + "_" + str(cntr) + "." + Type), 'wb')
                print ("Image can be found at: " + str(os.path.join(DIR_PATH, image_type + "_" + str(cntr) + Type)))
                # img_display = Image.open(os.path.join(DIR_PATH, image_type + "_" + str(cntr) + Type))
                # img_display.show()
                # img_display.close()
            # print "now writing image"
            f.write(raw_img)
            f.close()
        except Exception as e:
            print "could not load: " + img
            print e


class DataFromGutenberg:
    def __init__(self, id):
        self.bookID = id
        self.book_text = ""
        self.author = ""
        self.title = ""

    def read_book(self):
        text = strip_headers(load_etext(self.bookID)).strip()
        self.book_text = text

    def extract_metadata(self):
        url = "http://www.gutenberg.org/ebooks/" + str(self.bookID)
        page = urllib.urlopen(url)
        soup = BeautifulSoup(page,'html.parser')
        table = soup.find('div', attrs = {'id':'bibrec'})
        th_list = table.find_all('th')
        td_list = table.find_all('td')
        for i in range(0, len(th_list)):
            if th_list[i].text == 'Author':
                self.author = td_list[i].text
            elif th_list[i].text == 'Title':
                self.title = td_list[i].text
                print self.title
        if self.author == "":
            self.author = "Author not found"
        if self.title == "":
            self.title == "Title not found"

class TagData:
    def __init__(self, gutenberg_object):
        self.gutenberg_object = gutenberg_object
        self.sentences = []

    def extract_sentences(self):
        self.sentences = sent_tokenize(self.gutenberg_object.book_text)

    def extract_names(self):
        names = []
        for sentence in self.sentences:
            text = word_tokenize(sentence)
            tags = nltk.pos_tag(text)
            # for chunk in ne_chunk(tags):
                # if isinstance(chunk, Tree):
                    # print chunk
            for i in list(chain(*[chunk.leaves() for chunk in ne_chunk(tags) if isinstance(chunk, Tree)])):
                names.extend(i)
        unique_names = list(set(names))
        unique_names.remove("NNS")
        unique_names.remove("NNP")
        unique_names.remove("NNPS")
        print "unique names: ", unique_names
        return unique_names

    def tag_book_text(self):
        self.extract_sentences()
        self.unique_names = self.extract_names()
        for i in range(0, len(self.unique_names)):
            self.unique_names[i] = str(self.unique_names[i].encode('utf-8'))
        # print self.unique_names


class Interactions:
    def __init__(self, tag_object):
        self.tag_object = tag_object

    def find_interactions(self):
        gut_obj = self.tag_object.gutenberg_object
        temp_interactions = defaultdict(list)
        interaction_count = 0

        sentences = nltk.sent_tokenize(gut_obj.book_text)
        sentences = [nltk.word_tokenize(sent) for sent in sentences]
        sentences = [nltk.pos_tag(sent) for sent in sentences]

        grammar = r"""
        NP: {<PERSON> <.*>* <V.*> <.*>* <PERSON>}
        """
        r_parser = nltk.RegexpParser(grammar)
        for sentence in sentences:
            tree = r_parser.parse(nltk.ne_chunk(sentence))
            for subtree in tree.subtrees():
                if subtree.label() == 'NP':
                    if subtree != None:
                        # print "here"
                        interaction_count += 1
                        # temp_interactions[interaction_count].append([word for word, pos in subtree.pos() if pos == 'PERSON'])
                        word_list = []
                        for word, pos in subtree.pos():
                            if pos == 'PERSON':
                                act_word, tag = word
                                word_list.append(act_word.encode('utf-8'))
                        temp_interactions[interaction_count].append(word_list)

        # print temp_interactions
        interactions = {}
        interactor_list = []
        num_interactions = []
        for interaction in temp_interactions.itervalues():
            for character in interaction[0]:
                for oth_character in interaction[0]:
                    if character != oth_character:
                        # print character, oth_character
                        if (character + ", " + oth_character) in interactions.iterkeys():
                            interactions[character + ", " + oth_character] +=1
                        elif (oth_character + ", " + character) in interactions.iterkeys():
                            interactions[oth_character + ", " + character] += 1
                        else:
                            interactions[character + ", " + oth_character] = 1
        print "-----------------------------------------------------------------------------------"
        print "INTERACTIONS:"
        print interactions
        print "-----------------------------------------------------------------------------------"

        sorted_interactions = sorted(interactions.items(), key=operator.itemgetter(1))
        for interaction in interactions.iterkeys():
            interactor_list.append(interaction)
            num_interactions.append(interactions[interaction])

        try:
            fig, ax = plt.subplots()
            plt.title("Plot of characters v/c interactions")
            plt.xlabel("Character pairs")
            plt.ylabel("Number of interactions")
            plt.bar(interactor_list[len(interactor_list)-10:], num_interactions[len(num_interactions)-10:], color="black")

            for tick in ax.get_xticklabels():
                tick.set_rotation(20)
            legend_text = "X axis:1 unit=character pair\nY axis:2 units=1 interaction"
            plt.annotate(legend_text, (0.85, 1), xycoords='axes fraction')
            plt.savefig("person_person_interactions.jpg")
        except Exception as e:
            print "Graph could not be generated due to the following error:"
            print e


    def find_associations(self):
        gut_obj = self.tag_object.gutenberg_object
        associations = []
        association_count = 0

        sentences = nltk.sent_tokenize(gut_obj.book_text)
        sentences = [nltk.word_tokenize(sent) for sent in sentences]
        sentences = [nltk.pos_tag(sent) for sent in sentences]

        grammar = r"""
                NP: { <.>* <PERSON> <.*>+ <GPE> <.>* }
                    { <.>* <PERSON> <GPE> <.*>+ }
                    { <.>* <GPE> <.*>+ <PERSON> <.>* } 
                    { <.>* <GPE> <PERSON> <.*>+ } 
                    { <.>* <PERSON> <.*>+ <LOCATION> <.>* }
                """
        r_parser = nltk.RegexpParser(grammar)
        individual_associations = {}
        for sentence in sentences:
            statement = ""
            for ele in sentence:
                word, tag = ele
                statement += (str(word.encode('utf-8')) + " ")
            # print sentence
            tree = r_parser.parse(nltk.ne_chunk(sentence))
            for subtree in tree.subtrees():
                if subtree.label() == 'NP':
                    if subtree != None:
                        # print "here"
                        association_count += 1
                        # associations[association_count].append([word for word, pos in subtree.pos() if pos == 'PERSON' or 'LOCATION' or 'GPE'])
                        association = defaultdict(list)
                        person_list = []
                        location_list = []
                        for word, pos in subtree.pos():
                            if pos == 'PERSON':
                                act_word, tag = word
                                person_list.append(act_word)
                            elif pos == 'LOCATION' or 'GPE':
                                act_word, tag = word
                                # print act_word
                                if act_word != ','or '.'or '...' or '..':
                                    location_list.append(act_word)
                        association[association_count].append({'PERSON':person_list, 'LOCATION':location_list, 'SENTENCE': statement})
                        associations.append(association)
                        for character in person_list:
                            for loc in location_list:
                                # print character, oth_character
                                if (character + ", " + loc) in individual_associations.iterkeys():
                                    individual_associations[character + ", " + loc] += 1
                                elif (loc + ", " + character) in individual_associations.iterkeys():
                                    individual_associations[loc + ", " + character] += 1
                                else:
                                    individual_associations[character + ", " + loc] = 1
                        # print association


        # print association_count
        # print "\n\n\n\n\n\n"
        print "-----------------------------------------------------------------------------------"
        print "ASSOCIATIONS: "
        for association in associations:
            print association
        print "-----------------------------------------------------------------------------------"
        # output_file = open('output_file.txt', 'w')
        # output_file.write(associations)
        # output_file.close()
        assoc_list = []
        num_assoc = []
        sorted_interactions = sorted(individual_associations.items(), key=operator.itemgetter(1))
        for interaction in individual_associations.iterkeys():
            assoc_list.append(interaction)
            num_assoc.append(individual_associations[interaction])

        try:
            fig, ax = plt.subplots()
            plt.title("Plot of characters v/c location interactions")
            plt.xlabel("Character pairs")
            plt.ylabel("Number of interactions")
            plt.bar(assoc_list[len(assoc_list) - 10:], num_assoc[len(num_assoc) - 10:],
                    color="black")

            for tick in ax.get_xticklabels():
                tick.set_rotation(20)
            # legend_text = "X axis:1 unit=character-location pair\nY axis:2 units=1 interaction"
            # plt.annotate(legend_text, (0.85, 1), xycoords='axes fraction')
            plt.savefig("person_location_interactions.jpg")
        except Exception as e:
            print "Graph could not be generated due to the following error:"
            print e
        self.associations = associations


class ImageDownload:
    def __init__(self, interactions_object):
        self.interactions_object = interactions_object

    def extract_image(self):

        ele_list = random.sample(range(0, len(self.interactions_object.associations)), 10)

        for ele in ele_list:
            association = self.interactions_object.associations[ele]
            # print association
            # print ele
            sentence = association[ele+1][0]['SENTENCE']
            print sentence
            os.chdir("jythonMusic")
            process_jython = subprocess.Popen([".\jython.bat", "-i", "text_to_music.py", sentence],shell=True)
            time.sleep(5)
            process_jython.terminate()
            os.chdir('..')
            locations = association[ele+1][0]['LOCATION']
            for location in locations:
                location = str(location.encode('utf-8'))
                search_object = GoogleImageSearch(location)
                search_object.download_image()


class CreateHTMLPage:
    def __init__(self, gutenberg_object, tag_object, interactions_object, download_object):
        self.gutenberg_object = gutenberg_object
        self.tag_object = tag_object
        self.interactions_object = interactions_object
        self.download_object = download_object

    def extract_wiki_summary(self, keyword):
        summary = ""
        book_url = ""
        try:
            summary = wikipedia.summary(keyword)
            page = wikipedia.page(keyword)
            book_url = page.url
        except Exception as e:
            print e
        finally:
            if summary == "":
                summary = "Summary not found"
            if book_url == "":
                book_url = "URL not found"
            self.summary = summary
            self.book_url = book_url
            return summary

    def extract_date(self, book_url):
        url = book_url
        page = urllib.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find('table', attrs={'class': 'infobox vcard'})
        th_list = table.find_all('th')
        td_list = table.find_all('td')
        for i in range(0, len(th_list)):
            print th_list[i].text
        try:
            for i in range(0, len(th_list)):
                print th_list[i].text
                if th_list[i].text == 'Publication date':
                    self.pub_date = td_list[i].text
        except:
            print "Could not extract publication date"




    def create_page(self):
        out_file = open('BigIdea.html', 'w')
        out_file.write("<!DOCTYPE html>\n<html>\n<body>\n<h1 align='center'>\n<b>" + str(self.gutenberg_object.title) + "</b>\n</h1>\
        \n<h2 align = 'center'>"  + str(self.gutenberg_object.author) + "</h2>")
        book_summary = self.extract_wiki_summary(self.gutenberg_object.title)
        date = self.extract_date(self.book_url)
        author_summary = self.extract_wiki_summary(self.gutenberg_object.author)

        out_file.write("\n<h3>\nBook Summary:\n</h3>\n<p>" + str(book_summary.encode('utf-8')) + "</p>\n" )
        out_file.write("\n<h3>\nAuthor Summary:\n</h3>\n<p>" + str(author_summary.encode('utf-8')) + "</p>\n")

        try:
            out_file.write("\n<b>Publication Date: </b>" + str(self.pub_date))
        except:
            print "Did not find Publication date"
        # print book_summary
        # print author_summary
        out_file.write("\n</body>\n</html>")
        out_file.close()

class ImplementNLTK:
    def __init__(self, book_ID):
        gutenberg_object = DataFromGutenberg(book_ID)
        gutenberg_object.read_book()
        gutenberg_object.extract_metadata()
        tag_object = TagData(gutenberg_object)
        tag_object.tag_book_text()
        interactions_object = Interactions(tag_object)
        interactions_object.find_interactions()
        # interactions_object.find_associations()
        # download_object = ImageDownload(interactions_object)
        # download_object.extract_image()
        # page_object = CreateHTMLPage(gutenberg_object, tag_object, interactions_object, download_object)
        # try:
            # page_object.create_page()
        # except Exception as e:
            # print "Could not create web page due to following error"
            # print e

def main():
    # print "Enter the book ID of the book you want to access from the Gutenberg project"
    # book_ID = 11 # Alice's Adventures in Wonderland
    # book_ID = 8599 # Arabian Nights
    # book_ID = 53499 # Martin Luther
    # book_ID = 3289
    book_ID = 48320
    # book_ID = 11212 # Modern India
    # book_ID = int(raw_input())
    nltk_object = ImplementNLTK(book_ID)

if __name__ == "__main__":
    main()
