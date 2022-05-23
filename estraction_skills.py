from pdfminer.layout import LTTextContainer
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
import docx
   



def word_Sentece(pdfnamepath,stop,nlpRemove,namesprogramming):
   
    doc = docx.Document(pdfnamepath)
    frasiall = [p.text for p in doc.paragraphs if p.text.strip()!='']
    
  
    frasi=[]

    for sentece in frasiall :
             
     
               pattern = re.compile(r"[;,.] ")
               testo=[i.strip() for i in pattern.split(sentece)  if i != ' ' and i != '']
               frasi.extend(testo)
    resume_sections1 = []
    labelentity=[]
    entitydlete= ['CARDINAL','DATE', "PER",'EVENT', 'FAC','GPE','LAW','LOC', 'MONEY','NORP',
     'ORDINAL', 'ORG','PERCENT','PERSON', 'QUANTITY',
     'TIME','WORK_OF_ART']
    programmingskills=[]

    for t in frasi:
         for s in namesprogramming:
                s = s.replace('+', ' plus').replace('++', 'plus').replace('(',' ').replace(')',' ').replace('* ',' ').replace('+2',' ').strip()
                span_list = [(match.start(), match.end()) for match in
                             re.finditer(fr"\b{s}\b", t)]
                if span_list  and s not in programmingskills and s not in ['y)','C','D','T','L','E','F','B','S'] :
                    skill=t[span_list[0][0]:span_list[0][1]]
                    if  skill not in stop and skill not in programmingskills:
                     programmingskills.append(s)
                     
         reg_pat = r'\S+@\S+\.\S+'
         mails =  " ".join(re.findall(reg_pat ,t,re.IGNORECASE))
         mails =  " ".join(re.findall(reg_pat ,t,re.IGNORECASE))
         result = [re.sub("(\\d|\\W)+", ' ',re.sub('http://\S+|https://\S+',"",   re.sub('\.(?!(\S[^. ])|\d)', '', x.lower().strip().replace('++', 'plus').replace('+', 'plus') )   ) ).strip() for x in t.split() if x not in string.punctuation  and x!=mails]
         testskill= " ".join(result).strip().lower()
         doc = nlpRemove(testskill)   
         ent =[(ent.text,ent.label_) for ent in doc.ents] # if ent.label_ not in entitydlete
         labelentity.append((testskill,ent))    
         if len(ent)>0:
          for ent in doc.ents:
              if ent.label_  in entitydlete:
                  # print( ent.label_,ent.text,testskill)
                  testskill=testskill.replace(ent.text,"").strip()
                  
          testskill=" ".join(testskill.split())      
    
         
         
         if testskill!='' and len(span_list)==0 and len(testskill)>1 and testskill not in stop:
            resume_sections1.append(testskill.lower())
    
 
    print("programmingskills",programmingskills)
    return resume_sections1,programmingskills
def convert(fname):
    pagenums = set();
    
    manager = PDFResourceManager()
    codec = 'utf-8'
    caching = True
 
  
    output = io.BytesIO()
    converter = HTMLConverter(manager, output, codec=codec, laparams=LAParams())
 
    interpreter = PDFPageInterpreter(manager, converter)  
    infile = open(fname, 'rb')
    print("fname...",fname)
    for page in PDFPage.get_pages(infile, pagenums,caching=caching, check_extractable=False):
        interpreter.process_page(page)
 
    convertedPDF = output.getvalue()  
 
    infile.close(); converter.close(); output.close()
    return convertedPDF






          
    






