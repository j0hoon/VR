from pymongo import MongoClient

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import datetime
import pandas as pd
from tqdm import tqdm
import numpy as np


class Recognition():
    def __init__(self):
        
        self.FVL = -1
        self.FVI = -1
        self.FVR = -1
        self.AVL = -1
        self.AVR = -1
        self.RVL = -1
        self.RVI = -1
        self.RVR = -1
    
    def zero_reset(self):
        
        self.FVL = 0
        self.FVI = 0
        self.FVR = 0
        self.AVL = 0
        self.AVR = 0
        self.RVL = 0
        self.RVI = 0
        self.RVR = 0        

def connect_mongoDB():
    os.system('cls')
    print("CONNECTING MONGODB.....")
    # [Connect client]
    client = MongoClient("mongodb://192.168.75.251:27017/")

    # [Connect METIS]
    db = client['METIS']['Scenario']
    
    return db   

def get_query_data(db, dataType = "EXP-RG3", dataName = "RG3_030323",roadName = "HW", illumination = "Day", travelDistance = 2, status = 0, travelTime = 0.03,TOTAL_OPTION = False):
    print("GET QUERY DATA.....")
    # [Set query]
    # Query = {"$and":[{"dataType":dataType},{"scenery.roadName":{"$regex":roadName, "$options":"i"}},{"travelDistance":{"$gte":travelDistance}},{"environment.illumination":illumination},{"Status":status},{"directory.exported":{"$regex":dataName, "$options":"i"}},{"directory.registration":{"$regex":dataName, "$options":"i"}},{"directory.perception.SF":{"$regex":dataName, "$options":"i"}}]}
    Query = {"$and":[{"dataType":dataType},{"directory.exported":{"$regex":dataName, "$options":"i"}},{"directory.registration":{"$regex":dataName, "$options":"i"}},{"directory.perception.SF":{"$regex":dataName, "$options":"i"}},{"scenery.roadName":{"$regex":roadName, "$options":"i"}},{"travelDistance":{"$gte":travelDistance}},{"travelTime":{"$gte":travelTime}}]} 
    if TOTAL_OPTION:
        Query = {"$and":[{"dataType":dataType},{"directory.exported":{"$regex":dataName, "$options":"i"}},{"directory.registration":{"$regex":dataName, "$options":"i"}},{"directory.perception.SF":{"$regex":dataName, "$options":"i"}}]} 
    # [Load documents]
    Documents = list(db.find(Query))
    
    return Documents

def get_recognition_time(Document):
    analized_data = pd.DataFrame(columns =["FVL","FVI","FVR","AVL","AVR","RVL","RVI","RVR","directory"])
    
    recognition_file = get_recognition_file(Document["directory"]['perception']["recognition"])
    RECOGNITION = Recognition()    
    RECOGNITION_SUM = Recognition()
    RECOGNITION_SUM.zero_reset()
    for temp_num in range(recognition_file.shape[0]):
        
        check_recognition(recognition_file, temp_num, RECOGNITION)
        
        diff_frame = calculate_frame_diff(recognition_file['FrameIndex'], temp_num)
        
        add_to_recognition_sum(RECOGNITION_SUM , RECOGNITION , diff_frame)
        
        analized_data.loc[0] = [RECOGNITION_SUM.FVL,RECOGNITION_SUM.FVI,RECOGNITION_SUM.FVR,RECOGNITION_SUM.AVL,RECOGNITION_SUM.AVR,RECOGNITION_SUM.RVL,RECOGNITION_SUM.RVI,RECOGNITION_SUM.RVR,Document["directory"]['perception']["recognition"]]
    
    return analized_data

def calculate_frame_diff(frameIndex, temp_num):
    
    current_frame = 0
    next_frame = 0
    diff = 0
        
    try:
        next_frame = frameIndex[temp_num + 1]
        current_frame = frameIndex[temp_num]
        
    except:
        next_frame = 2410
        current_frame = frameIndex[temp_num]
    
    diff = next_frame - current_frame    

    return diff
    

def add_to_recognition_sum(RECOGNITION_SUM, RECOGNITION, diff_frame):
    if RECOGNITION.FVL>0:
        RECOGNITION_SUM.FVL += diff_frame
    if RECOGNITION.FVI>0:
        RECOGNITION_SUM.FVI += diff_frame
    if RECOGNITION.FVR>0:
        RECOGNITION_SUM.FVR += diff_frame
    if RECOGNITION.AVL>0:
        RECOGNITION_SUM.AVL += diff_frame
    if RECOGNITION.AVR>0:
        RECOGNITION_SUM.AVR += diff_frame
    if RECOGNITION.RVL>0:
        RECOGNITION_SUM.RVL += diff_frame
    if RECOGNITION.RVI>0:
        RECOGNITION_SUM.RVI += diff_frame
    if RECOGNITION.RVR>0:
        RECOGNITION_SUM.RVR += diff_frame
    

