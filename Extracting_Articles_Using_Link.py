import pandas as pd
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

# getting data from given Input.xlsx file
file_links= pd.read_excel("Input.xlsx")

from nltk import sent_tokenize

# Creating a dictionary for those pages which have different tags for the article text
different_structure_pages={}

# iterating through each record
for index in tqdm(file_links.index):
    try:

        #creating filename where the text will be stored
        filename= "Extracted_Articles/"+ str(file_links["URL_ID"][index])+".txt"

        # store link
        link= file_links["URL"][index]

        #getting request using link
        request= requests.get(link)
        request.encoding= 'utf-8'

        #storing the data received from request
        content= request.text

        # creating a soup
        soup=BeautifulSoup(content, 'html.parser')

        # finding text with specific tag and class using soup
        article= soup.find('div',class_="td-post-content tagdiv-type").text

        # to remove special characters like "\n" from the text
        article= " ".join(article.split())

        # removes the last line which has author description
        article= " ".join(sent_tokenize(article)[:-1])

        #saving text into a text file with same name as associated URL_ID
        with open(filename, "w", encoding="utf-8") as openfile:
            openfile.write(article)

    #exception will help in storing all the pages which have a different tag format   
    except Exception as e:
        different_structure_pages[file_links["URL_ID"][index]]= link


#Operating on the collected different structured pages
for key,value in tqdm(different_structure_pages.items()):
    try:
        #creating filename where the text will be stored
        filename= "Extracted_Articles/"+ str(key)+".txt"

        #stores link
        link= value
        
        #sending request
        request= requests.get(link)

        #creating soup
        soup=BeautifulSoup(request.text, 'html.parser')

        #finding all the tags with same class and then getting the 14th occurence with containes the text
        article= soup.find_all('div',class_="tdb-block-inner td-fix-index")[14]
        article= article.text

        #removes special characters
        article= " ".join(article.split())

        #removes author description given at the end of the text
        article= " ".join(sent_tokenize(article)[:-1])

        #storing text into a text file with name same as the associated URL_ID
        with open(filename, "w", encoding="utf-8") as openfile:
            openfile.write(article)
    
    #exception will deal with pages that does not exits ("Page Not Found") - There are two pages in this data that does not exits
    except Exception as e:
        print(f" page with URL_ID {key} is not found")
