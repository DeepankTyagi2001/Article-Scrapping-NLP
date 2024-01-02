from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk import sent_tokenize
from nltk.corpus import stopwords
import string
from math import ceil
import re
from tqdm import tqdm
import pandas as pd
import json

def find_complex_words(words):
    #Complex words- syllables>2 except 'e' in 'ed' and 'es'
    
    #list to store complex words
    complex_words=[]

    #variable to count complex words
    complex_words_count=0

    #variable to count syllables per word ( in whole text)
    syllable_per_word_count=0
    
    #creating a for loop to iterate through each word and check the number of syllables except 'ed' and 'es'
    for word in words:
        syllable_count= len(re.findall(r"[aeiouAEIOU]+",word))  #count all the syllables present in the word
    
        #if word ends with 'es' or 'ed' and syllable count > 3 then it is a complex word
        if re.findall(r"(es|ed)$",word):
            if syllable_count>3:
                complex_words.append(word)
                complex_words_count+=1
                syllable_per_word_count+=syllable_count-1  #dding syllable count after subtracting the 'e' of 'es' or 'ed'
        else:
            if syllable_count>2:
                complex_words.append(word)
                complex_words_count+=1
                syllable_per_word_count+=syllable_count
    return complex_words_count, syllable_per_word_count


def calculate_pronouns(punctuation_free_words):

    # assigning counting variable
        pronouns_count=0

    #creating a for loop to separate out pronouns using regex
        for word in punctuation_free_words:
            #US is not included in matching pattern as specified in the given instructions
            pattern_to_find_pronouns= r"\bwe\b|\bWe\b|\bi\b|\bI\b|\bus\b|\bUs\b|\bmy\b|\bMy\b|\bours\b|\bOurs\b" 
            if re.match(pattern_to_find_pronouns,word):
                pronouns_count+=1
                # print(word)
        return pronouns_count
        
        
def tokenization(text):
    
    #tokenizes text into sentences
    sentences= sent_tokenize(text)  
    
    #total number of sentences
    total_sentences= len(sentences)  

    #tokenizes text into words
    words= word_tokenize(text)           

    #replacing punctuation characters with ''
    re_punc = re.compile('[%s]' % re.escape(string.punctuation))     
    punctuation_free_words=  [re_punc.sub('', w) for w in words]

    #removing the remaining characters which are not aplhaneumeric
    punctuation_free_words= [word for word in punctuation_free_words if word.isalpha()]

    return punctuation_free_words,total_sentences

def pos_neg_words(words):
    #postitve words list
    pos_words=[]

    #negative words list
    neg_words=[]

    #Sentiment Analysis object using VADER
    Text_Analyzer= SentimentIntensityAnalyzer()

    #iterating through each word to get positive and negative words if scores are greater than 0.5
    for word in words:
        if Text_Analyzer.polarity_scores(word)['pos']>0.5:
            pos_words.append(word)
        elif Text_Analyzer.polarity_scores(word)['neg']>0.5:
            neg_words.append(word)
    
    #positive score= number of positive words (deduced according to the given definition)
    positive_score= len(pos_words)

    #negative score= number of negative words (deduced according to the given definition)
    negative_score= len(neg_words)

    #polarity score (according to the given definition)
    polarity_score= (positive_score-negative_score)/(positive_score+negative_score+0.000001)

    #subjectivity score (according to the given definition)
    subjectivity_score= (positive_score+negative_score)/(len(words)+0.000001)
    
    return positive_score,negative_score,polarity_score,subjectivity_score,pos_words,neg_words


#getting data from the given "Output Data Structure.xlsx" file
outputfile= pd.read_excel("Output Data Structure.xlsx")

#positive and negative words list to create dictionary later
positive_words=[]
negative_words=[]

