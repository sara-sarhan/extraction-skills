import fasttext.util
import os
import warnings
warnings.filterwarnings("ignore")   
# model=fasttext.load_model( "cc.it.300.bin")
from estraction_skills import skills_extraction

def main(pdfnamepath):


    Clss_skills=skills_extraction(pdfnamepath,os.path.join(os.getcwd(), "model", 'cc.it.300.bin'))
    allskills,tipojob,address,mails_find,name_find,data_nascita=Clss_skills.ita_skills()
    address_=[i for i in [address+["non troovati"]][0]  if   i is not None and i.strip()!=''][0]
    mails_=[i for i in [mails_find+["non troovati"]][0]  if  i is not None and i.strip()!=''][0]
    name_=[i for i in [name_find+["non troovati"]][0] if  i is not None and i.strip()!=''][0]
    data_=[i for i in [data_nascita+["non troovati"]][0] if   i is not None and i.strip()!=''][0]
    
      
    skills=[i for i in allskills if i.strip()!='']
    
    
       
    category=tipojob[0]
 

    if category.strip()=='' :
      category="Category: Not Found"
     
    return  category,list(set(skills)),address_,mails_,name_,data_






