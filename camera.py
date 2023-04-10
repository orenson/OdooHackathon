#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import threading
import numpy as np
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont


CLASSES = {
    0: "jupiler",
    1: "maes",
    2: "orval",
    3: "Unknown"
}


# class VideoCamera(object):
#     def __init__(self):
#         self.video = cv2.VideoCapture(0)
#         self.model = YOLO('yolo.pt')
#         self.pred_thread = threading.Thread(target=self.get_rois)
#         self.last_img = None
#         self.last_rois = list()
#         self.last_pred = None

#     def __del__(self):
#         self.video.release()
    
#     def get_rois(self):
#         if self.last_img is None:
#             return None
        
#         pil_img = Image.fromarray(self.last_img)
#         preds = self.model(pil_img, verbose=False)
#         #sleep(1)

#         rois = list()
#         for i, pred in enumerate(preds):
#             for box in pred.boxes:
#                 box_xywh = box.xywh[0]
#                 rois.append({
#                     'x': box_xywh[0],
#                     'y': box_xywh[1],
#                     'width': box_xywh[2],
#                     'height': box_xywh[3],
#                     'class': CLASSES[int(box.cls)],
#                     'confidence': box.conf.numpy()[0]})

#                 if box.conf.numpy()[0] > 0.3:
#                     self.last_pred = CLASSES[int(box.cls)]
#                     with open('pred.txt', 'w') as f:
#                         f.writelines([self.last_pred])
        
#         self.last_rois = rois.copy()

#     def get_frame(self):
#         success, image = self.video.read()
#         self.last_img = image
#         pil_img = Image.fromarray(image)

#         if success:
#             if not self.pred_thread.is_alive():
#                 self.pred_thread = threading.Thread(target=self.get_rois)
#                 self.pred_thread.start()
        
#             for roi in self.last_rois:
#                 pil_img = Image.fromarray(image)
#                 # Calculate the coordinates of the rectangle
#                 left = int(roi['x'] - roi['width'] / 2)
#                 top = int(roi['y'] - roi['height'] / 2)
#                 right = int(roi['x'] + roi['width'] / 2)
#                 bottom = int(roi['y'] + roi['height'] / 2)

#                 # Draw a red rectangle around the region of interest
#                 draw = ImageDraw.Draw(pil_img)
#                 draw.rectangle((left, top, right, bottom), outline='red', width=3)

#                 font = ImageFont.truetype("arial.ttf", 16)
#                 text_x, text_y = left, top - 20
#                 class_label = '{:.0%} {}'.format(roi["confidence"], roi["class"])
#                 draw.text((text_x, text_y), class_label, font=font, fill='red')

#             ret, jpeg = cv2.imencode('.jpg', np.array(pil_img))
#             return jpeg.tobytes()
        
#         else:
#             jpeg=Image.open('banner_background.jpeg')
#             return jpeg.tobytes()


from typing import List, Dict
class VideoCamera:
    def __init__(self) -> None:
        self.video = cv2.VideoCapture(0)
        self.model = YOLO('yolo.pt')
        self.pred_thread = threading.Thread(target=self.detect_regions_of_interest)
        self.last_img = None
        self.last_regions_of_interest: List[Dict[str, float]] = []
        self.last_prediction = None

    def __del__(self) -> None:
        print("Deleting video camera and pred thread")
        self.video.release()

    def detect_regions_of_interest(self) -> None:
        if self.last_img is None:
            return None
        
        pil_img = Image.fromarray(self.last_img)
        preds = self.model(pil_img, verbose=False)
        #sleep(1)

        regions_of_interest = []
        for i, pred in enumerate(preds):
            for box in pred.boxes:
                box_xywh = box.xywh[0]
                regions_of_interest.append({
                    'x': box_xywh[0],
                    'y': box_xywh[1],
                    'width': box_xywh[2],
                    'height': box_xywh[3],
                    'class': CLASSES[int(box.cls)],
                    'confidence': box.conf.numpy()[0]})

                if box.conf.numpy()[0] > 0.3:
                    self.last_prediction = CLASSES[int(box.cls)]
                    with open('pred.txt', 'w') as f:
                        f.writelines([self.last_prediction])
        
        self.last_regions_of_interest = regions_of_interest.copy()

    def get_frame(self) -> bytes:
        success, image = self.video.read()
        if not success:
            return None

        self.last_img = image
        pil_img = Image.fromarray(image)

        if not self.pred_thread.is_alive():
            self.pred_thread = threading.Thread(target=self.detect_regions_of_interest)
            self.pred_thread.start()

        for region in self.last_regions_of_interest:
            pil_img = Image.fromarray(image)
            left = int(region['x'] - region['width'] / 2)
            top = int(region['y'] - region['height'] / 2)
            right = int(region['x'] + region['width'] / 2)
            bottom = int(region['y'] + region['height'] / 2)

            draw = ImageDraw.Draw(pil_img)
            draw.rectangle((left, top, right, bottom), outline='red', width=3)

            font = ImageFont.truetype("arial.ttf", 16)
            text_x, text_y = left, top - 20
            class_label = f"{region['confidence']:.0%} {region['class']}"
            draw.text((text_x, text_y), class_label, font=font, fill='red')

        ret, jpeg = cv2.imencode('.jpg', np.array(pil_img))
        return jpeg.tobytes()