def ner(pdfnamepath):

    # Output directory
    from spacy.lang.en.stop_words import STOP_WORDS
    stops = spacy.lang.en.stop_words.STOP_WORDS
    nlp = spacy.load("en_core_web_sm", disable=['parser', 'tagger', 'ner'])
    nlp_remove = spacy.load("en_core_web_sm")
    skills = pd.read_csv("skills.csv", encoding='utf-8')
    prog=list(skills.columns)
    filename = os.path.join(os.getcwd(), 'programming-languages-corrected.csv')
    dffull = pd.read_csv(filename,sep=';', encoding = "ISO-8859-1")
    with open('skills_cv.txt') as f:
         skills_cv = f.read().splitlines() 
    namesprogramming=list(set(dffull['ï»¿name'].tolist()+prog+skills_cv)) 
    for i in ['y)','C','D','T','L','E','F','B','S']:
       namesprogramming.remove(i)
    
    occupation_en = pd.read_csv("occupations_en.csv", encoding='utf-8')
    titles_eng= pd.read_csv("job_skills.csv", encoding='utf-8') 
    listjob1= occupation_en['preferredLabel'].unique().tolist()+occupation_en['altLabels'].unique().tolist()
    lista=list(set([word[0:word.find(',')].replace('(','').replace(')','').lower().strip() for word in set(titles_eng['Category'].unique().tolist()+titles_eng['Title'].unique().tolist()) if len(word[0:word.find(',')])>4]))
    listjob1=list(set(listjob1 +lista))
    listjob1.extend(['developer'])
  
    listjob2=[]
    for job in listjob1:
      if type(job)!=float:
        if "/" in job:
            jobs=job.split("/")
            
            listjob2.extend(jobs)
        else:
            listjob2.append(job)
    listjob=[]
    for job in listjob2:
      if type(job)!=float:

        if "\n" in job:
              jobs=job.split("\n")
           
              listjob.extend(jobs)
        else:
            listjob.append(job)      
    listsentece,programmingskills=pdf_to_html(pdfnamepath,stops,nlp_remove,namesprogramming) 
    listjob=[ i.strip().replace('(','').replace(')','') for i in set(listjob +lista) if len(i)>4]
    listjob.remove("product")
    tipojob= extractjobb(listsentece,stops,listjob)
    
  
    
 
    category=tipojob[0]
    output_dir=os.path.join(os.getcwd(),"model")

    nlp = spacy.load(output_dir)
    skills_ner = []
    for paragraph in listsentece:

        sentences = paragraph.split(".")

        for sent in sentences:

            for s in namesprogramming:
                s=s.replace('++','+').replace('(','').replace(')','')
                span_list = [(match.start(), match.end()) for match in
                             re.finditer(fr"\b{s}\b", sent, re.IGNORECASE)]
                if  span_list:
                    skills_ner.append(s)
                    # print(s, sent)

            doc = nlp(sent)
            for ent in doc.ents:
                # displacy.render(doc, style="ent", jupyter=True, options=options)
                # print(ent.text, ent.label_)
                skills_ner.append(ent.text.lower())




    return skills_ner,tipojob


def pdf_to_html(pdfnamepath,stop,nlpRemove,namesprogramming):
    print("START pdf_to_html")
    filePDF = pdfnamepath #("input directory; your pdf file:   ")
    path=os.getcwd() 
    fileHTML = os.path.join(path,'dOPUT.html')
    convertedPDF = convert( filePDF)
    fileConverted = open(fileHTML, "wb")
    fileConverted.write(convertedPDF)
    fileConverted.close()
    with open(fileHTML, 'r',encoding='utf8') as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'lxml')
        h4s = soup.find_all('div')
        frasi=[]
        for h4 in h4s:
          frase=[]
          for sentece in h4.find_all("span"):
              s=sentece.text.strip()
              if s!='':
                  frase.append(s)
          if frase and frase not in frasi:
               pattern = re.compile(r"[;,.] ")
               testo=[i.strip() for i in pattern.split(" ".join(frase))  if i != ' ' and i != '']
               frasi.extend(testo)
    resume_sections1 = []
    labelentity=[]
    entitydlete= ['CARDINAL','DATE', "PER",'EVENT', 'FAC','GPE','LAW','LOC', 'MONEY','NORP',
     'ORDINAL', 'ORG','PERCENT','PERSON', 'QUANTITY',
     'TIME','WORK_OF_ART']
    programmingskills=[]
    namesprogramming.remove('p')
    namesprogramming.remove('J')
    namesprogramming.remove('G')
    namesprogramming.remove('es')
    namesprogramming.remove('FL')
    namesprogramming.remove('Io')
    namesprogramming.remove('K')

    for t in frasi:
         for s in namesprogramming:
                s = s.replace('+', ' plus').replace('++', 'plus').replace('(',' ').replace(')',' ').replace('* ',' ').replace('+2',' ').strip()
                span_list = [(match.start(), match.end()) for match in
                             re.finditer(fr"\b{s}\b", t)]
                if span_list  and s not in programmingskills and s not in ['y)','C','D','T','L','E','F','B','S'] :
                    skill=t[span_list[0][0]:span_list[0][1]]
                    if  skill not in stop and skill not in programmingskills:
                     programmingskills.append(s)
                     
         reg_pat = r'\S+@\S+\.\S+'
         mails =  " ".join(re.findall(reg_pat ,t,re.IGNORECASE))
         mails =  " ".join(re.findall(reg_pat ,t,re.IGNORECASE))
         result = [re.sub("(\\d|\\W)+", ' ',re.sub('http://\S+|https://\S+',"",   re.sub('\.(?!(\S[^. ])|\d)', '', x.lower().strip().replace('++', 'plus').replace('+', 'plus') )   ) ).strip() for x in t.split() if x not in string.punctuation  and x!=mails]
         testskill= " ".join(result).strip().lower()
         doc = nlpRemove(testskill)   
         ent =[(ent.text,ent.label_) for ent in doc.ents] # if ent.label_ not in entitydlete
         labelentity.append((testskill,ent))    
         if len(ent)>0:
          for ent in doc.ents:
              if ent.label_  in entitydlete:
                  # print( ent.label_,ent.text,testskill)
                  testskill=testskill.replace(ent.text,"").strip()
                  
          testskill=" ".join(testskill.split())      
    
         
         
         if testskill!='' and len(span_list)==0 and len(testskill)>1 and testskill not in stop:
            resume_sections1.append(testskill.lower())
    
    os.remove(fileHTML)
    print("END pdf_to_html")
   # print("programmingskills",programmingskills)

    return resume_sections1,programmingskills

 
 


 


