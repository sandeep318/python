import os 
import tarfile 
import re
import sys
import subprocess
import datetime
import pysftp



########################################    
# Remote sftp server Connection Details.
########################################

SFTP_HOST = 'hostname of remote server'       
SFTP_USER = 'root'
SFTP_PASSWD = 'rootpassword of remote server'
SFTP_DIR = '/backup/'
SFTP_PORT = '22'



timestamp=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
Temp_Location='/tmp/backup/'
if not os.path.exists('/tmp/backup'):
    os.makedirs('/tmp/backup')
def database_parse(Doc_root):
    
    os.chdir(Doc_root)


    with open('wp-config.php','r') as fh:
        file=fh.read()
    password_search=r'\s+?define\(\'DB_PASSWORD\',\s+?\'(.*)\'\);'
    database_search=r'\s+?define\(\'DB_NAME\',\s+?\'(.*)\'\);'
    user_search=r'\s+?define\(\'DB_USER\',\s+?\'(.*)\'\);'
    host_search=r'\s+?define\(\'DB_HOST\',\s+?\'(.*)\'\);'
    database=re.search(database_search,file).group(1)
    user=re.search(user_search,file).group(1)
    password=re.search(password_search,file).group(1)
    hostname=re.search(host_search,file).group(1)
    Db_details={'DATABASE':database,'PASSWORD':password,'USER':user,'HOST':hostname}
    return Db_details
     

def database_backup(Db_Dict):
    db=Db_Dict['DATABASE']
    db_user=Db_Dict['USER']
    db_password=Db_Dict['PASSWORD']
    db_host=Db_Dict['HOST']
    db_backup_path=Temp_Location+db+'-'+timestamp+'.sql'
    command='mysqldump -h '+db_host+' -u '+db_user+' -p'+db_password+' '+db+' >'+ Temp_Location+db+'-'+timestamp+'.sql'
    subprocess.call(command,shell=True)
    return db_backup_path
    

def wordpress_backup(Doc_root,dumpfile ):
        
            
            root=os.path.dirname(Doc_root)
            folder=os.path.basename(Doc_root)
            os.chdir(Doc_root)
            Temp_File=Temp_Location+folder+'-'+timestamp+'.tar.gz'
            if os.path.exists(Temp_File):
                print('removing ', Temp_File,end='')
                os.remove(Temp_File)
                print(': success')
            
            os.chdir(root)
            print('taking the backup of ' + Temp_File,end='')
            with tarfile.open(Temp_File,'w:gz') as archive:
                archive.add(folder,recursive=True)
                archive.add(dumpfile,arcname="database.sql")
            print(': success')
            return(Temp_File)
        
def filetransfer(Temp_File):
    with pysftp.Connection(SFTP_HOST,username=SFTP_USER,password=SFTP_PASSWD,port=int(SFTP_PORT)) as sftp:
        with sftp.cd(SFTP_DIR):           # temporarily chdir to public
            sftp.put(Temp_File)  # upload file to public/ on remote
    
        
Doc_root=input('enter the abs path of wordpress installation: ')
if Doc_root and os.path.exists(Doc_root):
        Doc_root=os.path.normpath(Doc_root)
        os.chdir(Doc_root)
        if 'wp-config.php' not in os.listdir():
            print('wp-config.php not exist')
            sys.exit(0)
        Db_Dict=database_parse(Doc_root)
        dumpfile=database_backup(Db_Dict)
        Temp_File=wordpress_backup(Doc_root,dumpfile)
        filetransfer(Temp_File)
        
else:
    print('path not exists')
    sys.exit(0)
    

