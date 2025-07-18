# ESXignite

## Prerequisites

Install python dependencies
```
pip3 install -r requirements.txt
```

Manually install pypykatz
```
git clone https://github.com/skelsec/pypykatz.git
pip3 install ./pypykatz/
```

Clone the pypykatz volatility plugin
```
git clone https://github.com/skelsec/pypykatz-volatility3.git
```

## Usage

```
      (        )                                 
      )\ )  ( /(                         )       
 (   (()/(  )\()) (   (  (        (   ( /(   (   
 )\   /(_))((_)\  )\  )\))(  (    )\  )\()) ))\  
((_) (_))  __((_)((_)((_))\  )\ )((_)(_))/ /((_) 
| __|/ __| \ \/ / (_) (()(_)_(_/( (_)| |_ (_))   
| _| \__ \  >  <  | |/ _` || ' \))| ||  _|/ -_)  
|___||___/ /_/\_\ |_|\__, ||_||_| |_| \__|\___|  
                     |___/ 
  
usage: ESXignite.py [-h] -t hostname -u user -p password -v vm_name

Create+extract the RAM of a running VM on an ESXi and extract it's secrets

options:
  -h, --help            show this help message and exit
  --target HOSTNAME, -t HOSTNAME
                        ESXi hostname/IP
  --username USERNAME, -u USERNAME
                        Username for ESXi SSH authication
  --password PASSWORD, -p PASSWORD
                        Password for ESXi SSH authentication
  --virtual-machine VM_NAME, -v VM_NAME
                        Virtual Machine name to dump secrets from
```