def extractjobb(resume_sections,stop,listjob)  :
    tipojob=[]
    print("START extractjobb")
    for testskill in resume_sections:
  
     
      
     if len(tipojob)<1:
      for idx,job in enumerate(listjob):
     
       
         span_list = [(match.start(), match.end()) for match in
                  re.finditer(fr"\b{job}\b",testskill )]
         if span_list :
             tipojob.append(job)

             break
    # conta=[ tipojob.count(i) for i in set(tipojob) ]  
    # labelpossible=[i for i in set(tipojob) if tipojob.count(i)==max(conta)]
    if len(tipojob)<1:
        for testskill in resume_sections:
      
         
         if len(tipojob)<1:
          for idx,job in enumerate(listjob):
             
           
             span_list=[i for i in set(job.split()).intersection(set(testskill.split()))   if i not in stop]    
             if span_list :
                 tipojob.append(job)

                 break
    print("END extractjobb")
    return tipojob
        
def extract_skills_npl(resume_sections,stop,namesprogramming,nlpRemove,listjob,listacompetenze,worddelete):
 words=[]        
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
      if len(span_list)>1:
             for i in range(len(span_list)-1):
                 skillfound=testskill[span_list[i][0]:span_list[i+1][0]]
                 skillmach.append(skillfound ) 
                
             if  skillfound.strip()!='' and skillfound not in stop and skillfound not in  skillmach and len(skillfound.split())>1 and skillfound not in worddelete:
                skillmach.append(skillfound ) #
      else:
         
          if testskill[span_list[0][0]:].strip()!='' and span_list and  testskill[span_list[0][0]:] not in stop and testskill not in  skillmach and len(testskill[span_list[0][0]:].split())>1 and testskill[span_list[0][0]:] not in worddelete:
             skillmach.append(testskill[span_list[0][0]:] ) #
 
  
  doc = nlpRemove(testskill) #clean_txt2(testskill,nlpRemove,stop)
  start=0
  end=0
  verb=[]
  sentece=[]
  endold=0
  oldtoken=''
  if doc:
      idx=0
      for token in doc:
        idx+=1  
        # print(token.pos_,token.text)
    
        if token.pos_ == "NOUN" or token.pos_ == "VERB" : #or token.pos_=='ADJ':
            start= token.idx  # Start position of token
            end = token.idx + len(token)  # End position 
          
            if token.pos_ == "VERB" : # or token.text in ["conoscenza","competenze","capacità"]:
               verb.append(token.pos_)
            
               # distanza verbo e noun poca al massimo tra verbo e parola ci può stara un adj oa o poco altro 
          
            if len(verb)>0  and   (-endold +start<= 3 or endold==0) :
                words.append((token.text, start, end, token.pos_,-endold +start))
                
                
                sentece.append( token.text ) # token.text
                
                endold= end
                oldtoken=token.pos_
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

