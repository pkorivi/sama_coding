from curses import meta
import json
import os
import shutil


def createSensorMetaData(frames, pcd_files, sensor_meta_data_folder):
    for file in pcd_files:
        odometry = frames.get(file).get("odom")
        meta_data = {
            "x": odometry.get("position").get("x"),
            "y": odometry.get("position").get("y"),
            "z": odometry.get("position").get("z"),
            "rotation_x": odometry.get("orientation").get("x"),
            "rotation_y": odometry.get("orientation").get("y"),
            "rotation_z": odometry.get("orientation").get("z"),
            "rotation_w": odometry.get("orientation").get("w"),
        }
        with open(sensor_meta_data_folder + "/"+file+".json", 'w') as fp:
            json.dump(meta_data, fp)


def zipAndDeleteTempFiles(sensor_meta_data_folder, sensor_meta_data_zip):
    shutil.make_archive(sensor_meta_data_zip,
                        'zip', sensor_meta_data_folder)
    shutil.rmtree(sensor_meta_data_folder)


def getInitialTaskCreationDict():
    dict = {
        "data": {
            "CloudURL": " Path to the folder cointaining the PCD files",
            "LeftCamera": "Path to the folder cointaining Left Camera Files",
            "RightCamera": "Path to the folder cointaining Right Camera Files ",
            "CenterCamera": "Path to the folder cointaining Center Camera Files",
            "SensorMetadata": "Path to Zip metadata"
        }
    }
    return dict


def createTaskCreation(frames, folder, sensor_meta_data_zip, task_creation_json_path):
    frame = next(iter(frames.values()))
    sync = frame.get("sync")
    center_id = sync.get("/sama/camera/center/image_raw/compressed")
    left_id = sync.get("/sama/camera/left/image_raw/compressed")
    right_id = sync.get("/sama/camera/right/image_raw/compressed")

    sensor_data = frame.get("sensor_data").keys()
    cam_idx_dict = {}
    for sensor in sensor_data:
        if sensor.startswith("CAM"):
            cam_idx_dict[frame.get("sensor_data").get(
                sensor).get("index")] = sensor

    task_creation = getInitialTaskCreationDict()
    task_creation["data"]["LeftCamera"] = folder + \
        "/images/"+cam_idx_dict[str(left_id)]
    task_creation["data"]["RightCamera"] = folder + \
        "/images/"+cam_idx_dict[str(right_id)]
    task_creation["data"]["CenterCamera"] = folder + \
        "/images/"+cam_idx_dict[str(center_id)]
    task_creation["data"]["CloudURL"] = folder + "/pcd/PCD_Struct/"
    task_creation["data"]["SensorMetadata"] = sensor_meta_data_zip + ".zip"

    with open(task_creation_json_path, 'w') as fp:
        json.dump(task_creation, fp)


os.chdir("Question_2_Sequences")
for folder in os.listdir():
    if folder.startswith("sequence_"):
        print(folder)
        pcd_files = None
        for rootdir, dirs, files in os.walk(folder + "/pcd/PCD_Struct"):
            # strip extension of pcd files
            pcd_files = [file[:-4] for file in files]

        sensor_meta_data_folder = folder + "/pcd/temp"
        sensor_meta_data_zip = folder+"/pcd/sensor_metadata"
        task_creation_json_path = folder+"/pcd/task_creation.json"
        # create meta data temp folder
        if not os.path.exists(sensor_meta_data_folder):
            os.makedirs(sensor_meta_data_folder)

        task_creation = None
        with open(folder + "/devkit/data.json", 'r') as file:
            data = json.load(file)
            createSensorMetaData(
                data["frames"], pcd_files, sensor_meta_data_folder)
            createTaskCreation(
                data["frames"], folder, sensor_meta_data_zip, task_creation_json_path)

        zipAndDeleteTempFiles(sensor_meta_data_folder, sensor_meta_data_zip)
