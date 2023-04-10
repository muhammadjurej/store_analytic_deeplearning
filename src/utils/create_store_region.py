import cv2
import numpy as np
import json
import os

num_point = 0
num_bbx = 0
list_bbx_point = []
list_bbx = {}
file_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..')) + "/config/store_region.txt"

def save_bbx_list(bbx_list, file_path):
    with open(file_path, "w") as file:
        json.dump(bbx_list, file)

def viz_bbx(frame, **list_bbx):
    for _, point in list_bbx.items():
        x1 = point[0][0]
        y1 = point[0][1]
        w = point[1][0]
        h = point[1][1]
        r = int(np.random.randint(100, 255, 1))
        g = int(np.random.randint(100, 255, 1))
        b = int(np.random.randint(100, 255, 1))
        color = (r, g, b)
        cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), color, 2)

def viz_click(frame, point):
    for point in list_bbx_point:
        if len(point) != 0:
            cv2.circle(frame, point, 5, (0, 255, 0), -1)

def mouse_callback(event, x, y, flags, param):
    global num_point
    global num_bbx
    global list_bbx_point
    if event == cv2.EVENT_LBUTTONDOWN:
        num_point += 1
        # print(f"Clicked at ({x}, {y})", "numpoint: ", num_point)
        list_bbx_point.append((x, y))
        point_xy = (x, y)

        if num_point == 4:
            num_bbx += 1
            name_bbx = "region" + str(num_bbx)

            x1 = list_bbx_point[0][0]
            y1 = list_bbx_point[0][1]
            w = abs(list_bbx_point[1][0] - x1)
            h = abs(list_bbx_point[2][1] - y1)

            list_bbx[name_bbx] = [(x1, y1), (w, h)]
            num_point = 0
            list_bbx_point = []

            # print(list_bbx)

    elif event == cv2.EVENT_RBUTTONDOWN:
        print(list_bbx, frame.shape)
        save_bbx_list(list_bbx, file_path)
        print("bounding box list saved ..")


vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cv2.namedWindow("frame")
cv2.setMouseCallback("frame", mouse_callback)

while True:

    ret, frame = vid.read()
    viz_click(frame, list_bbx_point)
    viz_bbx(frame, **list_bbx)
    cv2.imshow("frame", frame)

    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break

vid.release()
cv2.destroyAllWindows()