def check_recognition(recognition_file, temp_num, RECOGNITION):
    temp_recognition = recognition_file.iloc[temp_num]["Recognition"]
    temp_id = recognition_file.iloc[temp_num]["ID"]
    # temp_frameIndex = recognition_file.iloc[temp_num]["FrameIndex"]
    
    if temp_recognition == "FVL" :
        RECOGNITION.FVL = temp_id
    elif temp_recognition == "FVI":
        RECOGNITION.FVI = temp_id
    elif temp_recognition == "FVR":
        RECOGNITION.FVR = temp_id
    elif temp_recognition == "AVL":
        RECOGNITION.AVL = temp_id    
    elif temp_recognition == "AVR":
        RECOGNITION.AVR = temp_id    
    elif temp_recognition == "RVL":
        RECOGNITION.RVL = temp_id
    elif temp_recognition == "RVI":
        RECOGNITION.RVI = temp_id
    elif temp_recognition == "RVR":
        RECOGNITION.RVR = temp_id    
    # elif temp_recognition == "Ego" or  temp_recognition == "EGO":
    #     pass
    elif temp_recognition == "None" or temp_recognition == None:
        if RECOGNITION.FVL == temp_id:
            RECOGNITION.FVL = -1
        elif RECOGNITION.FVI == temp_id:
            RECOGNITION.FVI = -1
        elif RECOGNITION.FVR == temp_id:
            RECOGNITION.FVR = -1
        elif RECOGNITION.AVL == temp_id:
            RECOGNITION.AVL = -1
        elif RECOGNITION.AVR == temp_id:
            RECOGNITION.AVR = -1
        elif RECOGNITION.RVL == temp_id:
            RECOGNITION.RVL = -1
        elif RECOGNITION.RVI == temp_id:
            RECOGNITION.RVI = -1
        elif RECOGNITION.RVR == temp_id:
            RECOGNITION.RVR = -1
        else:
            pass
    else:
        pass
            
    


def get_recognition_file(directory):
    if "xlsx" in directory:
        directory = directory.replace("xlsx","csv")
    
    recog_file = pd.read_csv(directory)
    
    return recog_file

def CheckRecognition(targetRecognition,tempRecognition,gtFile,num,tempId,tempFrameIndex,tempGtRecog,frameSize = 2400):
    if tempRecognition == str(targetRecognition):
        for tempNum in range(num,gtFile.shape[0]):
            if tempId == gtFile.iloc[tempNum]["ID"] and gtFile.iloc[tempNum]["Recognition"] != str(targetRecognition):
                tempGtRecog = MakeOne(tempGtRecog,tempFrameIndex, gtFile.iloc[tempNum]["FrameIndex"],frameSize)
                break
    return tempGtRecog

def MakeOne(list, start, end,frameSize):
    start = int(start)
    end = int(end)

    if start >= end:
        end = frameSize
    
    tmpList = list
    if end >= np.size(tmpList):
        end = np.size(tmpList)-1
    tmpList[start:end] = np.ones(end-start)
    return tmpList

def main():
    
    total_result = pd.DataFrame(columns =["FVL","FVI","FVR","AVL","AVR","RVL","RVI","RVR","directory"])
    
    db = connect_mongoDB()
    
    data_list = ["RG3_030223", "RG3_030323", "RG3_030423"]
    
    for _dataName in data_list:
    
        document = get_query_data(db, dataType = "EXP-RG3", dataName = _dataName,roadName = "HW", illumination = "Day", travelDistance = 2, status = 0,TOTAL_OPTION=True)
        
        for tmp_doc in tqdm(document):
            tmp_result = get_recognition_time(tmp_doc)
            total_result = pd.concat([total_result, tmp_result], axis = 0, ignore_index = True)
    
    balanced_result = total_result.query("RVI > 0 and AVL > 0")
    
    balanced_result.to_csv("balanced_result.csv",index=False)
        
    # means = total_result.mean()

    # weight = [0.8, 0.8, 0.7, 100.0, 0.8, 0.8, 100.0, 0.5]
    
    # new_df = pd.DataFrame(columns =["FVL","FVI","FVR","AVL","AVR","RVL","RVI","RVR","directory"])
    # for i in range(len(total_result.columns)-1):
    #     col = total_result.columns[i]
    #     threshold = means[i]*weight[i]
    
    #     new_df[col] = total_result[total_result[col] <= threshold][col]

    # new_df_na = new_df.dropna()
    df1 = total_result.sum()
    df2 = balanced_result.sum()
    


    tmp_ = total_result.loc[:,["FVL","FVI","FVR","AVL","AVR","RVL","RVI","RVR"]]
    tmp_2 = tmp_.mean()    
    
    data = {'Recognition':["FVL","FVI","FVR","AVL","AVR","RVL","RVI","RVR"],
            'frame':[tmp_2['FVL'],tmp_2['FVI'],tmp_2['FVR'],tmp_2['AVL'],tmp_2['AVR'],tmp_2['RVL'],tmp_2['RVI'],tmp_2['RVR']]}
    
    result_df = pd.DataFrame(data)
    sns.barplot(x='Recognition',y='frame',data = result_df)
    plt.grid(True)
    plt.show()
    
    
    
    
    
    
    print(np.size(balanced_result))


if __name__ == "__main__":
    
    # target = 600
    # x = ["FVL","FVI","FVR","AVL","AVR","RVL","RVI","RVR"]
    # y = [target, target, target, target, target, target, target, target]
    # # y = [1000,1000, 1000, 1000, 1000, 1000, 1000, 1000]

    # sns.barplot(x=x, y=y)
    # plt.xlabel("Recognition")
    # plt.ylabel("frame")
    # plt.show()
    main()
    
    print("DONE")