import paramiko,os
client = paramiko.SSHClient()
client._policy = paramiko.WarningPolicy()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh_config = paramiko.SSHConfig()
user_config_file = os.path.expanduser("~/.ssh/config")
if os.path.exists(user_config_file):
    with open(user_config_file) as f:
        ssh_config.parse(f)

cfg={}
user_config = ssh_config.lookup('soumya')
cfg['hostname'] = user_config['hostname']
cfg['username'] = user_config['user']
cfg['port'] ='22'
cfg['sock'] = paramiko.ProxyCommand(user_config['proxycommand'])

client.connect(**cfg)

sftp = paramiko.SFTPClient.from_transport(client)

# Download
filepath = "/etc/passwd"
localpath = "/home/remotepasswd"
sftp.get(filepath,localpath)


# Close
if sftp: sftp.close()
if transport: transport.close()



# stdin, stdout, stderr = client.exec_command('tail /media/SOUMYA/KOUSHIK/mount/FH2_NEW/DIAB/UPDATED_SURF/RERUN/RSTAR_4.0_AD_DA/fort.24')

# print "stderr: ", stderr.readlines()
# print "pwd: ", stdout.readlines()




# import paramiko
# paramiko.util.log_to_file("paramiko.log")

# # Open a transport
# host,port = "example.com",22
# transport = paramiko.Transport((host,port))

# # Auth    
# username,password = "bar","foo"
# transport.connect(None,username,password)

# # Go!    
# sftp = paramiko.SFTPClient.from_transport(transport)

# # Download
# filepath = "/etc/passwd"
# localpath = "/home/remotepasswd"
# sftp.get(filepath,localpath)

# # Upload
# filepath = "/home/foo.jpg"
# localpath = "/home/pony.jpg"
# sftp.put(localpath,filepath)

# # Close
# if sftp: sftp.close()
# if transport: transport.close()