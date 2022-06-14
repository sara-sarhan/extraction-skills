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
import numpy as np
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename,askdirectory 
import spacy

from dateparser.search import search_dates
from estraction_skills import ita_skills_formsentece,ita_estrcation_jobs, esxtractin_progra_skills,\
ita_skills_formsentece_no_fasttext
from spacy.lang.it.stop_words import STOP_WORDS as it_stop
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer


class FeatureExtraction:
    final_stopwords_list = list(it_stop)

    @staticmethod
    def TFIDF(scraped_data, cv):
        tfidf_vectorizer = TfidfVectorizer(stop_words=FeatureExtraction.final_stopwords_list)

        tfidf_jobid = tfidf_vectorizer.fit_transform(scraped_data)

        user_tfidf = tfidf_vectorizer.transform(cv)

        cos_similarity_tfidf = map(lambda x: cosine_similarity(user_tfidf, x), tfidf_jobid)

        output = list(cos_similarity_tfidf)
        return [ i[0][0] for  i in  output]

    @staticmethod
    def BOW(scraped_data, cv):
        count_vectorizer = CountVectorizer()

        count_jobid = count_vectorizer.fit_transform(scraped_data)

        user_count = count_vectorizer.transform(cv)
        cos_similarity_countv = map(lambda x: cosine_similarity(user_count, x), count_jobid)
        output = list(cos_similarity_countv)
        return output

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filePDF = askopenfilename() # show an "Open" dialog box and return the path to the selected file
# path = askdirectory() # show an "Open" dialog box and return the path to the selected file

nlp = spacy.load("en_core_web_sm")
print("START pdf_to_html")
with open('NomiCognomi.txt',encoding="utf8") as f:
    linesnames = [i.replace('\n',' ').title() for i in f.readlines() ]
def extract_name(text,linesnames):
   
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
      
def extract_address(text,last):
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
     # else:
        # for s in ['residenza','luogo di nascita','domicilio']:
                   
                 
        #             span_list = [(match.start(), match.end()) for match in
        #                          re.finditer(fr"\b{s}\b", last.title())]
        #             if span_list :
        #                 print(text)
        #                 return text
def extract_email(text):
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
def extract_date(text,last):
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
def convert(fname):
    pagenums = set();

    manager = PDFResourceManager()
    codec = 'utf-8'
    caching = True

    output = io.BytesIO()
    converter = HTMLConverter(manager, output, codec=codec, laparams=LAParams())

    interpreter = PDFPageInterpreter(manager, converter)
    infile = open(fname, 'rb')
    print("fname...", fname)
    for page in PDFPage.get_pages(infile, pagenums, caching=caching, check_extractable=False):
        interpreter.process_page(page)

    convertedPDF = output.getvalue()

    infile.close();
    converter.close();
    output.close()
    return convertedPDF






      
# pdf_files = [ os.path.join(path,f) for f in os.listdir(path) if f.endswith('pdf')]
# for filePDF in pdf_files :
path=os.getcwd()
fileHTML = os.path.join(path,filePDF+'dOPUT.html')

convertedPDF = convert( filePDF)
fileConverted = open(fileHTML, "wb")
fileConverted.write(convertedPDF)
fileConverted.close()
tipojob = []
index=-1
import fitz # install using: pip install PyMuPDF
import  fasttext

model = fasttext.load_model(os.path.join(os.getcwd(), 'code_solo_ita',"model", 'cc.it.300.bin'))
all_skills=[]
nlp_date=[]

