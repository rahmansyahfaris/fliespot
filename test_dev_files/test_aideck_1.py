#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2021 Bitcraze AB
#
#  AI-deck demo
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  this program; if not, write to the Free Software Foundation, Inc., 51
#  Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#  Demo for showing streamed JPEG images from the AI-deck example.
#
#  By default this demo connects to the IP of the AI-deck example when in
#  Access point mode.
#
#  The demo works by opening a socket to the AI-deck, downloads a stream of
#  JPEG images and looks for start/end-of-frame for the streamed JPEG images.
#  Once an image has been fully downloaded it's rendered in the UI.
#
#  Note that the demo firmware is continously streaming JPEG files so a single
#  JPEG image is taken from the stream using the JPEG start-of-frame (0xFF 0xD8)
#  and the end-of-frame (0xFF 0xD9).

# Test AI-deck #1:
# - yolov5 onnx opencv
# - I forgot the training parameters (batch size probably 2, epochs probably 10)

import argparse
import time
import socket,os,struct, time
import numpy as np

# Args for setting IP/port of AI-deck. Default settings are for when
# AI-deck is in AP mode.
parser = argparse.ArgumentParser(description='Connect to AI-deck JPEG streamer example')
parser.add_argument("-n",  default="192.168.4.1", metavar="ip", help="AI-deck IP")
parser.add_argument("-p", type=int, default='5000', metavar="port", help="AI-deck port")
parser.add_argument('--save', action='store_true', help="Save streamed images")
args = parser.parse_args()

deck_port = args.p
deck_ip = args.n

print("Connecting to socket on {}:{}...".format(deck_ip, deck_port))
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((deck_ip, deck_port))
print("Socket connected")

imgdata = None
data_buffer = bytearray()

def rx_bytes(size):
  data = bytearray()
  while len(data) < size:
    data.extend(client_socket.recv(size-len(data)))
  return data

import cv2

start = time.time()
count = 0

net = cv2.dnn.readNetFromONNX('./object_detection_model/phone_yolov5s_batch_2_epochs_10_best.onnx')
classes = ['a', 'phone', 'b']

while(1):
    # First get the info
    packetInfoRaw = rx_bytes(4)
    #print(packetInfoRaw)
    [length, routing, function] = struct.unpack('<HBB', packetInfoRaw)
    #print("Length is {}".format(length))
    #print("Route is 0x{:02X}->0x{:02X}".format(routing & 0xF, routing >> 4))
    #print("Function is 0x{:02X}".format(function))

    imgHeader = rx_bytes(length - 2)
    #print(imgHeader)
    #print("Length of data is {}".format(len(imgHeader)))
    [magic, width, height, depth, format, size] = struct.unpack('<BHHBBI', imgHeader)

    if magic == 0xBC:
      #print("Magic is good")
      #print("Resolution is {}x{} with depth of {} byte(s)".format(width, height, depth))
      #print("Image format is {}".format(format))
      #print("Image size is {} bytes".format(size))

      # Now we start rx the image, this will be split up in packages of some size
      imgStream = bytearray()

      while len(imgStream) < size:
          packetInfoRaw = rx_bytes(4)
          [length, dst, src] = struct.unpack('<HBB', packetInfoRaw)
          #print("Chunk size is {} ({:02X}->{:02X})".format(length, src, dst))
          chunk = rx_bytes(length - 2)
          imgStream.extend(chunk)
     
      count = count + 1
      meanTimePerImage = (time.time()-start) / count
      #print("{}".format(meanTimePerImage)) // this was not commented initially
      #print("{}".format(1/meanTimePerImage)) // this was not commented initially

      if format == 0:
          bayer_img = np.frombuffer(imgStream, dtype=np.uint8)   
          bayer_img.shape = (244, 324)
          color_img = cv2.cvtColor(bayer_img, cv2.COLOR_BayerBG2BGR)
          
          blob = cv2.dnn.blobFromImage(color_img,scalefactor=1/255,size=(640,640),mean=[0,0,0],swapRB=True,crop=False)
          net.setInput(blob)
          detections = net.forward()[0]
          classes_ids = []
          confidences = []
          boxes = []
          rows = detections.shape[0]

          img_width, img_height = color_img.shape[1], color_img.shape[0]
          x_scale = img_width / 640
          y_scale = img_height / 640

          for i in range(rows):
              row = detections[i]
              confidence = row[4]
              if confidence > 0.5:
                  classes_score = row[5:]
                  ind = np.argmax(classes_score)
                  if classes_score[ind] > 0.5:
                      classes_ids.append(ind)
                      confidences.append(confidence)
                      cx, cy, w, h = row[:4]
                      x1 = int((cx - w / 2) * x_scale)
                      y1 = int((cy - h / 2) * y_scale)
                      width = int(w * x_scale)
                      height = int(h * y_scale)
                      box = np.array([x1, y1, width, height])
                      boxes.append(box)

          indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.5)
          for i in indices:
              x1, y1, w, h = boxes[i]
              label = classes[classes_ids[i]]
              conf = confidences[i]
              text = label + "{:.2f}".format(conf)
              cv2.rectangle(color_img, (x1, y1), (x1 + w, y1 + h), (255, 0, 0), 2)
              cv2.putText(color_img, text, (x1, y1 - 2), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 255), 2)

          cv2.imshow('Raw', bayer_img)
          cv2.imshow('Color', color_img)
          """
          if args.save:
              cv2.imwrite(f"stream_out/raw/img_{count:06d}.png", bayer_img)
              cv2.imwrite(f"stream_out/debayer/img_{count:06d}.png", color_img)
          """
          cv2.waitKey(1)
      else:
          with open("img.jpeg", "wb") as f:
              f.write(imgStream)
          nparr = np.frombuffer(imgStream, np.uint8)
          decoded = cv2.imdecode(nparr,cv2.IMREAD_UNCHANGED)
          cv2.imshow('JPEG', decoded)
          cv2.waitKey(1)

