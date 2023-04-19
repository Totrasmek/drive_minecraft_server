# For google drive access:
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
# For running server commands and file zipping
import os
# For zipping world files for upload
from zipfile import ZipFile
import urllib.request

world_file_name = 'world_data.zip'
original_directory = os.getcwd()
server_directory = 'java_server'
drive_folder_id = '1oNYDKZX0lE0hPmRp9PLM0Mp545plJvXo'

# Zips the world data files and uploads the .zip
# code from https://www.geeksforgeeks.org/working-zip-files-python/
def zipWorld():
	print('Preparing local world files for upload')
  
	# calling function to get all file paths in the directory
	file_paths,zip_names = get_all_file_paths('./'+server_directory)
  
	# writing files to a zipfile
	with ZipFile(world_file_name,'w') as zip_file:
		# writing each file one by one
		for file,zip_name in zip(file_paths,zip_names):
			zip_file.write(file,zip_name)

# Unzips the world data files into the minecraft server directory
# code from https://www.geeksforgeeks.org/working-zip-files-python/
def unzipWorld():
	print('Preparing minecraft server world data')
	# opening the zip file in READ mode
	with ZipFile(world_file_name, 'r') as zip:
		# printing all the contents of the zip file
		zip.printdir()
	  
		# extracting all the files
		zip.extractall(path='./'+server_directory)

# code from https://www.geeksforgeeks.org/working-zip-files-python/ 
def get_all_file_paths(directory):

	# Specify minecraft server files and directories that do not contain world data
	ignore = ["versions","server.jar","libraries","logs"]

	# initializing empty file paths and archive names list
	file_paths = []
	zip_names = []
  
	# crawling through directory and subdirectories
	for root, directories, files in os.walk(directory):
		for filename in files:
			# join the two strings in order to form the full filepath.
			filepath = os.path.join(root, filename)
			
			# add filepaths and archive names that are not on the ignore list
			# archive names don't have the \mserver root directory
			paths=filepath.split("\\")
			if paths[1] not in ignore:
				zip_name = '\\'.join(paths[1:])
				file_paths.append(filepath)
				zip_names.append(zip_name)
  
	# returning all file paths
	return file_paths,zip_names

# Downloads the world file from the goole drive world folder
def downloadWorld(drive,file_id):

	if file_id == None:
		print('WARNING: No existing world data in google drive to download. Contact the group chat, work out who played last, and put the world file back on the drive manually! Exiting...')
		exit()
	else:
		gfile = drive.CreateFile({'id':file_id})
		
	print('Downloading world file. Any local zipped world data will be overwritten. Sorry :3')
	gfile.GetContentFile(world_file_name)

# Uploads the world file to the google drive world folder
def uploadWorld(drive,file_id):
	
	if file_id == None:
		print('WARNING: No existing world data in google drive. How could this happen if we downloaded it earlier? Make sure no one is deleting files in the drive folder. Continuing to upload new world file to google drive.')
		gfile = drive.CreateFile({'parents': [{'id': drive_folder_id}]})
	else:
		gfile = drive.CreateFile({'id':file_id})
		
	print('Uploading world file. Any google drive world data will be overwritten. Sorry :3')
	gfile.SetContentFile(world_file_name)
	gfile.Upload()
	
# Given an authenticated google drive object, finds the id of the first file in the google drive world folder with the name of the world file
def findWorldFileID(drive):

	# code from https://github.com/googlearchive/PyDrive/issues/117
	file_list = drive.ListFile({'q':"'"+drive_folder_id+"' in parents and trashed=False"}).GetList()
	
	file_id = None
	
	for file in file_list:
		if file['title'] == world_file_name:
			print('Identified world file in Google Drive')
			file_id = file['id']
			break
	
	return file_id


# Authenticates a connection with the Google Drive API. On first run, mycreds.txt will not exist and the user's browser will prompt them to authorise the app. On future runs, mycreds.txt should have been created so that it is a silent process.
def getDriveConnection():

	gauth = GoogleAuth()  

	# code below from https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process
	# Try to load saved client credentials
	gauth.LoadCredentialsFile("mycreds.txt")
	if gauth.credentials is None:
		# Authenticate if they're not there
		gauth.LocalWebserverAuth()
	elif gauth.access_token_expired:
		# Refresh them if expired
		gauth.Refresh()
	else:
		# Initialize the saved creds
		gauth.Authorize()
	# Save the current credentials to a file
	gauth.SaveCredentialsFile("mycreds.txt")

	return GoogleDrive(gauth)  

