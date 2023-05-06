# References:
# https://www.codedonut.com/raspberry-pi/mount-network-share-raspberry-pi/
# https://www.blog.pythonlibrary.org/2012/07/19/python-101-downloading-a-file-with-ftplib/
# https://www.thepythoncode.com/article/list-files-and-directories-in-ftp-server-in-python


# Need to mount drive:
# cd to parent directory of nas folder
# sudo mount -t cifs -o username=admin,password=password1 //10.0.0.1/USB_Storage nas
# sudo mount -t cifs -o / nas
# sudo mount /media/pi/TOSHIBA nas
import os
import sys, time, ftplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ftplib import FTP, error_perm
from credentials import server_email_address, server_email_password, recipients, ftp_host, ftp_user, ftp_password
# from pathlib import Path


def checkInternetSocket(host="8.8.8.8", port=53, timeout=3):
    import socket
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


def get_folder(path):
	folder = path.split('/')[-1]
	print(f'folder {folder}')
	return folder


def ftp0(base_path_local, base_path_remote):
	if not os.path.exists(base_path_local):
		os.makedirs(base_path_local)
	start = time.time()
	os.chdir(base_path_local)
	ftp(base_path_local, base_path_remote, '')


def ftp(local, remote, path):
	f = None
	try:
		start = time.time()
		print(ftp_host)
		f = FTP(ftp_host)
		login_code = f.login(user=ftp_user, passwd=ftp_password)
		login_code = login_code.split()
		login_code = login_code[0]
		download(f, local, remote)
		f.quit()

	except Exception as e:
		print('Exception ', e)

	finally:
		print( '.', end='' )


def download(f, local, remote):
	# print(f'local = {local}')
	# print(f'remote= {remote}')
	f.cwd(remote)
	print(remote)
	for remote_entry in f.mlsd():
		remote_entry_name = remote_entry[0]
		print(f'{remote_entry_name}')
		if remote_entry_name == '.':
			continue

		if remote_entry_name == '..':
			continue

		if remote_entry_name.startswith('.'):
			print(f'Delete {remote_entry_name}')
			f.delete(remote_entry_name)
			continue

		try:
			if remote_entry[1]["type"] == "dir":
				local_list = [ entry.name for entry in os.scandir()]
				if not remote_entry_name in local_list:
					print(f'create local dir --> {remote_entry_name}')
					os.mkdir(remote_entry_name)
				f.cwd(remote_entry_name)
				os.chdir(remote_entry_name)
				local = os.getcwd()
				time.sleep( 1 )
				download(f, local, f.pwd() )

				recursed_dir = f.pwd()
				f.cwd('../')
				# print('81')
				# f.rmd(recursed_dir)	Only remove if previous day.
				f.rmd( get_folder(recursed_dir) )
				os.chdir('../')


			else:
				print('remote file --> ', remote_entry_name)
				print('ftp ', f.pwd() )
				print(f'local = {local}')
				print(f'remote= {remote}')
				lf = open(remote_entry_name, "wb")
				f.retrbinary("RETR " + remote_entry_name, lf.write, 8*1024)
				lf.close()
				f.delete(remote_entry_name)


		except Exception as e:
			print('Exception', e)
			print(remote_entry_name)
			return


base_path_local = '/Users/samsuper/Desktop/nas'
base_path_remote = '/bayrvs/blackhawk/reolink'
while True:
	if checkInternetSocket():
		ftp0(base_path_local, base_path_remote)
	time.sleep(60)	
