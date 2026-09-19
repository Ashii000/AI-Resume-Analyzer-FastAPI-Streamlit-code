import http.client, urllib.parse
conn = http.client.HTTPConnection('127.0.0.1', 8000)
params = urllib.parse.urlencode({'username':'ali@example.com','password':'StrongP@ssw0rd'})
headers = {'Content-Type':'application/x-www-form-urlencoded'}
conn.request('POST','/api/auth/login',body=params,headers=headers)
res = conn.getresponse()
print(res.status, res.reason)
print(res.read().decode())
