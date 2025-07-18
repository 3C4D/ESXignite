import paramiko, scp 

def ssh_connect(hostname, username, password):
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(hostname=hostname, username=username, password=password)
  return ssh

def get_file(ssh, file):
  print(f'[+] Downloading file : {file}')
  fileshort = file.split('/')[-1]
  with scp.SCPClient(ssh.get_transport()) as client:
    client.get(file)
  print(f'[+] Memory dump successfully written at : ./{fileshort} !')