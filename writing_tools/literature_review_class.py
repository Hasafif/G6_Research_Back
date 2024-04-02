# https://lukasschwab.me/arxiv.py/arxiv.html
# https://poe.com/chat/2t4f2epll96yl0li4gn
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import json
from ath.info import *
import re
from bs4 import BeautifulSoup
from pyzotero import zotero

# Dependency functions
##backoff & retry implementation for zotero requests
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def zoter_create(zot,template):
    resp = zot.create_items([template])
    return resp
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def zoter_retrieve(zot):
    resp = zot.items()
    return resp
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def zoter_delete(zot,z):
    resp = zot.delete_item(z)
    return resp
##backoff & retry implementation for gpt requests
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def gpt_request_retry(payload):
   response = requests.post(api_url, headers=header2, json=payload)
   return response
#function to add citation (,),[] in the correct position
def addcitation(message:str,citation:str,auth_name:str):
      pattern1 = fr"({auth_name +'.'})\'s\s*(\w+)"
      #pattern = fr"\b({auth_name})\b\'s\s*(\w+)"
      pattern2 = fr"({auth_name})\'s\s*(\w+)"
      match1 = re.search(pattern1, message)
      match2 = re.search(pattern2, message)
      if match1:
            message = re.sub(pattern1, rf"\1's \2 {citation}", message)
            return message
      elif match2:
               message = re.sub(pattern2, rf"\1's \2 {citation}", message)
               return message
           
      else:
           pos = message.find(auth_name)
           if pos != -1:
        # Find the position of the last space after the author's name
                   last_space_pos = pos +len(auth_name)
                   print(last_space_pos)
           else:
                return message
           if last_space_pos != -1:
            # Insert the text after the last space
                 message = message[:last_space_pos+1]+ citation+' '+message[last_space_pos+1:]
                 return message
           return message
##function to insert references list
def documentation(References,type):
      bib = ['References:']
      itemkeys = []
      zot = zotero.Zotero(library_id, library_type, zoter_api_key)
      print(zot)
      print(References)
      for i,entry in enumerate(References):
          template = zot.item_template('journalArticle')
          template['title'] = entry.title
          template['date'] = entry.publish_year
          template['url'] = entry.pdfUrl
         # Parsing Author names
          if len(entry.authors) == 1:
                template['creators'][0]['firstName'] = str(entry.authors[0]).split()[0]
                template['creators'][0]['lastName'] = str(entry.authors[0]).split()[1]
          else:
              au = []
              for h in entry.authors:
                 try:
                    n = {'creatorType': 'author', 'firstName': str(h).split()[0], 'lastName': str(h).split()[1]}
                    print(n)
                    au.append(n)
                 except:
                      continue
              try:
                   template['creators'] = au
              except Exception as e:
                   print(e)
                   itemkeys.append('not there')
                   continue
                   
              
          #template['creators']
          #resp = zot.create_items([template])
          try:
             resp = zoter_create(zot,template)
             itemkeys.append(resp['successful']['0']['key'])
             print(resp['successful']['0']['key'])
          except:
               itemkeys.append('not there')
               continue
        
          
          
      
      for i,entry in enumerate(itemkeys):
        zot.add_parameters(format='json',content= 'bib', itemKey=entry, style = type)
            #z = zot.items()
        print(zot)
        try:
            z = zoter_retrieve(zot)
            print(z)
            soup = BeautifulSoup(z[0], "html.parser")
            stripped_text = soup.get_text(separator=" ")
            if type =='ieee':
                   stripped_text = stripped_text.replace('[1]',f'[{i+1}]')
            elif type =='ama':
                 stripped_text = stripped_text.replace('1.',f'{i+1}'+'.')
            bib.append(stripped_text)
            # Delete the items
            zot.add_parameters(format='json', itemKey=entry)
            z = zoter_retrieve(zot)
            #print(z)
            z[0]['version'] =  zot.last_modified_version()
            z = zoter_delete(zot,z)
            print(z)
        except Exception as e:
                  print(e)
      bibstr = '\n'.join(bib)
      res = {'bib':bib,'bibstr':bibstr}
      return res
##function to extract year of publishing
def parse_year(d) -> int:
  d = str(d)
  return d.split()[0][0:4]


# Classes
#class for all refernces or papers
class Research:
   def __init__(self, title:str,authors:list, pdfUrl:str,abs:str,publish_year:str):
       self.title = title
       self.author_name = self.parse_author_name(authors)
       self.pdfUrl = pdfUrl 
       self.publish_year = publish_year
       self.authors = authors
       self.abstract = abs
   def parse_author_name(self,authors:list):
     
     if len(authors) == 1:
              author = str(authors[0]).split()[-1]
     else:
          au = str(authors[0]).split()[-1] 
          author = au + ' et al'
     return author



