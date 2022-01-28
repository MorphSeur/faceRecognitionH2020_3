# -*- coding: utf-8 -*-
import os
import requests
from argparse import ArgumentParser
from flask import Flask, jsonify, request
from cryptography.fernet import Fernet

cback_app = Flask(__name__)

@cback_app.route('/callback')
def callback():
  print("Callback received!!!")

def send_start(args):
  url = "{}/startAnalytics".format(args.target)

  payload = dict(
    session_id=args.session_id,
    iai_datalake=args.datalake,
    iai_datacipher=args.datacipher,
    iai_datakey=args.datakey,
    iai_files=args.files,
    on_finish_url=None)
    
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
  print("== Preparing datalake ==")

  for filename in files:
    print("- encrypt: {}...".format(filename))

    plain_file = os.path.join(datalake_dir, filename)
    enc_file = os.path.join(datalake_dir, filename + '.enc')

    with open(plain_file, 'rb') as fin:
      with open(enc_file, 'wb') as fout:
        fout.write(f.encrypt(fin.read()))

  encfilenames = [fname + '.enc' for fname in files]
  return encfilenames


def main():
  p = ArgumentParser()
  p.add_argument('--target', '-t', default='http://localhost:5000', help="Address where iai agent server is running")
  subparsers = p.add_subparsers(help='Available action', dest='action')
  p_start = subparsers.add_parser('start')
  p_start.add_argument('--datalake', '-dl', required=True)
  p_start.add_argument('--datakey', default=Fernet.generate_key().decode('ASCII'))
  p_start.add_argument('--datacipher', default="AES128-CBC")
  p_start.add_argument('--session-id', default='1234')
  p_start.add_argument('files', nargs='+')

  p_stop = subparsers.add_parser('stop')
  p_stop.add_argument('--session-id', default='1234')

  args = p.parse_args()

  if args.action == 'start':
    encfilenames = encrypt_datalake(args.datakey, args.datalake, args.files)
    args.files = encfilenames
    send_start(args)
  elif args.action == 'stop':
    send_stop(args)


if __name__ == '__main__':
  main()
