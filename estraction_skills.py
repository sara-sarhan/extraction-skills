import spacy
import string
import re
import pandas as pd
import os
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.converter import HTMLConverter
import io
import  fasttext
import numpy as np
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

class skills_extraction():
   def __init__(self, pdfnamepath,pathmodel):  
       self.pdfnamepath=pdfnamepath
       self.pathmodel=pathmodel
      
       from spacy.lang.it.stop_words import STOP_WORDS
       self.stop = list(spacy.lang.it.stop_words.STOP_WORDS)
       self.stop.extend(['e','i'])
       skills = pd.read_csv(os.path.join(os.getcwd(), "dataset","skills.csv"), encoding='utf-8')
       prog=list(skills.columns)
       filename = os.path.join(os.getcwd(), "dataset",'programming-languages-corrected.csv')
       dffull = pd.read_csv(filename,sep=';', encoding = "ISO-8859-1")
       with open( os.path.join(os.getcwd(), "dataset",'skills_cv.txt')) as f:
            skills_cv = f.read().splitlines() 
       self.namesprogramming=list(set(dffull['ï»¿name'].tolist()+prog+skills_cv)) 
       for i in ['y)','C','D','T','L','E','F','B','S']:
           self.namesprogramming.remove(i)
           
    
       full_occupations = pd.read_csv(os.path.join(os.getcwd(), "dataset","occupation_full.csv"), encoding='utf-8')
   
       self.listjob=pd.read_csv(os.path.join(os.getcwd(), "dataset","jobs_title.csv"), encoding='utf-8',delimiter=';')['jobs'].tolist()
       self.listjob.sort() 
       tipojob=[]
       
       
       full_occupations_skills = full_occupations[['essential_skills', 'optional_skills','isco_group']]
       full_occupations_skills['essential_skills'] = full_occupations_skills['essential_skills'].apply(lambda x: ','.join(str(x).split('; ')))
       full_occupations_skills['optional_skills'] = full_occupations_skills['optional_skills'].apply(lambda x: ','.join(str(x).split('; ')))
       
       full_occupations_skills_clean = pd.DataFrame({'occupations_skillset': full_occupations_skills['essential_skills']})
       l=[]
       spliskills=full_occupations_skills_clean['occupations_skillset'].str.split(',').tolist()
       l = [x.strip() for lista in spliskills for x in lista if x]
       self.namesprogramming.append('ibatis')
       self.namesprogramming.extend(["Eclipse", "Java" "J2EE", "HTML", "JSP"," JAX RPC", "JAXB", "CSS3", "JavaScript",  "jQuery", "Spring MVC", "Hibernate"," RESTful web services", "Apache Tomcat", "Cucumber", "Cassandra", "Junit", "Jenkins", "Maven", "GitHub", "XML", "Log4j", "EJB", "MySQL", "Ajax"])
       self.uniqueskills=list(set(l))
       self.nlpRemove = spacy.load("it_core_news_lg")
      
         
       self.model = fasttext.load_model(self.pathmodel)
      
       self.namesprogramming.remove('p')
       self. namesprogramming.remove('J')
       self.namesprogramming.remove('G')
       self.namesprogramming.remove('es')
       self.namesprogramming.remove('FL')
       self.namesprogramming.remove('Io')
       self.namesprogramming.remove('K')

   def extract_name(self,text):
       with open(os.path.join(os.getcwd(), "dataset", 'NomiCognomi.txt'),encoding="utf8") as f:
           linesnames = [i.replace('\n',' ').title() for i in f.readlines() ]
       text=text.replace(':','').title().strip()
       NAME = re.findall("((Curriculum Vitae|Informazioni Personali|Nome|Cognome|Nome e Cognome) ([A-Z].?\s?)*([A-Z][a-z]+\s?)+)|(([A-Z].?\s?)*([A-Z][a-z]+\s?)+(Curriculum vitae|Informazioni Personali|Nome|Cognome))", text)

       if NAME:
           try:
               if "@" in NAME[0][0]:
                   name=NAME[0][0][-1].split("@")[0].replace('Curriculum Vitae',' ').replace('Informazioni Personali',' ').replace('Cognome',' ').replace('Nome',' ')
               else:
                 name= NAME[0][0].replace('Curriculum Vitae',' ').replace('Informazioni Personali',' ').replace('Cognome',' ').replace('Nome',' ')
               return name
           except IndexError:
               return -1
       else:
           for s in linesnames:
                      
                    
                       span_list = [(match.start(), match.end()) for match in
                                     re.finditer(fr"\b{s.strip()}\b", text.title().strip())]
                      
                       if span_list and len(text.split())<=4:
                           print('NAME',text)
                           return text
         
   def extract_address(self,text,last):
        '''
        Helper function to extract email id from text

        :param text: plain text extracted from resume file
        '''
        text=text.replace(':','').lower().replace('\n','').replace('cap.','').replace('n.','').replace(',','')
        text=re.sub(r'[0-9\n]', '', text.strip().lower()).replace(" ", " ").replace('n°','').replace('–','')
        text=" ".join(text.split())
        address = re.findall("((corso,residenza|luogo di nascita|domicilio|via|viale|piazza|vicolo|piazzale|viale|contrada|circonvallazione) ([a-z].?\s?)*([a-z][a-z]+\s?)+)", text)
      
       
        if address:
            try:
                return address[0][0]
            except IndexError:
                return -1   

   def extract_email(self,text):
       '''
       Helper function to extract email id from text

       :param text: plain text extracted from resume file
       '''
       text=text.replace(':','')
       email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", text)
       if email:
           try:
               return email[0].split()[0].strip(';')
           except IndexError:
               return -1
   def extract_date(self,text,last):
       '''
       Helper function to extract email id from text

       :param text: plain text extracted from resume file
       '''
       text=text.replace(':','').lower().strip()
       data = re.findall("(((\d{1,4}([.\-/])([.\-/])\d{1,4}\s)(nascita|nata|data di nascita|nato|nascita|di nascita))|(nascita|nata|data di nascita|nato|di nascita) ((\d{1,4}([.\-/])\d{1,2}([.\-/])\d{1,4}))|(nascita|nata|data di nascita|nato|di nascita) ((\s\d{1,4}([.\-/])\d{1,2}([.\-/])\d{1,4})))", text)
      
       if data:
           try:
               return data[0][0]
           except IndexError:
               return -1
       else:
           for s in ["nascita","nata","data di nascita","nato",'nascita','luogo di nascita','di nascita']:
                     
                   
                       span_list = [(match.start(), match.end()) for match in
                                   re.finditer(fr"\b{s}\b", last.lower())]
                       span_list2 =  [(match.start(), match.end()) for match in
                                   re.finditer(fr"\b{s}\b", text.lower())]
                       data = re.findall("(((\d{1,4}([.\-/])([.\-/])\d{1,4}\s))|((\d{1,4}([.\-/])\d{1,2}([.\-/])\d{1,4}))| ((\s\d{1,4}([.\-/])\d{1,2}([.\-/])\d{1,4})))", text)
                       if  data and len(span_list)>0 and len(span_list2)==0:
                           print('data', text)
                           return text



  
   def convert(self,fname):
       pagenums = set();
       
       manager = PDFResourceManager()
       codec = 'utf-8'
       caching = True
    
     
       output = io.BytesIO()
       converter = HTMLConverter(manager, output, codec=codec, laparams=LAParams())
    
       interpreter = PDFPageInterpreter(manager, converter)  
       infile = open(fname, 'rb')
     #  print("fname...",fname)
       for page in PDFPage.get_pages(infile, pagenums,caching=caching, check_extractable=False):
           interpreter.process_page(page)
    
       convertedPDF = output.getvalue()  
    
       infile.close(); converter.close(); output.close()
       return convertedPDF
   def extractjobb(self,resume_sections)  :
      tipojob=[]
      print("START extractjobb")
    
      for testskill in resume_sections:
    
       
        
       if len(tipojob)<1:
           
        for idx,job in enumerate(self.listjob):
       

           span_list = [(match.start(), match.end()) for match in
                    re.finditer(fr"\b{job}\b",testskill )]
           if span_list :
               tipojob.append(job)

               break
   
      print("END extractjobb")
      return tipojob



      
   def extract_skills_npl(self,resume_sections,listacompetenze,worddelete):

       unionskills=[]   
       skillmach=[]
       
       print("START extract_skills_npl")
    
       for testskill in resume_sections:
    
        span_list=[]
        for competenze in listacompetenze: #[ ,'responsabile della','acquisito esperienza','acquisito una collaudata esperienza',
             mach=[(match.start(), match.end()) for match in
                        re.finditer(fr"\b{competenze}\b", testskill)]
             if mach:
                span_list.extend(mach)
               
        if  span_list:  
            if len(testskill)>1:
                
                   for i in range(len(span_list)-1):
                 
                       skillfound=testskill[span_list[i][0]:span_list[i+1][0]]
                       skillmach.append(skillfound ) 
                   skillfound=testskill[span_list[len(span_list)-1][0]:]
                   skillmach.append(skillfound )    
                   if  skillfound.strip()!='' and skillfound not in self.stop and skillfound not in  skillmach and len(skillfound.split())>1 and skillfound not in worddelete:
                      skillmach.append(skillfound.strip() ) #
            else:
               
                if testskill[span_list[0][0]:].strip()!='' and span_list and \
                    testskill[span_list[0][0]:] not in self.stop and testskill not in  skillmach\
                     and len(testskill[span_list[0][0]:].split())>1 and testskill[span_list[0][0]:] \
                         not in worddelete and testskill[span_list[0][0]:] not in skillmach:
                   skillmach.append(testskill[span_list[0][0]:].strip() ) #
       
        #print("testskill",testskill)
        doc = self.nlpRemove(testskill) #clean_txt2(testskill,nlpRemove,stop)
        start=0
        end=0
        verb=[]
        sentece=[]
        endold=0
    
       
        if doc:
            idx=0
    
            for token in doc:
              idx+=1  
          
    
              if token.pos_ == "NOUN" or token.pos_ == "VERB":#  or token.pos_=='DET':
                  start= token.idx  # Start position of token
                  end = token.idx + len(token)  # End position 
                 
                  if token.pos_ == "VERB" : # or token.text in ["conoscenza","competenze","capacità"]:
                     verb.append(token.pos_)
                  
                     # distanza verbo e noun poca al massimo tra verbo e parola ci può stara un adj oa o poco altro 
                
                  if len(verb)>0  and   (-endold +start<= 3 or endold==0) :
    
                      
                      
                      sentece.append( token.text ) # token.text
                      
                      endold= end
                      #oldtoken=token.pos_
                      # se ho 2 verbi sono 2 frrasi e si spezzano
                      if " ".join(sentece).strip()!='' and len(sentece)>=2 and len(verb)>1:
                         sentece.remove( token.text)
                         
                         verbo=verb[-1]
                         verb=[verbo]
                         if len(sentece)>=2:
    
                             unionskills.append(" ".join(sentece))
                         sentece=[ token.text]  #[ token.lemma_]
                       
            if len(verb)==1  and " ".join(sentece).strip()!='' and len(sentece)>1:
                unionskills.append(" ".join(sentece).strip())
       print("END extract_skills_npl")
       return unionskills ,skillmach

   def cosine_similarity(self,v1, v2):
       mag1 = np.linalg.norm(v1)
       mag2 = np.linalg.norm(v2)
       if (not mag1) or (not mag2):
           return 0
       return np.dot(v1, v2) / (mag1 * mag2)
   
   def fasttext_skills(self,unionskills,uniqueskills):
       
      print ("START fasttext_skills")
      candidate_skills_fasttext=[]
      candidate_skills_eco=[]
      for word  in unionskills:
          if len(word.split())<=3:
                threshold=0.75
          else:
              threshold=0.69
          resumes_clean_vec=self.model.get_sentence_vector(word)

          for idx,skills in enumerate(uniqueskills):  #[i for i in row['occupations_skillset'].split(',') ]:
                
                 skills_vec=self.model.get_sentence_vector(skills)
                 
                 score_skill=self.cosine_similarity(skills_vec, resumes_clean_vec)
                 
               
                 if score_skill > threshold and word not in candidate_skills_fasttext:
                                 print( 'word', word, 'skill', skills, score_skill)
                             
                                 candidate_skills_fasttext.append(word)
                                 candidate_skills_eco.append((skills,score_skill))
                                 break
      print("END fasttext_skills")
      return  candidate_skills_fasttext,candidate_skills_eco


   def ita_skills(self):
      
     
      listsentece,programmingskills,address,mails_find,name_find,data_nascita=self.pdf_to_html()

      
      listacompetenze=['skills','addetto al','addetta al','specializzato in','specializzata in',"conoscenza","competenze","capacità",'predisposizione al',"specializzato nell","specializzata nell"]
      worddelete=['capacità e competenze personali','patente guida',"capacità di lettura  capacità di scrittura  capacità di espressione orale","capacità di lettura",  "capacità di scrittura", "capacità di espressione orale", 'capacità di','competenze personali','competenze informatiche','capacità e competenze informatiche','capacità e competenze']
      skills,skillmach=  self.extract_skills_npl(listsentece,listacompetenze,worddelete)
      
      tipojob= self.extractjobb(listsentece)
   
    
      candidate_skills_fasttext,candidate_skills_eco=self.fasttext_skills(skills,self.uniqueskills)
      allskills=candidate_skills_fasttext+programmingskills+skillmach
   
      return  allskills,tipojob,address,mails_find,name_find,data_nascita
 
   def pdf_to_html(self):
    print("START pdf_to_html")
    filePDF = self.pdfnamepath #("input directory; your pdf file:   ")
    path=os.getcwd()

    fileHTML = os.path.join(path,filePDF+'dOPUT.html')
    convertedPDF = self.convert( filePDF)
    fileConverted = open(fileHTML, "wb")
    fileConverted.write(convertedPDF)
    fileConverted.close()
    address=[]
    mails_find=[]
    name_find=[]
    data_nascita=[]
    with open(fileHTML, 'r',encoding='utf8') as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'lxml')
        h4s = soup.find_all('div')
        frasi=['0']
        for h4 in h4s:
          frase=[]
          for sentece in h4.find_all("span"):
              s=sentece.text.strip()
              if s!='':
                  frase.append(s)
          if frase and frase not in frasi:
            
               
             
            nestext=" ".join(frase).replace('\n',' ').strip()
   
          
            if len([i for i in mails_find if i is not None and i.strip()!=''])==0 :
             mails_find.append(self.extract_email(nestext.lower()))
             #name_find.append(mails_find[-1].split("@")[0])
            mail = [i for i in mails_find if i is not None and i.strip()!='']
            if len([i for i in address if i is not None and i.strip()!=''])==0:

             address.append(self.extract_address(nestext.lower(),frasi[-1]))
            if len([i for i in name_find if i is not None and i.strip()!=''])==0:
             name_find.append(self.extract_name(nestext.title()))
            if len([i for i in data_nascita if i is not None and i.strip()!=''])==0:
             data_nascita.append(self.extract_date(nestext.lower(),frasi[-1]))
            if len([i for i in name_find if i is not None and i.strip()!='']) == 0 and len(mail)>0:

                name_find.append(mail[0].split("@")[0])
                
               
            pattern = re.compile(r"[;,.] ")
            testo=[i.strip() for i in pattern.split(" ".join(frase))  if i != ' ' and i != '']
            frasi.extend(testo)
    resume_sections1 = []
    labelentity=[]
    entitydlete= ['CARDINAL', "PER",'EVENT', 'FAC','GPE','LAW','LOC', 'MONEY','NORP', #DATE
     'ORDINAL', 'ORG','PERCENT','PERSON', 'QUANTITY',
     'TIME','WORK_OF_ART']
    programmingskills=[]
  
    frasi=frasi[1:]
    for t in frasi:
         for s in self.namesprogramming:
                s = s.replace('+', ' plus').replace('++', 'plus').replace('(',' ').replace(')',' ').replace('* ',' ').replace('+2',' ').strip()
                span_list = [(match.start(), match.end()) for match in
                             re.finditer(fr"\b{s}\b", t)]
                if span_list  and s not in programmingskills and s not in ['y)','C','D','T','L','E','F','B','S'] :
                    skill=t[span_list[0][0]:span_list[0][1]]
                    if  skill not in self.stop and skill not in programmingskills:
                     programmingskills.append(s)
                     
         reg_pat = r'\S+@\S+\.\S+'
         mails =  " ".join(re.findall(reg_pat ,t,re.IGNORECASE))
         mails =  " ".join(re.findall(reg_pat ,t,re.IGNORECASE))
         result = [re.sub("(\\d|\\W)+", ' ',re.sub('http://\S+|https://\S+',"",   re.sub('\.(?!(\S[^. ])|\d)', '', x.lower().strip().replace('++', 'plus').replace('+', 'plus') )   ) ).strip() for x in t.split() if x not in string.punctuation  and x!=mails]
         testskill= " ".join(result).strip().lower()
         doc = self.nlpRemove(testskill)   
         ent =[(ent.text,ent.label_) for ent in doc.ents] # if ent.label_ not in entitydlete
         labelentity.append((testskill,ent))    
         if len(ent)>0:
          for ent in doc.ents:
              if ent.label_  in entitydlete:
                  # print( ent.label_,ent.text,testskill)
                  testskill=testskill.replace(ent.text,"").strip()
                  
          testskill=" ".join(testskill.split())      
    
         
         
         if testskill!='' and len(span_list)==0 and len(testskill)>1 and testskill not in self.stop:
            resume_sections1.append(testskill.lower())
    
    os.remove(fileHTML)
    print("END pdf_to_html")
   # print("programmingskills",programmingskills)

    return resume_sections1,programmingskills,address,mails_find,name_find,data_nascita

 
 






          
    










 







