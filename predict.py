import fasttext.util
import os
import re
import spacy
import string
import pandas as pd
import warnings
warnings.filterwarnings("ignore")   
# model=fasttext.load_model( "cc.it.300.bin")
from estraction_skills import pdf_to_html,extractjobb,extract_skills_npl,fasttext_skills,ner,ita_skills,eng_skills

def main(pdfnamepath,language):
 skills=[]
 category= "Category: Not Found"
 if language.strip()=="English":
    skills,tipojob=ner(pdfnamepath)
    category=tipojob[0]

 if language.strip() == "Italian":
   
    
    allskills,tipojob=ita_skills(pdfnamepath)
  
    skills=[i for i in allskills if i.strip()!='']
    

   
    category=tipojob[0]
 

 if category.strip()=='' :
     category="Category: Not Found"
     
 return  category,list(set(skills)),






