import spacy
from spacy.matcher import Matcher
import textacy
from textacy.extract import token_matches
import re
import webbrowser
from bs4 import BeautifulSoup
from pprint import pprint
import requests
import csv
import queue
import time
import random
from requests_html import HTMLSession
import os
from openai import OpenAI
from itertools import chain

#text = "The scripture quote was listed in Alma 15. This will be talking about the book of Mosiah."


# Notes:
# implement the better index counter into prophets_vs_scriptures.py
# implement mark removal based on M or m(done)
# distinguish between job and Job based on J or j(done)
# remove king james in the regex(done)
# fix book of mormon appearing in the text(done)
# add a proper noun checker for james, john, jacob, matthew, authors(done)
# add next word back into the code(done)



prophet_clarify_list = [512,514,526,528,543,554,555,563,581,582,588,598,600,603,604,620,633,639,648,652,668,672,674,675,679,702,761,764,781,788,800,803,806,814,820,821,825,826,847,858,860,886,901,905,911,915,922,924,937,939,944,947,968,984,998,1001,1022,1027,1034,1059,1066,1073,1105,1122,1140,1166,1173,1189,1197,1199,1221,1224,1239,1247,1248,1265,1267,1268,1271,1273,1277,1282,1306,1315,1319,1343,1347,1360,1368,1373,1390,1396,1399,1415,1418,1420,1435,1443,1456,1489,1499,1512,1514,1520,1533,1564,1566,1576,1587,1588,1603,1619,1629,1719,1721,1722,1741,1749,1754,1756,1760,1766,1767,1780,1781,1799,1809,1817,1849,3686,3700,3702,3708,3713,3739,3752,3757,3758,3766,3769,3770,3778,3791,3809,3814,3823,3826,3833,3842,3844,3848,3849,3851,3859,3870,3876,3887,3896,4002,4185,4468,4710,4759,4843,4849,4857,4860,4869,4879,4890,4893,4900,4903,4904,4914,4917,4918,4929,4946,4949,4962,5068,5079,5110,5128,5140,5142,5143,5188,5189,5191,5198,5215,5236,5239,5243,5251,5272,5296,5297,5300,5331,5336,5337,5341,5344,5346,5354,5357,5362,5377,5382,5391,5392,5393,5400,5407,5439,5440,5448,5452,5454,5457,5458,5459,5461,5477,5481,5482,5484,5485,5487,5490,5511,5512,5522,5523,5527,5533,5538,5542,5546,5551,5553,5554,5555,5556,5557,5558,5559,5560,5561,5562,5563,5564,5565,5566,5567,5568,5569,5570,5571,5572,5573,5574,5575,5576,5577,5578,5579,5580,5581,5582,5583,5584,5585,5586,5587,5588,5589,5590,5591,5592,5593,5594,5595,5596,5597,5598,5599,5600,5603,5604,5607,5609,5619,5623,5632,5639,5659,5670,5671,5673,5678]
#prophet_clarify_list = [462]
for i in prophet_clarify_list:
    i = str(i)
    print("article:" + str(i))
    url = "http://byu-studies-frontend.s3-website-us-west-2.amazonaws.com/article/"+i
    #webbrowser.open(url)

    #scrapes the page
    session = HTMLSession()
    try:
         response = session.get(url)
         response.html.render(sleep=.50)

         soup = BeautifulSoup(response.html.html, 'html.parser')
         article = soup.find(class_='text-lg article lg:min-w-[600px] pb-10')
         article_text = article.text
    except Exception as e:
            print(f"An error occurred: {str(e)}")
    finally:
        session.close()
    text = article_text.replace("\n\n", " ").replace("\n", " ")
    #print(text)


    def remove_numbered_scriptures(text):
        patterns = [
            r'Alma (?:6[0-3]|[1-5][0-9]|[1-9])',#removed Alma
            r'Ezra (?:10|[1-9])',#removed Ezra
            r'Esther (?:10|[1-9])',#removed Esther
            r'Job (?:42|[1-3][0-9]|[1-9])',#removed job
            r'Isaiah (?:66|[1-5][0-9]|[1-9])|',#removed Isaiah
            r'Daniel (?:12|[1-9]|10|11)',#removed Daniel
            r'Joel (?:[1-3])',#removed Joel
            r'Jonah (?:[1-4])',#removed Jonah
            r'Jacob (?:[1-7])',#removed Jacob
            r'Enos 1',#removed Enos
            r'Jarom 1',#removed Jarom
            r'Omni 1',#removed Omni
            r'Mosiah (?:2[0-9]|[1-9])',#removed Mosiah
            r'Alma (?:6[0-3]|[1-5][0-9]|[1-9])',#removed Alma
            r'Helaman (?:1[0-6]|[1-9])|Helaman(?!\s*\d)',#remove Helaman
            r'Ether (?:1[0-5]|[1-9])',#removed Ether
            r'Moroni (?:10|[1-9])',#removed Moroni
            r'Matthew (?:2[0-8]|1[0-9]|[1-9])',#remove Matthew
            r'Mark (?:1[0-6]|[1-9])',#removed Mark
            r'Luke (?:2[0-4]|1[0-9]|[1-9])',# removed Luke
            r'John (?:2[0-1]|1[0-9]|[1-9])',#removed John
            r'Romans (?:1[0-6]|[1-9])|Romans (?!\s*\d)',#removed Romans
            r'Philippians (?:[1-4])',#removed Philippians
            r'Philip\. (?:[1-4])',#removed Philip
            r'Jude 1',#removed Jude
            r'Moses (?:[1-8])|Moses\. (?!\s*\d)',#removed Moses
            r'Abraham (?:[1-5])',#removed Abraham
            r'\b[Bb]ook of [Mm]ormon\b',
            r'\b[Kk]ing [Jj]ames\b',
            r'mark',
            r'job'
        ]
        for pattern in patterns:
                matches = re.findall(pattern, text)
                matches = "".join(matches)
                #print(matches)
                if matches:
                    text = re.sub(pattern, "", text)
        #print(text)
        return text

        # Load a pre-trained SpaCy model
    nlp = spacy.load('en_core_web_sm')

    def remove_all_authors(all_author_reference):
        matcher = Matcher(nlp.vocab)
        patterns = [[{"TEXT": "Alma"}, {"POS": "PROPN"}],[{"TEXT": "Ezra"}, {"POS": "PROPN"}],[{"TEXT": "Esther"}, {"POS": "PROPN"}],[{"TEXT": "Job"}, {"POS": "PROPN"}],[{"TEXT": "Isaiah"}, {"POS": "PROPN"}],[{"TEXT": "Daniel"}, {"POS": "PROPN"}],[{"TEXT": "Joel"}, {"POS": "PROPN"}],[{"TEXT": "Jonah"}, {"POS": "PROPN"}],[{"TEXT": "Jacob"}, {"POS": "PROPN"}],[{"TEXT": "Enos"}, {"POS": "PROPN"}],[{"TEXT": "Jarom"}, {"POS": "PROPN"}],[{"TEXT": "Omni"}, {"POS": "PROPN"}],[{"TEXT": "Mosiah"}, {"POS": "PROPN"}],[{"TEXT": "Alma"}, {"POS": "PROPN"}],[{"TEXT": "Helaman"}, {"POS": "PROPN"}],[{"TEXT": "Ether"}, {"POS": "PROPN"}],[{"TEXT": "Moroni"}, {"POS": "PROPN"}],[{"TEXT": "Matthew"}, {"POS": "PROPN"}],[{"TEXT": "Mark"}, {"POS": "PROPN"}],[{"TEXT": "Luke"}, {"POS": "PROPN"}],[{"TEXT": "John"}, {"POS": "PROPN"}],[{"TEXT": "Romans"}, {"POS": "PROPN"}],[{"TEXT": "Philippians"}, {"POS": "PROPN"}],[{"TEXT": "Philip"}, {"POS": "PROPN"}],[{"TEXT": "Jude"}, {"POS": "PROPN"}],[{"TEXT": "Moses"}, {"POS": "PROPN"}],[{"TEXT": "Abraham"}, {"POS": "PROPN"}]]
        # patterns2 = [[{"POS":"PROPN"}, {"POS": "ADV"}], [{"POS":"PROPN"}, {"POS": "VERB"}]]
        for pattern in patterns:
            matcher.add("PROPER_NAME_PATTERN", [pattern])
        doc = nlp(all_author_reference)
        matches = matcher(doc)
        authors = [doc[start:end] for match_id, start,end in matches]
        #print(authors)     
        if authors != []:  
            for author in authors:
                without_authors = all_author_reference.replace(str(author), "")
            #print(without_authors)
        else:
             without_authors = all_author_reference
        return without_authors




    def find_nearest_punctuation(doc, index, direction):
                            sentence_ending_punctuation = '.!?'
                            if direction == "left":
                                for i in range(index, -1, -1):
                                    #print(doc[i].text + " " + str(i))
                                    if doc[i].text in sentence_ending_punctuation:
                                        #print(doc[i].text + " " + str(i))
                                        return i+1
                                return 0
                            elif direction == "right":
                                 for i in range(index, len(doc)):
                                     if doc[i].text in sentence_ending_punctuation:
                                         #print(doc[i].text)
                                         #print(i)
                                         return i
                                 return len(doc)

        # Custom classification function
    def classify_mormon(text):
            doc = nlp(text)
            results_scripture = []
            results_person = []
            target_words = {
                'alma', 'ezra', 'esther', 'job', 'isaiah', 'jeremiah', 'daniel', 
                'joel', 'jonah', 'jacob', 'enos', 'jarom', 'omni', 'mosiah', 'helaman', 
                'ether', 'moroni', 'matthew', 'mark', 'luke', 'john', 'romans', 
                'philippians', 'philip', 'james', 'jude', 'abraham'
            }
            prophet_index_list = []
            surrounding_words_list = []
            if text == "":
                results_scripture.append("No Prophet scripture references")
            else:
                seen = set()
                for i, token in enumerate(doc):
                    if token.text.lower() in target_words:
                        if i not in seen:
                            prophet_index_list.append(i)
                            seen.add(i)            
            #print(prophet_index_list)

            if token:
                    for index in prophet_index_list:
                                seen = set()
                                #print(index)
                                start_index = find_nearest_punctuation(doc, index, "left")
                                #print(start_index)
                                end_index = find_nearest_punctuation(doc, index, "right")
                                #print(end_index)
                                surrounding_text = doc[start_index:end_index]
                                #print(surrounding_text)
                                #print("space")
                                surrounding_words = [t.text.lower() for t in surrounding_text]
                                surrounding_words = ' '.join(surrounding_words)
                                #print(surrounding_words)
                                #print("space")

                                if 'book' in surrounding_words or 'scripture' in surrounding_words or 'chapter' in surrounding_words:
                                    results_scripture.append((token.text))
                                    #print(results_scripture)
                                    seen = set()
                                    if surrounding_words not in seen:
                                        surrounding_words_list.append(surrounding_words)
                                        seen.add(surrounding_words)
                    #print(surrounding_words_list)
            else:
                    results_person.append((token.text, 'Person'))
            if surrounding_words_list != []:
                surrounding_words_string = ' '.join(surrounding_words_list)
                #print(surrounding_words_string)
                print(cut_string_before_keywords(surrounding_words_string))
            else:
                print("No Prophet scriptures")
            return results_scripture
    def cut_string_before_keywords(text):
        # Define the pattern to match "book", "scripture", or "chapter" (case-insensitive)
        pattern = r'\b(book|scripture|chapter)\b'
        pattern2 = r'\bAlma\b|\bEzra\b|\bEsther\b|\bJob\b|\bIsaiah\b|\bJeremiah\b|\bDaniel\b|\bJoel\b|\bJonah\b|\bJacob\b|\bEnos\b|\bJarom\b|\bOmni\b|\bMosiah\b|\bHelaman\b|\bEther\b|\bMoroni\b|\bMatthew\b|\bMark\b|\bLuke\b|\bJohn\b|\bRomans\b|\bPhilippians\b|\bPhilip\b|\bJames\b|\bJude\b|\bAbraham\b'
        # Search for the pattern in the text
        match = re.search(pattern, text, re.IGNORECASE)
                                
        if match:
            # Find the start position of the match
            cut_front = match.start()
            # Return the substring from the cut position onward
            front_cut_result = text[cut_front:]
            match2 = re.search(pattern2, front_cut_result, re.IGNORECASE)

            if match2:
                cut_back = match2.end()
                remaining_text = front_cut_result[cut_back:].strip()
                next_word = re.search(r'\b\w+\b', remaining_text)

                if next_word:
                    extra_word_end = next_word.end()
                    final_cut_result = front_cut_result[:cut_back+extra_word_end+1]
                    #print(final_cut_result)
                    return final_cut_result
                                        
        return text




    # def remove_duplicates(items):
    #         """Remove duplicate items from a list."""
    #         #print(items)
    #         seen = set()
    #         unique_items = []
    #         for item in items:
    #             #if item == "No Prophet scripture references":
    #             #     unique_items.append(item)
    #             if item not in seen:
    #                 unique_items.append(item)
    #                 seen.add(item)
    #         #print(unique_items)
    #         return unique_items



    # Process the text and classify 'Mormon'
    removed_number_scriptures = remove_numbered_scriptures(text)
    removed_all_authors = remove_all_authors(removed_number_scriptures)
    classifications = classify_mormon(removed_all_authors)
    #print(classifications)
    #removed_duplications = remove_duplicates(classifications)
    #print(removed_duplications)


    unique_item_list = []

    #if removed_duplications == ["No Prophet scripture references"]:
        #for unique_item in removed_duplications:
        #print(unique_item)
        #    scriptures_with_prophet_names = str(unique_item)+"+"+str(i)
            # print(scriptures_with_prophet_names)
            # with open('prophets_vs_scriptures2.csv', 'a', newline='') as file:
            #     writer = csv.writer(file)
            #     writer.writerow([scriptures_with_prophet_names])
    #else:
        #for unique_item in removed_duplications:
            #if unique_item != "No Prophet scripture references":
            #    unique_item_list.append(unique_item)
        #unique_item_string = ", ".join(unique_item_list)
        #scriptures_with_prophet_names = unique_item_string+"+"+str(i)
        #print(scriptures_with_prophet_names)
        #with open('prophets_vs_scriptures2.csv', 'a', newline='') as file:
        #    writer = csv.writer(file)
        #    writer.writerow([scriptures_with_prophet_names])
            #print(scriptures_with_prophet_names)
            