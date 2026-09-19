import http.client, json
conn = http.client.HTTPConnection('127.0.0.1', 8000)
payload = json.dumps({'email':'ali@example.com','password':'StrongP@ssw0rd'})
headers = {'Content-Type':'application/json'}
conn.request('POST','/api/auth/register',body=payload,headers=headers)
res = conn.getresponse()
print(res.status, res.reason)
print(res.read().decode())