#iterating through all the records of the output file to do text analysis one by one and save the values in the associated columns
for index in tqdm(outputfile.index):
    try:
        #accessing files from "Extracted_Articles" folder with same "URL_ID"
        filename= "Extracted_Articles/"+str(outputfile["URL_ID"][index])+".txt"
        file= open(filename,'r',encoding='utf-8')
        text=file.read()
        file.close()
        
        #function call to get punctuation free words and total number of sentences
        punctuation_free_words,total_sentences=tokenization(text)
    
        #total number of words
        total_words= len(punctuation_free_words)
        
        #calling function to count the pronouns [called before removing stop words because otherwise it will remove the pronouns]
        pronouns_count=calculate_pronouns(punctuation_free_words)
        
        #saving the output to "PERSONAL PRONOUNS" column
        outputfile["PERSONAL PRONOUNS"][index]= pronouns_count
    
        #filter out stop words
        stop_words = set(stopwords.words('english'))
        punctuation_free_words = [w for w in punctuation_free_words if not w in stop_words]
        
        #converting all words into smallercase
        punctuation_free_words=[word.lower() for word in punctuation_free_words]
        #saving the output to "WORD COUNT" column
        outputfile["WORD COUNT"][index]= len(punctuation_free_words)
        
        #calling function to calculate complex words count and syllable per word count
        complex_words_count, syllable_per_word_count = find_complex_words(punctuation_free_words)
        #saving the output to "COMPLEX WORD COUNT" column
        outputfile["COMPLEX WORD COUNT"][index]= complex_words_count
    
        # character counting in words
        char_count=0
        for word in punctuation_free_words:
            char_count+=len(word)
        #saving the output to "AVG WORD LENGTH" column
        outputfile["AVG WORD LENGTH"][index]= ceil((char_count)/len(punctuation_free_words))
        

        #saving the output to "SYLLABLE PER WORD" column
        outputfile["SYLLABLE PER WORD"][index]= syllable_per_word_count
    
        #average word per sentence
        #saving the output to "AVG NUMBER OF WORDS PER SENTENCE" column
        outputfile["AVG NUMBER OF WORDS PER SENTENCE"][index]= ceil(total_words/total_sentences)
    
        #average sentence length
        #saving the output to "AVG SENTENCE LENGTH" column
        outputfile["AVG SENTENCE LENGTH"][index]= ceil(total_words/total_sentences)
    
        #percentage of complex words
        #saving the output to "PERCENTAGE OF COMPLEX WORDS" column
        outputfile["PERCENTAGE OF COMPLEX WORDS"][index]= (complex_words_count/total_words)
    
        #FOG index
        #saving the output to "FOG INDEX" column
        outputfile["FOG INDEX"][index]=0.4*(complex_words_count/total_words)+(total_words/total_sentences)
    
        #function call to get positive score, negative score , polarity score, subjectivity score, positive and negative words
        positive_score,negative_score,polarity_score,subjectivity_score,pos_words,neg_words= pos_neg_words(punctuation_free_words)
        for word in pos_words:
            positive_words.append(word)

        for word in neg_words:
            negative_words.append(word)


        #saving the output to "POSITIVE SCORE" column
        outputfile["POSITIVE SCORE"][index]=positive_score

        #saving the output to "NEGATIVE SCORE" column
        outputfile["NEGATIVE SCORE"][index]=negative_score

        #saving the output to "POLARITY SCORE" column
        outputfile["POLARITY SCORE"][index]=polarity_score

        #saving the output to "SUBJECTIVITY SCORE" column
        outputfile["SUBJECTIVITY SCORE"][index]=subjectivity_score
    except Exception as e:
        print(e)

#saving all positive words and negative words into a MasterDictionary in "MasterDictionary" folder
MasterDictionary={}

#making sure no duplicate values are present in the lists
positive_words= list(set(positive_words))
negative_words= list(set(negative_words))

MasterDictionary["Positive Words"]= positive_words
MasterDictionary["Negative Words"]= negative_words
with open('MasterDictionary/MasterDictionary.json','w') as dictfile:
    json_object= json.dump(MasterDictionary,dictfile)

#saving final output to "Final_Output_File.csv"    
#[Note: Two file links are not working (page not found error), hence out of 114 entries 2 are blank]
outputfile.to_csv("Final_Output_File.csv",index=False)