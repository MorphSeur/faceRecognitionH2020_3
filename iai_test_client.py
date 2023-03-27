# -*- coding: utf-8 -*-
import os
import requests
from argparse import ArgumentParser
from flask import Flask
from cryptography.fernet import Fernet

# request_body = {
#   "session_id": "SESSION_ID_PLACEHOLDER", 
#   "iai_datalake": "IAI_DATALAKE_PLACEHOLDER", 
#   "iai_datacipher": "base64", 
#   "iai_datakey": None, 
#   "iai_files": ["IAI_FILE_PLACEHOLDER.dpo"], 
#   "on_finish_url": "ON_FINISH_URL_PLACEHOLDER", 
#   "iai_params": {}, 
#   "iai_dpo_metadata": [
#     {
#       "id": "IAI_FILE_ID_PLACEHOLDER", 
#       "dsa_id": "IAI_FILE_DSA_ID_PLACEHOLDER", 
#       "start_time": "IAI_FILE_START_TIME_PLACEHOLDER",
#       "end_time": "IAI_FILE_END_TIME_PLACEHOLDER", 
#       "event_type": "IAI_FILE_EVENT_TYPE_PLACEHOLDER",
#       "organization": "IAI_FILE_ORGANIZATION_PLACEHOLDER",
#       "file:extension": "IAI_FILE_FILE_EXTENSION_PLACEHOLDER",
#       }
#   ]
# }

request_body = {
       "session_id":"32f6fd1e-3b51-41e5-863a-c42ff0c0675f",
       "iai_datalake":"./tmp/testiai",
       "iai_datacipher":"base64",
       "iai_datakey":None,
       "iai_files":[
          "1659113580288-6919f8c9-bfe0-481b-aa14-6e63295d06c9.dpo",
          "1659113547023-a9046ece-50fb-4765-b0ef-a2a9dec2e701.dpo"
       ],
       "on_finish_url":"http://tomcat:8080/iai-api/_analyticsCallback/32f6fd1e-3b51-41e5-863a-c42ff0c0675f",
       "iai_params":{
          
       },
       "iai_dpo_metadata":[
          {
             "id":"1659113547023-a9046ece-50fb-4765-b0ef-a2a9dec2e702",
             "dsa_id":"DSA-26e30e52-18b5-4feb-9281-7af3962d97ce",
             "start_time":"2022-07-29T18:52:52Z",
             "end_time":"2022-07-29T19:52:52Z",
             "event_type":"_facerecognition",
             "organization":"CNR",
             "file:extension":"png"
          },
          {
             "id":"1659113547023-a9046ece-50fb-4765-b0ef-a2a9dec2e701",
             "dsa_id":"DSA-26e30e52-18b5-4feb-9281-7af3962d97ce",
             "start_time":"2022-07-29T18:52:09Z",
             "end_time":"2022-07-29T19:52:09Z",
             "event_type":"_facerecognition",
             "organization":"CNR",
             "file:extension":"png"
          }
       ]
    }

cback_app = Flask(__name__)

@cback_app.route('/callback')
def callback():
  print("Callback received!!!")

def send_start(args):
  url = "{}/startAnalytics".format(args.target)
 
  payload = dict(
    session_id=request_body["session_id"],
    iai_datalake=request_body["iai_datalake"],
    iai_datacipher=request_body["iai_datacipher"],
    iai_datakey=request_body["iai_datakey"],
    iai_files=request_body["iai_files"],
    on_finish_url=None,
    iai_params=request_body["iai_params"],
    iai_dpo_metadata=request_body["iai_dpo_metadata"]
    )

  if request_body["iai_datakey"] is not None:
    encfilenames = encrypt_datalake(payload["iai_datakey"], payload["iai_datalake"], payload["iai_files"])
    payload["iai_files"] = encfilenames

  ret = requests.post(url, json=payload)
  print("Server response: [status={}, body={}]".format(ret.status_code, ret.json() if ret.status_code == 200 else ret.content.decode('UTF-8')))

def send_stop(args):
  url = "{}/stopAnalytics".format(args.target)

  ret = requests.put(url, params={'session_id': args.session_id})
  print("Server response: [status={}, body={}]".format(ret.status_code, ret.json() if ret.status_code == 200 else ret.content.decode('UTF-8')))


def encrypt_datalake(key, datalake_dir, files):
  """
  Encrypts the files provided in datalake in order to be used in IAI agent

  Parameters:
  key The key to use for encrypt files
  datalake_dir Directory of the datalake
  files array of filenames to use in analytics

  Return: Encryption key
  """
  f = Fernet(key)
  print("== Prepare datalake ==")

  for filename in files:
    print("- encrypt: {}...".format(filename))
    with open(os.path.join(datalake_dir, filename), 'rb') as fin:
      with open(os.path.join(datalake_dir, filename + '.enc'), 'wb') as fout:
        fout.write(f.encrypt(fin.read()))

  encfilenames = [fname + '.enc' for fname in files]

  return encfilenames


def main():
  p = ArgumentParser()
  p.add_argument('--target', '-t', default='http://localhost:5000', help="Address where iai agent server is running")
  
  subparsers = p.add_subparsers(help='Available action', dest='action')
  p_start = subparsers.add_parser('start')

  p_stop = subparsers.add_parser('stop')
  p_stop.add_argument('--session-id', default='1234')

  args = p.parse_args()

  if args.action == 'start':
    send_start(args)
  elif args.action == 'stop':
    send_stop(args)


if __name__ == '__main__':
  main()