def getProgramMode():
	print("Type 1 + enter to download the latest world from drive\n" \
		 +"Type 2 + enter to upload your local world to drive\n" \
		 +"Type 3 + enter to start the server\n" \
		 +"Type 4 + enter to exit this program\n" )
	mode = input()
	if mode != '1' and mode != '2' and mode != '3' and mode != '4':
		return getProgramMode()
	else:
		return int(mode)
		
def get_download_link():
#concept stolen from https://stackoverflow.com/questions/70746779/python-requests-get-doesnt-return-anything
    download_url = None;

    import requests
    webpage_url = "https://www.minecraft.net/en-us/download/server"
    
    header_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"
    #header details stolen from https://www.whatismybrowser.com/guides/the-latest-user-agent/edge
    session = requests.Session()
    session.headers.update({"User-Agent":header_agent})
    response = session.get(webpage_url, timeout=2).text

    
    try:
        start_text_to_match = "https://piston-data.mojang.com/"
        end_text_to_match = "server.jar"
    
        url_start_index = response.index(start_text_to_match)
        url_end_index = response[url_start_index:-1].index(end_text_to_match)+len(end_text_to_match)+url_start_index

        download_url = response[url_start_index:url_end_index]
        
        print('URL for server.jar download is:\n'+download_url)
        
    except ValueError:
        print('!!!!!!\nCouldn''t locate link to download server.jar in html at\n'+webpage_url+'\n!!!!!!')
        exit()
        
    return download_url
        
def getJar():
	if os.path.isfile(original_directory+'/'+server_directory+'/server.jar'):
		print("No server.jar download required")
	else:
		os.chdir(original_directory+'/'+server_directory+'/')
		print("Downloading server.jar ...")
		urllib.request.urlretrieve(get_download_link(), "server.jar")
		os.chdir(original_directory)
		
FREEDNS_URL = 'http://freedns.afraid.org/dynamic/update.php?'
OLDIP_FILE = original_directory + '/oldip.txt'
USER_KEYS = ["SnluVEw3VElwR3VwTlV4VjRuZkxjQVFEOjIwOTMyMTM1"]

def updatedns(ip):
    for key in USER_KEYS:
        print(urllib.request.urlopen(FREEDNS_URL+key).read().strip().decode("utf-8"))

    f = open(OLDIP_FILE, 'w')
    f.write(ip.decode("utf-8"))
    f.close()

def updateIP():
	newip = urllib.request.urlopen("http://ip.dnsexit.com/").read().strip()

	if not os.path.exists(OLDIP_FILE):
		updatedns(newip)
	else:
		f = open(OLDIP_FILE, 'r')
		oldip = f.read()
		f.close()
		if oldip != newip:
			updatedns(newip)
			
# Runs the minecraft server
def runServer():
	print('Updating IP on FreeDNS')
	updateIP()
	print('Running the minecraft server.')
	server_command = 'java -Xmx1024M -Xms1024M -jar server.jar nogui'
	os.chdir(original_directory+'/'+server_directory+'/')
	os.system(server_command)
	os.chdir(original_directory)

def main():
	if not os.path.exists(os.path.join(original_directory,server_directory)): 
		os.mkdir(os.path.join(original_directory,server_directory))
	getJar()
	while True:
		mode = getProgramMode()
	  
		if mode == 1:
			print('Downloading latest world')
			drive = getDriveConnection()
			file_id = findWorldFileID(drive)
			downloadWorld(drive,file_id)
			unzipWorld()
		elif mode == 2:
			print('Uploading your local world')
			zipWorld()
			drive = getDriveConnection()
			file_id = findWorldFileID(drive)
			uploadWorld(drive,file_id)
		elif mode == 3:
			print('Running the server')
			runServer()
		elif mode == 4:
			print('Exiting')
			exit()
		else:
			print('Bad program mode.')
	exit()

if __name__ == "__main__":
	main()
	
