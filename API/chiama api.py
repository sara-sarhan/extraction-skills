import requests
import requests

url = "http://127.0.0.1:8051//fileupload"

payload={}
files=[
  ('file',('cuoco.pdf',open('/C:/Users/sarhan.CORP/Documents/KEREZU/CODE SERVIZI PYTHON/code skill from cv/cuoco.pdf','rb'),'application/pdf')),
  ('file',('Meccanico.pdf',open('/C:/Users/sarhan.CORP/Documents/KEREZU/CODE SERVIZI PYTHON/code skill from cv/Meccanico.pdf','rb'),'application/pdf'))
]
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)

## chima api lancia
url = "http://127.0.0.1:8051//fileupload"

payload={}
pathfile='C:/Users/sarhan.CORP/Documents/KEREZU/CODE SERVIZI PYTHON/code skill from cv/cuoco.pdf'
files=[
  ('file',('cuoco.pdf',open(pathfile,'rb'),'application/pdf'))
]
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)
print(response.status_code)

## chima api start 
url = "http://127.0.0.1:8051/services/start"

payload={}
headers = {}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

url = "http://127.0.0.1:8051/services/healtcheck/isalive"

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)