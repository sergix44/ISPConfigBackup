from time import gmtime, strftime
import os
import tempfile
import shutil
import subprocess
import sys

#######--CONFIG--#######
DB_USER = 'root'
DB_PASSWORD = 'root'
BACKUP_DIR = '/root/backups_ispconfig'
BACKUP_ROTATION = False
BACKUP_ROTATION_N = 5
DROPBOX_UPLOAD = False
DROPBOX_UPLOAD_ACCESSKEY = 'INSERT-ACCESSKEY-HERE'
########################

if DROPBOX_UPLOAD:
    try:
        import dropbox
    except:
        print('-- ERROR: Failed to import DropBox Library, make sure it is installed. (pip install dropbox)')
        sys.exit(1)

temp_folder = tempfile.mkdtemp(prefix='pyISPCbackup')
temp_folder_databases = '/databases/'
temp_folder_sites = '/sites/'

print(' * Fetching databases...')
databases = subprocess.check_output('mysql --user=' + DB_USER + ' --password=' + DB_PASSWORD + ' -e "SHOW DATABASES;" | tr -d "| " | grep -v Database', shell=True).split('\n')
databases = [x for x in databases if x]

print(' * Creating folders...')
os.mkdir(temp_folder + temp_folder_databases)
os.mkdir(temp_folder + temp_folder_sites)

print('-- Backup databases')
for db in databases:
    if db[0] == 'c':
        print(' * Saving ' + db + '...')
        os.system('mysqldump --user=' + DB_USER + ' --password=' + DB_PASSWORD + ' ' + db + ' > ' + temp_folder + temp_folder_databases + db + '.sql')

print('-- Backup sites')
sites = subprocess.check_output('ls /var/www/ | grep "\."', shell=True).split('\n')
sites = [x for x in sites if x]
for site in sites:
    if site.count('.') >= 2:
        continue
    print(' * Saving ' + site + '...')
    os.system('cp -Lr /var/www/' + site + ' ' + temp_folder + temp_folder_sites + site + '/')
    if os.path.isdir(temp_folder + temp_folder_sites + site + '/backup'):
        print(' * Removing old ' + site + ' saved backups...')
        shutil.rmtree(temp_folder + temp_folder_sites + site + '/backup')
    if os.path.isdir(temp_folder + temp_folder_sites + site + '/log'):
        print(' * Removing ' + site + ' logs...')
        shutil.rmtree(temp_folder + temp_folder_sites + site + '/log')

print('-- Compressing...')
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)
os.system('cd ' + temp_folder + ' && tar -zcf ' + BACKUP_DIR + '/ispconfig_' + strftime("%d-%m-%Y_%H:%M:%S", gmtime()) + '.tar.gz *')
backups_in_folder = sorted(os.listdir(BACKUP_DIR), key=lambda f: os.path.getctime("{}/{}".format(BACKUP_DIR, f)))

if DROPBOX_UPLOAD:
    print('-- Syncing with Dropbox...')
    try:
        dpclient = dropbox.Dropbox(DROPBOX_UPLOAD_ACCESSKEY)
        dpclient.files_upload(open(BACKUP_DIR + '/' + backups_in_folder[-1]), '/' + backups_in_folder[-1])
    except Exception, e:
        print('* ERROR:' + str(e))

if BACKUP_ROTATION:
    print('-- Backup rotation...')
    if len(backups_in_folder) > BACKUP_ROTATION_N:
        print('* Removing old backup from locally...')
        os.remove(BACKUP_DIR + '/' + backups_in_folder[0])
        if DROPBOX_UPLOAD:
            print('* Removing old backup from Dropbox...')
            try:
                dpclient.files_delete('/' + backups_in_folder[0])
            except Exception, e:
                print('* ERROR:' + str(e))

print(' * Removing temp files...')
shutil.rmtree(temp_folder)
print('-- Done.')
