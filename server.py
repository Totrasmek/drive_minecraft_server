# For google drive access:
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
# For running server commands and file zipping
import os
# For zipping world files for upload
from zipfile import ZipFile

world_file_name = 'world_data.zip'
server_directory = 'java_server'
drive_folder_id = '1oNYDKZX0lE0hPmRp9PLM0Mp545plJvXo'

# Runs the minecraft server
def runServer():
	print('Running the minecraft server.')
	
	server_command = 'java -Xmx1024M -Xms1024M -jar server.jar nogui'
	original_directory = os.getcwd()
	os.chdir(original_directory+'/'+server_directory+'/')
	os.system(server_command)
	os.chdir(original_directory)

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
		
	print('Downloading world file. Any local world data will be overwritten. Sorry :3')
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
	print("Type 1 + enter use the latest world from google drive\n" \
		 +"Type 2 + enter to use your local world and after play your local world will still update google drive\n" \
		 +"Type 3 + enter to use your local world with no google drive interaction")
	mode = input()
	print(mode)
	print(type(mode))
	if mode != '1' and mode != '2' and mode != '3':
		return getProgramMode()
	else:
		return int(mode)

def main():

	mode = getProgramMode()
	
	if mode == 1:
		print('mode 1')
		drive = getDriveConnection()
		file_id = findWorldFileID(drive)
		downloadWorld(drive,file_id)
		unzipWorld()
		runServer()
		zipWorld()
		file_id = findWorldFileID(drive)
		uploadWorld(drive,file_id)
	elif mode == 2:
		print('mode 2')
		runServer()
		zipWorld()
		drive = getDriveConnection()
		file_id = findWorldFileID(drive)
		uploadWorld(drive,file_id)
	elif mode == 3:
		print('mode 3')
		runServer()
	else:
		print('Bad program mode.')
	
	exit()

if __name__ == "__main__":
	main()