import time

from pydroid_ipcam import *
import aiohttp
import asyncio
import sys
from thingin.thingin_requests import *
import uuid
import platform
import os
import json

update_frequency = 30


hue_url= "https://192.168.1.47/api/75WMpeSrs1ogZ6kxD79ez-fseyPxaCNkt-r8YL1z/lights/1/state"

print("###########################")
print("Program arguments : ")
for arg in sys.argv:
    print(arg)

token = sys.argv[1]
domain_to_insert = sys.argv[2]
name = sys.argv[3]
ip_local = sys.argv[4]
camuser = sys.argv[5]
campwd = sys.argv[6]
print("###########################")
my_uuid = uuid.uuid3(namespace=uuid.NAMESPACE_DNS, name=name)


if platform.system() == "Windows":
    thingindir = os.getcwd()+"\\thingin\\"
else:
    thingindir = os.getcwd()+"/thingin/"

boostrap_data_file = open(thingindir+'boostrap_result.json', 'r')
boostrap_data = json.load(boostrap_data_file)
print("Updating existing data :")
print(boostrap_data)
luminance_uuid = ""
motion_uuid = ""


async def main():
    async with aiohttp.ClientSession() as client:
        cam = PyDroidIPCam(websession=client, host=ip_local, username=camuser, password=campwd, port=8080, ssl=False)

        while(True):
            time.sleep(update_frequency)
            await cam.update()
            try:
                print_data(cam)
                update_data(cam)
            except Exception as e:
                print(e)


def print_data(cam):
    print("Camera availability ", cam.available)
    print("Enabled sensors ", cam.enabled_sensors)
    try:
        print("Motion events ", cam.sensor_data["motion_event"])
    except Exception:
        print("No motion sensor, ignoring")
    try:
        print("Luminance Value ", cam.sensor_data["light"])
    except Exception:
        print("No light sensor, ignoring")
    try:
        print("Torch status ", cam.status_data["curvals"]["torch"])
    except Exception:
        print("No access to torch status, ignoring")

def update_data(cam):
    try:
        motion_update_result = put_motion_event_thingin(uuid=motion_uuid, iri=motion_iri, motion_data=cam.sensor_data["motion_event"], access_token=token)
        print("Motion data update result: ", motion_update_result)
    except Exception:
        print("failed to send motion sensor information, maybe not available")
    try:
        luminance_update_result = put_luminance_thingin(uuid=luminance_uuid, iri=luminance_iri, luminance_data=cam.sensor_data["light"], access_token=token)
        print("Luminance data update: ", luminance_update_result)
    except Exception:
        print("failed to send light sensor information, maybe not available")




# ##BOOTSTRAP DATA UUIDS LOADING FROM THINGIN RESPONSE"
luminance_iri = domain_to_insert+"androidIPCam.luminance-"+str(my_uuid)
motion_iri = domain_to_insert+"androidIPCam.movementDetection-"+str(my_uuid)
for node in boostrap_data:
    if node["iri"] == luminance_iri:
        luminance_uuid = node["uuid"]
    if node["iri"] == motion_iri:
        motion_uuid = node["uuid"]

# MAIN LOOP
loop = asyncio.get_event_loop()
loop.run_until_complete(main())


