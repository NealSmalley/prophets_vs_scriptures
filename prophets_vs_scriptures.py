import spacy
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
# find difference between Mark and mark




for i in range(12,13):
    i = str(i)
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
        ]
        for pattern in patterns:
                matches = re.findall(pattern, text)
                matches = "".join(matches)
                #print(matches)
                if matches:
                    text = re.sub(matches, "", text)
        print(text)
        return text

        # Load a pre-trained SpaCy model
    nlp = spacy.load('en_core_web_sm')

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
            if text == "":
                results_scripture.append("No Prophet scripture references")
            else:
                for token in doc:
                    if token.text.lower() in target_words:
                            surrounding_text = doc[max(token.i - 5, 0): min(token.i + 6, len(doc))]
                            surrounding_words = [t.text.lower() for t in surrounding_text]
                            #print(surrounding_words)
                            # Custom rules for determining if it's the scripture or person
                            if 'book' in surrounding_words or 'scripture' in surrounding_words or 'chapter' in surrounding_words:
                                results_scripture.append((token.text))
                                #print(surrounding_words)
                            else:
                                results_person.append((token.text, 'Person'))
                    if token.text.lower() not in target_words:
                        #print("No Prophet scripture references")
                        results_scripture.append("No Prophet scripture references")
            return results_scripture



    def remove_duplicates(items):
            """Remove duplicate items from a list."""
            #print(items)
            seen = set()
            unique_items = []
            for item in items:
                #if item == "No Prophet scripture references":
                #     unique_items.append(item)
                if item not in seen:
                    unique_items.append(item)
                    seen.add(item)
            #print(unique_items)
            return unique_items



    # Process the text and classify 'Mormon'
    removed_number_scriptures = remove_numbered_scriptures(text)
    classifications = classify_mormon(removed_number_scriptures)
    #print(classifications)
    removed_duplications = remove_duplicates(classifications)
    #print(removed_duplications)


    unique_item_list = []

    if removed_duplications == ["No Prophet scripture references"]:
        for unique_item in removed_duplications:
        #print(unique_item)
            scriptures_with_prophet_names = str(unique_item)+"+"+str(i)
            # print(scriptures_with_prophet_names)
            # with open('prophets_vs_scriptures2.csv', 'a', newline='') as file:
            #     writer = csv.writer(file)
            #     writer.writerow([scriptures_with_prophet_names])
    else:
        for unique_item in removed_duplications:
            if unique_item != "No Prophet scripture references":
                unique_item_list.append(unique_item)
        unique_item_string = ", ".join(unique_item_list)
        scriptures_with_prophet_names = unique_item_string+"+"+str(i)
        #print(scriptures_with_prophet_names)
        #with open('prophets_vs_scriptures2.csv', 'a', newline='') as file:
        #    writer = csv.writer(file)
        #    writer.writerow([scriptures_with_prophet_names])
            #print(scriptures_with_prophet_names)
            