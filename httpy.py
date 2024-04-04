# Simple HTTP/HTTPS client that only uses built-in libraries. 
# Doesn't require pip, just drop-in-and-use

import http.client
import json
import time

def send_http_request(url, method = 'GET', headers = None, body_str = None, timeout_sec = None):
  is_https = False
  if url.startswith('https://'):
    url = url[len('https://'):]
    is_https = True
  elif url.startswith('http://'):
    url = url[len('http://'):]
  else:
    raise Exception("Need http:// or https:// protocol prefix")

  parts = url.split('/')
  domain = parts[0]
  path = '/' + '/'.join(parts[1:])
  parts = domain.split(':')
  if len(parts) == 2:
    domain = parts[0]
    port = int(parts[1])
  else:
    port = None # defaults based on protocol

  connection_ctor = http.client.HTTPSConnection if is_https else http.client.HTTPConnection

  con = connection_ctor(domain, timeout = timeout_sec, port = port)
  start = time.time()
  con.connect()
  end = time.time()
  epsilon = 0.01

  # TODO: There is a more robust way to do this. Please look it up.
  if timeout_sec != None and end - start > timeout_sec - epsilon:
    return {
      'status': 0,
      'contentType': 'text/plain',
      'isJson': False,
      'body': 'Timeout',
      'isTimeout': True,
    }

  if headers == None:
    headers = { }

  con.request(method, path, body_str, headers)
  res = con.getresponse()

  out_headers = {}
  out_headers_flat = {}
  easy_lookup = {}
  for k in res.headers.keys():
    out_headers[k] = list(res.headers.get_all(k))
    out_headers_flat[k] = out_headers[k][-1]
    easy_lookup[k.lower()] = out_headers_flat[k]
  content_type = easy_lookup.get('content-type')

  body = res.read().decode('utf-8')
  is_json = 'application/json' in content_type
  json_body = None
  try:
    json_body = json.loads(body) if is_json else None
  except:
    pass

  return {
    'status': res.status,
    'headersMultimap': out_headers,
    'headers': out_headers_flat,
    'contentType': content_type,
    'body': body,
    'isJson': is_json,
    'bodyJson': json_body,
    'isTimeout': False,
  }

def send_json_post_request(url, data, timeout_sec = None, user_agent = None):
  headers = { 'Content-Type': 'application/json' }
  if user_agent != None:
    headers['User-Agent'] = user_agent
  return send_http_request(url, 'POST', headers, json.dumps(data))