from utils import extraxtinfo
from spacy.matcher import Matcher
nlpRemove = spacy.load("it_core_news_lg")
matcher = Matcher(nlpRemove.vocab)
address=[]
mails_find=[]
name_find=[]
data_nascita=[]
with open(fileHTML, 'r',encoding='utf8') as f:
    contents = f.read()
    soup = BeautifulSoup(contents, 'lxml')
    h4s = soup.find_all('div')
    frasiesperienza=['0']
    data=[]
    frasi=[]
    for h4 in h4s:
      frase=[]
      for sentece in h4.find_all("span"):
          s=sentece.text.strip()
          if s!='':
              frase.append(s)



      if frase and frase not in frasiesperienza  :


           nestext=" ".join(frase).replace('\n',' ').strip()
           print(nestext)
           if len([i for i in mails_find if i is not None and i.strip()!=''])==0 :
            mails_find.append(extract_email(nestext.lower()))
            #name_find.append(mails_find[-1].split("@")[0])
           mail = [i for i in mails_find if i is not None and i.strip()!='']
           if len([i for i in address if i is not None and i.strip()!=''])==0:

            address.append(extract_address(nestext.lower(),frasiesperienza[-1]))
           if len([i for i in name_find if i is not None and i.strip()!=''])==0:
            name_find.append(extract_name(nestext.title(),linesnames))
           if len([i for i in data_nascita if i is not None and i.strip()!=''])==0:
            data_nascita.append(extract_date(nestext.lower(),frasiesperienza[-1]))
           if len([i for i in name_find if i is not None and i.strip()!='']) == 0 and len(mail)>0:

               name_find.append(mail[0].split("@")[0])
           frasiesperienza.append(" ".join(frase))
           index+=1
           pattern = re.compile(r"[;,.] ")
           testo=[re.sub(r'[^\w\s]', '', i.strip().lower()) for i in pattern.split(" ".join(frase))  if  re.sub(r'[^\w\s]', '', i.strip()) != '']

           frasi.extend(testo)

           string = " ".join(frase).lower().strip()
           string=string.replace("  ", " ").replace('‘','')
           prog=esxtractin_progra_skills(string)
           if prog  :
            all_skills.extend(prog )






           # solo date mm/dd/yy o con -'(\d{1,4}([.\-/])\d{1,2}([.\-/])\d{1,4})

           # solo date mm/dd/ o con -  (\d{1,4}([.\-/])\d{1,2}\d{1,4})

           # assieme '(\d{1,4}([.\-/])\d{1,2}([.\-/])\d{1,4})|(\d{1,2}([.\-/])\d{1,4})'
           if   'data di nascita' not in frasiesperienza[index-1].strip().lower() \
               and 'sesso' not in string \
                and 'europass'not in string and 'ufficio di collocamento ' not in string \
            and 'nome' not in string  and 'dati personali' not in string  \
            and string not in tipojob and 'data di nascita' not in string \
            and 'pagina'not in string   and   'autorizzo il trattamento' not in string  \
                and 'consenso  al trattamento' not in string  and 'hrs' not in string and\
                    'curriculum vitae ' not in string  and\
                'dell’ar' not in string and \
              'dall’art.'not in string  and 'decreto legge' not in string \
                    and ' tel.' not in string and 'cellulare' not in string   \
            and 'patente'not in string  and 'nascita' not in string   and 'd.lg' not in string \
                and '© unione europea' not in string and 'curriculum vitae'  not in string  :


               matches =  search_dates(string, settings={"STRICT_PARSING": True,'PARSERS':  ['timestamp', 'absolute-time'],}, languages=['it', 'en'])
               if matches and string not in tipojob:

                       tipojob.append(string)
                       data.append((index," ".join(frase).lower().strip()))
                       print('match...........',string )
               # print(string)
               if string not in tipojob:
                    x = re.findall(r'((\b(0|[0-12][0-9])([\-/–])\d{1,2}[0-12]\b)([\-/–])\d{1,4})|(\b(0|[0-12][0-9])([\-/])\d{2,4})|(\b\d{1,4}(\s[-/–]*)(0|[0-12][0-9])(oggi|attuale|in corso|presente|present, fino al)\b)|(\b\d{4}([-–])\d{4})|(\b\d{4}(\s[-–]*)\s\d{4})|(\b\d{4}(\s[al]*)\s\d{4})|(\b\d{1,4}([-/–]*)(0|[0-12][0-9])(oggi|attuale|in corso|presente|present)\b)|(\b\d{1,4}([-/–]*)(oggi|attuale|in corso|presente|present)\b)|((\b\d{1,4}([-/– ]*)(oggi|attuale|in corso|presente|present))\b)(\d{1,4}([.\-/])\d{1,2}([.\-/])\d{1,4})', string,re.DOTALL)
                    if x and string not in tipojob:
                      print('new_string',index,x,string)
                      tipojob.append(" ".join(frase).lower().strip())
                      data.append((index," ".join(frase).lower().strip()))

                    y = re.findall(r'(\d{1,4}\s)(February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sept|September|Oct|October|Nov|November|Dec|December|gennaio|gen.|gen.|febbraio|feb|feb.|mar|mar.|marzo|aprile|apr|apr.|mag.|mag|maggio|giu|giu.|giugno|luglio|lug.|lug|agosto|ago.|ago|set|set.|settembre|ott.|ott|ottobre|nov.|nov|novembre|dicembre|dic.|dic)'
                                 , string)
                    if y and string not in tipojob :
                      print('new_string 2',y,index,string)
                      tipojob.append(" ".join(frase).lower().strip())
                      data.append((index," ".join(frase).lower().strip()))

                    z = re.findall(r'((\b(February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sept|September|Oct|October|Nov|November|Dec|December|gennaio|gen|febbraio|feb|mar|marzo|aprile|apr|mag|maggio|giu|giugno|luglio|lug|agosto|ago|set|settembre|ott|ottobre|nov|novembre|dicembre|dic)(\s\d{1,4}))) |(\b(February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sept|September|Oct|October|Nov|November|Dec|December|gennaio|gen|febbraio|feb|mar|marzo|aprile|apr|mag|maggio|giu|giugno|luglio|lug|agosto|ago|set|settembre|ott|ottobre|nov|novembre|dicembre|dic) (\d{1,4}))', string)

                    if z and string not in tipojob :
                        print('new_string 3',index,z,string)
                        tipojob.append(" ".join(frase).lower().strip())
                        data.append((index," ".join(frase).lower().strip()))