def cosine_similarity(v1, v2):
     mag1 = np.linalg.norm(v1)
     mag2 = np.linalg.norm(v2)
     if (not mag1) or (not mag2):
         return 0
     return np.dot(v1, v2) / (mag1 * mag2)
 
def fasttext_skills(unionskills,uniqueskills,namesprogramming,model):
    print ("START fasttext_skills")
    candidate_skills_fasttext=[]
    candidate_skills_eco=[]
    for word  in unionskills:
        if len(word.split())<=3:
              threshold=0.75
        else:
            threshold=0.69
        resumes_clean_vec=model.get_sentence_vector(word)

        for idx,skills in enumerate(uniqueskills):  #[i for i in row['occupations_skillset'].split(',') ]:
              
               skills_vec=model.get_sentence_vector(skills)
               
               score_skill=cosine_similarity(skills_vec, resumes_clean_vec)
               
             
               if score_skill > threshold and word not in candidate_skills_fasttext:
                               print( 'word', word, 'skill', skills, score_skill)
                           
                               candidate_skills_fasttext.append(word)
                               candidate_skills_eco.append((skills,score_skill))
                               break
    print("END fasttext_skills")
    return  candidate_skills_fasttext,candidate_skills_eco




'''versione italiana'''
## italiano
def ita_skills(pdfnamepath,formato="pdf",pathmode=''):
    from spacy.lang.it.stop_words import STOP_WORDS
    stop = list(spacy.lang.it.stop_words.STOP_WORDS)
    stop.extend(['e','i'])
    skills = pd.read_csv("skills.csv", encoding='utf-8')
    prog=list(skills.columns)
    filename = os.path.join(os.getcwd(), 'programming-languages-corrected.csv')
    dffull = pd.read_csv(filename,sep=';', encoding = "ISO-8859-1")
    with open('skills_cv.txt') as f:
         skills_cv = f.read().splitlines() 
    namesprogramming=list(set(dffull['ï»¿name'].tolist()+prog+skills_cv)) 
    for i in ['y)','C','D','T','L','E','F','B','S']:
        namesprogramming.remove(i)
        
        
    full_occupations = pd.read_csv("occupation_full.csv", encoding='utf-8')
    occupation_it = pd.read_csv("occupations_it.csv", encoding='utf-8')
    titles_eng= pd.read_csv("job_skills.csv", encoding='utf-8') 
    listjob1= occupation_it['preferredLabel'].unique().tolist()+occupation_it['altLabels'].unique().tolist()
    listjob=[]
    for job in listjob1:
      if type(job)!=float:
        if "/" in job:
            jobs=job.split("/")
            
            listjob.extend(jobs)
        elif "\n" in job:
              jobs=job.split("\n")
           
              listjob.extend(jobs)
        else:
            listjob.append(job)
    with open('titoloLavori.txt') as f:
        contents = f.read().splitlines() 
        
    listjob.extend(contents)
    lista=list(set([word[0:word.find(',')].replace('(','').replace(')','').lower().strip() for word in set(titles_eng['Category'].unique().tolist()+titles_eng['Title'].unique().tolist()) if len(word[0:word.find(',')])>4]))
    listjob=list(set(listjob +lista))
    listjob.remove("console")
    listjob.sort() 
    
    
    full_occupations_skills = full_occupations[['essential_skills', 'optional_skills','isco_group']]
    full_occupations_skills['essential_skills'] = full_occupations_skills['essential_skills'].apply(lambda x: ','.join(str(x).split('; ')))
    full_occupations_skills['optional_skills'] = full_occupations_skills['optional_skills'].apply(lambda x: ','.join(str(x).split('; ')))
    
    full_occupations_skills_clean = pd.DataFrame({'occupations_skillset': full_occupations_skills['essential_skills']})
    l=[]
    spliskills=full_occupations_skills_clean['occupations_skillset'].str.split(',').tolist()
    l = [x.strip() for lista in spliskills for x in lista if x]
    namesprogramming.append('ibatis')
    namesprogramming.extend(["Eclipse", "Java" "J2EE", "HTML", "JSP"," JAX RPC", "JAXB", "CSS3", "JavaScript",  "jQuery", "Spring MVC", "Hibernate"," RESTful web services", "Apache Tomcat", "Cucumber", "Cassandra", "Junit", "Jenkins", "Maven", "GitHub", "XML", "Log4j", "EJB", "MySQL", "Ajax"])
    uniqueskills=list(set(l))
    nlpRemove = spacy.load("it_core_news_lg")
    if formato=="word":
        listsentece,programmingskillista=word_Sentece(pdfnamepath,stop,nlpRemove,namesprogramming)
    else:
      listsentece,programmingskills=pdf_to_html(pdfnamepath,stop,nlpRemove,namesprogramming)

    
    listacompetenze=['skills','addetto al','addetta al','specializzato in','specializzata in',"conoscenza","competenze","capacità",'predisposizione al',"specializzato nell","specializzata nell"]
    worddelete=['capacità e competenze personali','patente guida',"capacità di lettura  capacità di scrittura  capacità di espressione orale","capacità di lettura",  "capacità di scrittura", "capacità di espressione orale", 'capacità di','competenze personali','competenze informatiche','capacità e competenze informatiche','capacità e competenze']
    skills,skillmach=  extract_skills_npl(listsentece,stop,namesprogramming,nlpRemove,listjob,listacompetenze,worddelete)
    
    tipojob= extractjobb(listsentece,stop,listjob)
    print("tipojob",tipojob)
    if pathmode != '':
        print(pathmode)

        model = fasttext.load_model(pathmode)
    else:
        model = fasttext.load_model("cc.it.300.bin")

    candidate_skills_fasttext,candidate_skills_eco=fasttext_skills(skills,uniqueskills,namesprogramming,model)
    allskills=candidate_skills_fasttext+programmingskills+skillmach
    print([i for i in skills if i not in candidate_skills_fasttext])
    print(tipojob)
    return  allskills,tipojob

