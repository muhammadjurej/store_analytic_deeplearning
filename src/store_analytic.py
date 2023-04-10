import sys
import cv2
import json
import numpy as np
from loguru import logger as log
from config.default_cfg import Config
from tflite_runtime.interpreter import Interpreter
from src.utils.tools import time_, calculate_time

sys.path.append("../config")

class StoreAnalytic:
    def __init__(self):
        self.config = Config()
        self.model_path = self.config.model_path
        self.data_sample = self.config.sample_video_path
        self.region_data_path = self.config.region_data_path
        
        #data template
        self.person_info = {}
        self.region_info = 0
        self.num_person = 0
        self.curr_num_people_on_region = {}
        self.last_num_people_on_region = {}
        self.start_time_on_region = {}
        self.end_time_on_region = {}
        self.state_time = {}
        self.analytic_result = {} # analytic_result = {region_name:[person_acumulate, time_acumulate}
        
    def _init_analytic(self, list_region_names):
        for region_name in list_region_names:
            self.analytic_result[region_name] = [0, 0]
            self.curr_num_people_on_region[region_name] = 0
            self.last_num_people_on_region[region_name] = 0
            self.start_time_on_region[region_name] = 0
            self.end_time_on_region[region_name] = 0
            self.state_time[region_name] = False
            
    def _vis_region(self, frame, region_info):
        region_keypoints, region_name = region_info
        for idx, region_keypoint in enumerate(region_keypoints):
            cv2.rectangle(
                frame,
                (region_keypoint[0], region_keypoint[1]),
                (region_keypoint[2], region_keypoint[3]),
                (255, 255, 0),
                2,
            )
            cv2.putText(
                frame,
                region_name[idx],
                (region_keypoint[0], region_keypoint[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 255),
                2,
            )
            
    def _is_intersect(self, store_region, person):
        x1 = max(store_region[0], person[0])
        y1 = max(store_region[1], person[1])
        x2 = min(store_region[2], person[2])
        y2 = min(store_region[3], person[3])

        if x1 >= x2 or y1 >= y2:
            return False
        else:
            return True
        
    def _extrac_person_info(self, person_info):
        list_person_keypoint = []
        list_person_id = []

        for person_id, keypoint in person_info.items():
            list_person_keypoint.append(keypoint)
            list_person_id.append(person_id)

        return list_person_keypoint, person_id
    
    def _count_people_and_time_on_region(self, region_info, person_info):
        region_keypoints, region_names = region_info
        
        self.curr_num_people_on_region = {name: 0 for name in region_names}
        
        if person_info == -1:
            no_person = True
        else:
            no_person = False
            person_keypoints, _ = person_info
            
        if no_person == True:
            self.curr_num_people_on_region = {name: 0 for name in region_names}
            
        if no_person == False:
            for idx, region_keypoint in enumerate(region_keypoints):
                for person_keypoint in person_keypoints:
                    if self._is_intersect(region_keypoint, person_keypoint):
                        self.curr_num_people_on_region[region_names[idx]] +=1

                #calculate people
                if self.curr_num_people_on_region[region_names[idx]] > self.last_num_people_on_region[region_names[idx]]:
                    self.analytic_result[region_names[idx]][0] += \
                        self.curr_num_people_on_region[region_names[idx]] - self.last_num_people_on_region[region_names[idx]]
        #calculate time     
        self.region_time(self.curr_num_people_on_region)
        
        self.last_num_people_on_region = self.curr_num_people_on_region
        
    def region_time(self, curr):
        for idx, (region_names, num) in enumerate(curr.items()):
            if self.state_time[region_names] == False:
                    if self.curr_num_people_on_region[region_names] !=0:
                        self.start_time_on_region[region_names] = time_()
                        self.state_time[region_names] = True
                        
            if self.state_time[region_names] == True:
                if self.curr_num_people_on_region[region_names] == 0:
                    self.end_time_on_region[region_names] = time_()
                    self.analytic_result[region_names][1] += \
                        abs(calculate_time(self.end_time_on_region[region_names], self.start_time_on_region[region_names]))
                    self.start_time_on_region[region_names] = ""
                    self.end_time_on_region[region_names] = ""
                    self.state_time[region_names] = False
    
    def _extrac_region_info(self):
        list_store_region = {}
        list_region_keypoint = []
        list_region_name = []

        with open(self.region_data_path, "r") as file:
            data = json.load(file)
        for region_name, point in data.items():
            list_store_region[region_name] = [tuple(point[0]), tuple(point[1])]

        for region_name, value in list_store_region.items():
            x1 = value[0][0]
            y1 = value[0][1]
            w_bbx = value[1][0]
            h_bbx = value[1][1]
            x2 = x1 + w_bbx
            y2 = y1 + h_bbx

            list_region_keypoint.append([x1, y1, x2, y2])
            list_region_name.append(region_name)

        return list_region_keypoint, list_region_name
        
    def run(self, vis_region=False, source="video"):
        """ Run analytic sytem"""
        interpreter = Interpreter(model_path=self.model_path)
        interpreter.allocate_tensors()
        input_detail = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        self.region_info = self._extrac_region_info()
        self._init_analytic(self.region_info[1])
        
        if source == "video":
            cap = cv2.VideoCapture(self.data_sample)
            
        elif source == "cam":
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        elif source == "web_cam":
            cv2.VideoCapture(1, cv2.CAP_DSHOW)
            
        while True:
            ret, frame = cap.read()
            if ret == False:
                log.warning("error while open video")
                break
            self.person_info.clear()
            self.num_person = 0
            
            in_model = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # resize gambar ke 300,300 sesuai input model
            in_model = cv2.resize(in_model, (300, 300), interpolation=cv2.INTER_AREA)
            # rubah format gambar(1, 300, 300, 3)
            in_model = in_model.reshape(1, in_model.shape[0], in_model.shape[1], in_model.shape[2])
            # conver ke uint8 (0-255)
            in_model = in_model.astype(np.uint8)
            
            #set input tensor
            interpreter.set_tensor(input_detail[0]["index"], in_model)
            
            #run model
            interpreter.invoke()
            
            # unpack output tensor
            boxes = interpreter.get_tensor(output_details[0]["index"])
            labels = interpreter.get_tensor(output_details[1]["index"])
            scores = interpreter.get_tensor(output_details[2]["index"])
            num = interpreter.get_tensor(output_details[3]["index"])
            
            for i in range(boxes.shape[1]):
                if scores[0, i] > 0.5:
                    if int(labels[0, i]) == 0:
                        self.num_person +=1
                        box = boxes[0, i, :]
                        x0 = int(box[1] * frame.shape[1])
                        y0 = int(box[0] * frame.shape[0])
                        x1 = int(box[3] * frame.shape[1])
                        y1 = int(box[2] * frame.shape[0])
                        box = box.astype(int)
                        cv2.rectangle(frame, (x0, y0), (x1, y1), (255, 0, 0), 2)
                        cv2.rectangle(
                            frame, (x0, y0), (x0 + 100, y0 - 30), (255, 0, 0), -1
                        )
                        cv2.putText(
                            frame,
                            "person",
                            (x0, y0),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (255, 255, 255),
                            2,
                        )
                        self.person_info[f"person_{self.num_person}"] = [x0, y0, x1, y1]
                        
                        if vis_region == True:
                            self._vis_region(frame, self.region_info)
                            
            if self.person_info == {}:
                self._count_people_and_time_on_region(self.region_info, -1)
            else:
                self._count_people_and_time_on_region(self.region_info, self._extrac_person_info(self.person_info))
            print(self.analytic_result)
            cv2.putText(frame, f"num person: {self.num_person}", (0, 20), cv2.FONT_HERSHEY_SIMPLEX
                        , 1, (255, 0, 0), 2)
            cv2.imshow("analytic view", frame)
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
            
                
        
        