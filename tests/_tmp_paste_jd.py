import http.client, urllib.parse
conn = http.client.HTTPConnection('127.0.0.1', 8000)
params = urllib.parse.urlencode({'text':'We are looking for a Python developer with 5+ years of experience in FastAPI, SQLAlchemy, and cloud deployment. Responsibilities: build APIs, test, deploy. Degree: BSc or MSc in Computer Science.'})
headers = {'Content-Type':'application/x-www-form-urlencoded'}
conn.request('POST','/api/jobs/paste',body=params,headers=headers)
res = conn.getresponse()
print(res.status, res.reason)
print(res.read().decode())