os.remove(fileHTML)
print("END pdf_to_html")
skills=ita_skills_formsentece(frasi,model)
address_=[i for i in [address+["non trovati"]][0]  if i!='' and i is not None][0]
mails_=[i for i in [mails_find+["non trovati"]][0]  if i!='' and i is not None][0]
name_=[i for i in [name_find+["non trovati"]][0] if i!='' and i is not None][0]
data_=[i for i in [data_nascita+["non trovati"]][0] if i!='' and i is not None][0]

df0 = pd.DataFrame({'nome e cognome':[name_],'residenza o domicilio': [address_],'mails':[mails_],'data nascita':data_})
print("0info persoali,",mails_,name_,data_,address_)

all_skills=list(set(all_skills))
test=[]
skills=[]
job=[]
inedx=0
frasiesperienza=frasiesperienza[1:]
    # salto l'utima data
while inedx+1< len(data) :
    string=",".join(frasiesperienza[data[inedx][0]:data[inedx+1][0]  ]).lower().strip() # len(string.split())>2   and
    string_list=string.split()[0:10]
    if'data di nascita' not in string_list  and ( ( ('© unione europea' not in string_list \
        and 'd.lg' not in string_list and 'europass' not in string_list)) ):
      test.append(string.replace('\n',' '))
      print("strat string............")
      new_string = re.sub(r'[^\w\s]', ' ', string).replace('\n',' ')
      jobs=ita_estrcation_jobs(new_string)

      # skills_find=[i for i in all_skills[data[inedx][0]:data[inedx+1][0]  ] if i.strip()!='']



      category=jobs

      # skills.append(skills_find)
      job.append(category)
      print("ennd string............")
      # print(inedx,string)
    inedx+=1

if data[inedx][0] +4 <len(frasiesperienza) and 'data di nascita' not in ",".join(frasiesperienza[data[inedx][0]:data[inedx][0] +4 ]).lower().strip()  \
    and 'dell’art.'  not in ",".join(frasiesperienza[data[inedx][0]:data[inedx][0] +4 ]).lower().strip()  and '© unione europea' not in ",".join(frasiesperienza[data[inedx][0]:data[inedx][0] +4 ]).lower().strip() \
    and 'd.lg' not in ",".join(frasiesperienza[data[inedx][0]:data[inedx][0] +4 ]).lower().strip() and 'europass' not in ",".join(frasiesperienza[data[inedx][0]:data[inedx][0] +4 ]).lower().strip(): #and len(data[inedx][1].split())>=2  :
    test.append(",".join(frasiesperienza[data[inedx][0]:data[inedx][0] +4 ]).lower().strip().replace('\n',' '))

    new_string = re.sub(r'[^\w\s]', '', ",".join(frasiesperienza[data[inedx][0]:data[inedx][0] +4 ]).lower().strip() )
    jobs=ita_estrcation_jobs(new_string)

    # skills_find=[i for i in all_skills[data[inedx][0]:data[inedx][0] +4 ] if i.strip()!='']



    category=jobs

    # skills.append(skills_find)
    job.append(category)
else:
 if  'dell’art.'  not in frasiesperienza[data[inedx][0]] and 'data di nascita' not in frasiesperienza[data[inedx][0]] and '© unione europea' not in  frasiesperienza[data[inedx][0]] \