'''versione inglese'''
### inglsese 
def eng_skills(pdfnamepath,formato='pdf',pathmode=''):
    from spacy.lang.en.stop_words import STOP_WORDS
    stop = spacy.lang.en.stop_words.STOP_WORDS
    nlp = spacy.load("en_core_web_sm")
    skills = pd.read_csv("skills.csv", encoding='utf-8')
    prog=list(skills.columns)
    filename = os.path.join(os.getcwd(), 'programming-languages-corrected.csv')
    dffull = pd.read_csv(filename,sep=';', encoding = "ISO-8859-1")
    with open('skills_cv.txt') as f:
         skills_cv = f.read().splitlines() 
    namesprogramming=list(set(dffull['ï»¿name'].tolist()+prog+skills_cv)) 
    for i in ['y)','C','D','T','L','E','F','B','S']:
       namesprogramming.remove(i)
           
   
    namesprogramming.extend(["Eclipse", "Java" "J2EE", "HTML", "JSP"," JAX RPC", "JAXB", "CSS3", "JavaScript",  "jQuery", "Spring MVC", "Hibernate"," RESTful web services", "Apache Tomcat", "Cucumber", "Cassandra", "Junit", "Jenkins", "Maven", "GitHub", "XML", "Log4j", "EJB", "MySQL", "Ajax"])
    occupation_en = pd.read_csv("occupations_en.csv", encoding='utf-8')
    titles_eng= pd.read_csv("job_skills.csv", encoding='utf-8') 
    listjob1= occupation_en['preferredLabel'].unique().tolist()+occupation_en['altLabels'].unique().tolist()
    lista=list(set([word[0:word.find(',')].replace('(','').replace(')','').lower().strip() for word in set(titles_eng['Category'].unique().tolist()+titles_eng['Title'].unique().tolist()) if len(word[0:word.find(',')])>4]))
    listjob1=list(set(listjob1 +lista))
    listjob1.extend(['developer'])
     
    listjob2=[]
    for job in listjob1:
      if type(job)!=float:
        if "/" in job:
            jobs=job.split("/")
            
            listjob2.extend(jobs)
        else:
            listjob2.append(job)
    listjob=[]
    for job in listjob2:
      if type(job)!=float:
    
        if "\n" in job:
              jobs=job.split("\n")
           
              listjob.extend(jobs)
        else:
            listjob.append(job)  
    if formato=="word":
        listsentece1,programmingskillista=word_Sentece(pdfnamepath,stop,nlp,namesprogramming)
    else:
      listsentece1,programmingskills=pdf_to_html(pdfnamepath,stop,nlp,namesprogramming) 
    removesentece=['page', 'nationality', 'nationality', 'driving license', 'guide', 'b', 'curriculum', 'vitae', 'personal information', 'name', 'education', 'mother tongue',
           'surname', 'email', 'number', 'telephone', 'curriclum', 'vitae', 'curriclum',
           'e-mail', 'telephone', 'birth', 'address', 'personal data processing',
           'I authorize the', 'processing of personal data', 'signature', 'birth', 'main subjects studied',
           'pursuant to the legislative decree', 'residence', 'domicile', 'mobile', 'legislative decree',
           'pursuant to', 'personal protection material code', 'the undersigned expresses my consent so that the personal data provided can be treated with respect',
           'd.lgs.', 'data processing', 'personal European regulation', 'tel', 'institute', 'undersigned express consent',
           'the undersigned expresses consent for personal data provided',
           'sex', 'place of birth', 'birth', 'personal protection regulation matter code',
           'material code', 'personal protection regulation', 'information', 'pursuant to legislative decree', 'pursuant to legislative decree',
           'pursuant to legislative decree June n code for personal protection matters',
           'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'January', 'February', 'March', 'April',
           'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'personal data protection code',
           'master degree', 'three-year degree', 'doctorate', 'medium level', 'basic level', 'intermediate level', 'advanced level',
           'activity sector', 'professional training', 'thesis title', 'graduate', 'graduate']
     
    listsentece=[]
    
    for testskill in listsentece1:
          
            span_list = [(match.start(), match.end(),s,testskill) for s in removesentece for match in
                          re.finditer(fr"\b{s}\b", testskill.strip())]
            if testskill!='' and len(span_list)==0:
                listsentece.append(testskill.lower())
    
    listjob=[ i.strip().replace('(','').replace(')','') for i in set(listjob +lista) if len(i)>4]
    listjob.remove("product")
    tipojob= extractjobb(listsentece,stop,listjob)
    
    if pathmode!='':
        print(pathmode)
        
        model=fasttext.load_model( pathmode)
    else:
        model=fasttext.load_model( "cc.en.300.bin")
     
    listacompetenze=['skills','ability to','developmebt','ability in','ability of',"conoscenza","capability to","capability in",'capability of',"level in","level of"
                     ,"Know how in","Know how of","Know-how in","Know-how of","proficiency in",
                     "proficiency of","proficiency at"]
    worddelete=listacompetenze
    skills,skillmach=  extract_skills_npl(listsentece,stop,namesprogramming,nlp,listjob,listacompetenze,worddelete)
    
    tipojob= extractjobb(listsentece,stop,listjob)
    print("tipojob",tipojob)
    full_occupations = pd.read_csv("occupation_full_eng.csv", encoding='utf-8')
    full_occupations_skills = full_occupations[['essential_skills', 'optional_skills','isco_group']]
    full_occupations_skills['essential_skills'] = full_occupations_skills['essential_skills'].apply(lambda x: ','.join(str(x).split('; ')))
    full_occupations_skills['optional_skills'] = full_occupations_skills['optional_skills'].apply(lambda x: ','.join(str(x).split('; ')))
    
    full_occupations_skills_clean = pd.DataFrame({'occupations_skillset': full_occupations_skills['essential_skills']})
    l=[]
    spliskills=full_occupations_skills_clean['occupations_skillset'].str.split(',').tolist()
    l = [x.strip() for lista in spliskills for x in lista if x]

    uniqueskills=list(set(l))
    candidate_skills_fasttext,candidate_skills_eco=fasttext_skills(skills,uniqueskills,namesprogramming,model)
    
    allskills=candidate_skills_fasttext+programmingskills+skillmach
    print([i for i in skills if i not in candidate_skills_fasttext])
    print(tipojob)
    return  allskills,tipojob