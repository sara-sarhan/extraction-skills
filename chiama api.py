import requests

url = "http://127.0.0.1:8051//fileupload"

payload={}
pathfile='C:/Users/sarhan.CORP/Documents/KEREZU/CODE SERVIZI PYTHON/code skill from cv/cuoco.pdf'
files=[
  ('file',('cuoco.pdf',open(pathfile,'rb'),'application/pdf'))
]
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)