import os.path
import sys
from internetarchive import files, upload, get_files, get_item

### CONFIG FILES ###
dir = 'Folder Name'    # The directory of files to upload.
identifier = 'Identifier'           # The IA identifier to upload to.
subfolder = ''                                  # specifiy a folder within the item to upload to. Leave blank to upload to root item folder.
acceptedtypes = [".mp3", ".jpg"]        # The extension of files to be uploaded.
acceptedtypesglob = ["*.mp3", "*.jpg"] # The extension of files to be uploaded, * is needed for glob patterns below.
### CONFIG FILES ###

if os.path.isdir(dir) == False:
    sys.exit(f"{dir} is not a valid dir, exiting.")
else:
    os.chdir(dir)

if len(identifier) < 8:
    sys.exit("Identifier appears to be too short")
elif "/" in identifier:
    sys.exit("Illegal character in identifier, is this a directory?")
else:
    print (f"Working directory is: '{os.getcwd()}' and identifier is: '{identifier}'")

# Build a local list of files in the folder matching the filetypes type we want.
localfilelist = []
for filename in next(os.walk(os.getcwd()))[2]:
    if os.path.getsize(filename) > 100:
        if filename.endswith(tuple(acceptedtypes)):
            localfilelist.append(filename)  
sortedfilelist = sorted(localfilelist, key=lambda t: os.stat(t).st_mtime) # Sort files so we upload the oldest ones first.

filelistwithdir = []
for i in range(len(sortedfilelist)):
    filelistwithdir.append(os.path.join(subfolder, sortedfilelist[i]))
#print(filelistwithdir)
    
# Get list of files from IA and compare locally, to determine if file has already been uploaded. Exit if ia list returns nothing.
ialist = [iafile.name for iafile in get_files(identifier, glob_pattern=acceptedtypesglob)]
print (ialist)
if not ialist:
    sys.exit("No files detected on IA. There may be an issue with the IA or this is a new identifier. Exiting.")
else: print("List of files currently on IA: " + str(ialist).strip('[]'))

filestoupload = []
for filename in filelistwithdir:
    if filename in ialist:
        print (f"{filename} is already on IA.")
    if filename not in ialist:
        print (f"{filename} is not on IA.")
        filestoupload.append(filename)

# If file is not on IA let's upload it...
if not filestoupload:
    sys.exit("Nothing to upload.")
else:
    print("Preparing to upload: " + str(filestoupload).strip('[]'))

if subfolder:
    os.chdir('..')
    print("Jumping up a directory to upload subfolder contents.")

if not subfolder:
    upload(identifier, filestoupload, verbose=True, verify=True, retries=100, retries_sleep=10)
elif subfolder:
    for file in filestoupload:
        try: 
            upload(identifier, files = {file: file}, verbose=True, verify=True, retries=100, retries_sleep=10, queue_derive=False)
        except Exception as exception:
            print(exception)
            get_item(identifier).derive
            sys.exit("Exception occurred. Running derive and exiting.")

    print (f"Done uploading, running derive.")
    get_item(identifier).derive

print("Finished. If any errors persisted wait until the item derive has completed before trying again.")
