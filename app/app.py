import time, datetime, os, uuid, json
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from python_json_config import ConfigBuilder

x = datetime.datetime.now()
print(x)

builder = ConfigBuilder()
dir_path = os.path.dirname(os.path.realpath(__file__))
config = builder.parse_config(dir_path + '/' + "config.json")

local_path = config.outputDirectory
connect_str = config.azure.blobStorageConnectionString
blob_service_client = ""

def initClient():
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

def createContainer(container_name):
    print("Creating " + container_name + "...")
    blob_service_client.create_container(container_name)
    print("Azure Blob storage account created " + container_name)

def generateDate():
    timestr = time.strftime("%Y%m%d%H%M%S")
    return timestr

def takePhoto(image_path):
    image_filename = image_path + "image%s.jpg"%(generateDate())
    print("Saving photo as " +image_filename)
    command = "raspistill -vf -o {0} -n --exposure auto".format(image_filename)
    os.system(command)

def uploadSingleFileToStorage(container_name,upload_file_path,upload_filename):
    print("Uploading " + upload_file_path + upload_filename + " to " + container_name)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=upload_filename)

    with open(upload_file_path, "rb") as data:
        blob_client.upload_blob(data)
    print("Upload complete")

def startLoop(image_path,frames):
    interval = 60
    frameCount = 0

    while frameCount < frames:
        takePhoto(image_path)
        frameCount += 1
        time.sleep(interval)

def createVideo():
    list_filename = local_path + "stills.txt"
    video_filename = generateDate() + ".avi"
    video_path = local_path + video_filename

    os.system("ls {0}*.jpg > {1}".format(local_path,list_filename))

    print("Saving " + video_filename)
    os.system("mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 -vf scale=1920:1080 -o {0} -mf type=jpeg:fps=24 mf://@{1}".format(video_path,list_filename))
    return video_filename

try:
    #initClient()
    startLoop(local_path, 1440)
    video_filename = createVideo()
    containerName = "stills-" + generateDate()

    #createContainer(containerName)
    #uploadSingleFileToStorage(containerName,local_path+video_filename,video_filename)

except Exception as ex:
    print('Exception:')
    print(ex)