##literature_Review class
class Literature_Review:
  def __init__(self,Researches:list[Research],subject):
    self.subject = subject
    self.references = Researches
    self.research_count = len(Researches)
    self.authors = self.process_authors()['auth']
    self.publish_years = [obj.publish_year for obj in Researches]
    self.pdf_urls = [obj.pdfUrl for obj in Researches]
    self.titles = [obj.title for obj in Researches]
    self.abstracts = [obj.abstract for obj in Researches]
    self.raw_literature_reviews = self.generate_literature_review()
    self.full_literature_review = self.merge_and_rephrase()
    self.isCited = False
    self.isdocumented = False
  ##function to process author names to avoid repeated authors or citation errors
  def process_authors(self)->dict:
      auth = []
      chosed_authors = []
      print('m')
      for i,entry in enumerate(self.references):
          if len(entry.authors)==1:
                   a = entry.author_name
                   if a not in auth:
                           auth.append(a)
                           chosed_authors.append(i)
          else:
               for i,entry in enumerate(entry.authors):
                    au = str(entry).split()[-1] 
                    a = au + ' et al'
                    if a not in auth:
                         auth.append(a)
                         chosed_authors.append(i)
                         break
                    else:
                         continue
      a = {'auth':auth}
      print('m')
      return a
  ##function to parse refernces
  def list_researches(self) -> None:
    print(f"Researches Count:{self.research_count} \n")
    for i in range(0,self.research_count):
      r = f'[{i+1}] Title:{self.titles[i]}\n Authors:{self.authors[i]}\nURLs:{self.pdf_urls[i]}\nabstract:{self.abstracts[i]}\nPublish Year:{self.publish_years[i]}\n'
      print(r)
  ##function to summarize each article,then rephrasing via gpt prompts
  def generate_literature_review(self) -> list:
    lR  = []
    for i in range(0,len(self.references)):
      a = self.authors[i] 
      t = self.abstracts[i]
      payload = {
        'model': 'gpt-4',
        'messages': [
              {'role': 'system', 'content': 'You are a helpful assistant.'},
              {'role': 'user', 'content':f'Rephrase the following paragraph:\n{t} to include the author name:{a}'}
            ]
        }
        # First GPT-4 Request
      response = gpt_request_retry(payload)
        #response = requests.post(api_url, headers=header2, json=payload)
      print(response.json())
        # Parse the response
      data = response.json()
      message = data['choices'][0]['message']['content']  
        
      print(message)  
      lR.append(message)   
    return lR

  ##function to merge paragraphs,then rephrase in the appropriate way
  def merge_and_rephrase(self) -> str:
    m = '\n'.join(self.raw_literature_reviews)
    print(m)
    payload = {
              'model': 'gpt-4',
              'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content':f'merge and rephrase the following pharagraphs together as a literature review about {self.subject}:\n{m} , and also remember to use linking words "While", "However" and "Whereas", between each paragraph'}
        ]
        }
      # Second GPT-4 request 
    response = gpt_request_retry(payload)
    print(response.json())
    # Parse the response
    data = response.json()
    message = data['choices'][0]['message']['content']  
    print(message)
    return message
  ##function to add citations to the literature
  def add_citations(self,citation_type:str):
    # Adding citations to the literature review
    full_lr = self.full_literature_review
    print(full_lr)
    if not self.isCited:
      self.isCited = True
      for i,entry in enumerate(self.references):
          year = entry.publish_year # year of publish
          auth_name = self.authors[i] # author name case
          # Preparing citations
          if (citation_type=='mla'):
                  citation = f'({auth_name})'
          elif (citation_type=='ieee'):
                  citation = f'[{i+1}]'
          else:
                  citation = f'({auth_name}, {year})'
          if (auth_name == self.authors[i-1]):
                             break
          else:
                      pass
          full_lr = addcitation(message = full_lr,citation=citation,auth_name=auth_name)
      self.full_literature_review = full_lr
      print(full_lr)
      return full_lr
    else:
      return "This literature review is already cited!"
  ##function to add refernces list to the text 
  def add_references(self,type:str):
    lr = self.full_literature_review
    print(lr)
    if not self.isdocumented:
      self.isdocumented = True
      lr = self.full_literature_review
      ref = documentation(self.references,type)
      print(ref)
      for r in ref['bib']:
           lr = f'{lr}\n{r}\n'
      self.full_literature_review = lr
      return lr
    else:
      return "References are already loaded!"




  