and 'd.lg' not in frasiesperienza[data[inedx][0]] \
and 'europass' not in frasiesperienza[data[inedx][0]]:
     test.append(frasiesperienza[data[inedx][0]].lower().strip().replace('\n',' '))
     new_string = re.sub(r'[^\w\s]', '', frasiesperienza[data[inedx][0]].lower().strip())
     jobs=ita_estrcation_jobs(new_string)

     # skills_find=[i for i in all_skills[data[inedx][0]] if i.strip()!='']



     category=jobs

     # skills.append(skills_find)
     job.append(category)

name=filePDF.replace("pdf",'xlsx')

df = pd.DataFrame({'name': test,'jobTitke':job})



with pd.ExcelWriter(name, engine='xlsxwriter') as writer1:
# df.to_excel(name,index=False)
 df.to_excel(writer1, sheet_name='job titles', index=False)
 df0.to_excel(writer1, sheet_name='informazioni personali', index=False)
 df1 = pd.DataFrame({"allskills":all_skills})

 df1.dropna(subset=['allskills'], inplace=True)

 filter = df1["allskills"] != ""
 dfNew = df1[filter]
 dfNew.to_excel(writer1, sheet_name='allskills', index=False)
writer1.save()
from utils.cross_functions import CrossFunctions
from utils.job_posts_processing import JobPostsProcessing
from utils.read_cv import ReadCV
preprocessing = JobPostsProcessing()
it_job_posts = preprocessing.processed_dataset
it_job_posts['jobTitle']=it_job_posts['jobTitle'].apply(lambda  x:re.sub(r'[^\w\s]', '',x).strip().lower() )
description=it_job_posts['jobDescription'].tolist()
senteces=[]
for sentece  in description:
    soup = BeautifulSoup(sentece)
    pattern = re.compile(r"[;.] ")
    lista= [frase for frase in [BeautifulSoup(_,'html.parser').text.strip()  for _ in str(soup).split('<br/>')] if frase!='' and  len(frase.split())>2]
    testo=[re.sub(r'[^\w\s]', '', i.strip().lower()) for frase in lista for i in pattern.split("".join(frase))  if  re.sub(r'[^\w\s]', '', i.strip()) != '']

    senteces.append(  testo  )

it_job_posts["Domain"] = it_job_posts[['jobDescription',"jobTitle"]].apply(lambda x: ", ".join(x), axis =1)
frasi1=it_job_posts['Domain'].tolist()
print("info persoali.........",mails_,name_,data_,address_)
# # skills_jobpost=[]
# # for index,testo in  enumerate(senteces):
   
# #     skills_jobpost.append(",".join(ita_skills_formsentece_no_fasttext(testo,model))+ ",".join(esxtractin_progra_skills(".".join(testo))) )
# #     print(index)
# # ideale sarebbe usare fasstex come abbaimo fatto per cercare i lavori vicini skills vs skills valore più alto 

# rs = pd.DataFrame(columns=['job user', 'jobID', 'jobTitle', 'jobLocation', 'jobDescription',
#         'jobSalary', 'jobIndustry', 'jobSector', 'score', 'jobCompany'])

# rs = pd.DataFrame(columns=['jobID','job user','jobTitle', 'score', 'jobCompany'])

# # 
# for experience,text in zip(job,test):
#     if len(experience)>0 and ",".join(experience) not in ['corso formazione','corso', 'attestato conseguito','stage','laurea','facolatà','facolata','scuola','università','liceo','diploma','dottorato','master','istituto technico']:
   
#         scoreDomin=  np.array(FeatureExtraction.TFIDF(it_job_posts['jobTitle'].tolist(), [",".join(experience)]))
#         # scoreDomin = (scoreDomin1 - scoreDomin1.min())/ (scoreDomin1.max() - scoreDomin1.min())
        
#         # per ogni job post:  max( [frasi di un job post] vs tutte skills+ frase-iesima cv for frase-iesima  in listafrasi_jdi_un_jobpost) cosi ho uno score per ogni job post ( formato da frasi )
#         # 
#         score_skills=  np.array([ max(FeatureExtraction.TFIDF(i, [",".join(all_skills).replace('\n','')+t for t in text.split(',')]))  for i in senteces])
#         # score_skills = (score_skills1 - score_skills1.min())/ (score_skills1.max() - score_skills1.min())
#         output_tfidf =0.6*scoreDomin+float(0.4)*np.array(score_skills)
#         top = sorted(range(len(output_tfidf)), key=lambda i: output_tfidf[i], reverse=True)[:3]
#         list_scores = [output_tfidf[i] for i in top]
#         rs=rs.append( CrossFunctions.get_recommendation(top, it_job_posts, list_scores,experience))
#         print(rs)
  