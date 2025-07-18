from utils import random_string, waiting
import re

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

def find_vm_snapshot(ssh, vm_name, vm_folder, snapshot_id):
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