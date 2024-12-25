import time
import argparse
import time
import socket, struct, time
import numpy as np

def crazyCamera(common_event, common_var):

    # Args for setting IP/port of AI-deck. Default settings are for when
    # AI-deck is in AP mode.
    parser = argparse.ArgumentParser(description='Connect to AI-deck JPEG streamer example')
    parser.add_argument("-n",  default="192.168.4.1", metavar="ip", help="AI-deck IP")
    parser.add_argument("-p", type=int, default='5000', metavar="port", help="AI-deck port")
    parser.add_argument('--save', action='store_true', help="Save streamed images")
    args = parser.parse_args()

    deck_port = args.p
    deck_ip = args.n

    try:
        print("Connecting to socket on {}:{}...".format(deck_ip, deck_port))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(3)
        client_socket.connect((deck_ip, deck_port))
        print("Socket connected")
    except (socket.error, socket.timeout) as err:
        print(f"Failed to connect to socket: {err}")
        common_event['finishCrazyTelegram'].set()
        common_event['crazyAbortEvent'].set()
        common_event['finishCrazyCamera'].set()
        return

    imgdata = None
    data_buffer = bytearray()

    def rx_bytes(size):
        data = bytearray()
        try:
            while len(data) < size:
                data.extend(client_socket.recv(size-len(data)))
        except Exception as err:
            print(f"Error: Possibly a timeout error. {err}")
            common_event['finishCrazyTelegram'].set()
            common_event['crazyAbortEvent'].set()
            common_event['finishCrazyCamera'].set()
            return
        return data

    import cv2

    start = time.time()
    count = 0

    try:
        net = cv2.dnn.readNetFromONNX(f'./{common_var['camera']['model_directory']}{common_var['camera']['model']}')
        classes = []
        with open(f'{common_var['camera']['classes_directory']}{common_var['camera']['classes']}', 'r') as file:
            # Read lines and strip newline characters
            classes = [line.strip() for line in file]
    except Exception as err:
        print(f"Crazy Camera Process Terminating due to {err}")
        common_event['finishCrazyTelegram'].set()
        common_event['crazyAbortEvent'].set()
        common_event['finishCrazyCamera'].set()
        return
    
    label = None
    conf = None
    isFound = False

    while True:

        if common_event['crazyAbortEvent'].is_set() or common_event['cameraAbortEvent'].is_set():
            break


        try:
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
        except Exception as err:
            print(f"Crazy Camera Process Terminating due to {err}")
            common_event['finishCrazyTelegram'].set()
            common_event['crazyAbortEvent'].set()
            common_event['finishCrazyCamera'].set()
            return

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
                    if classes_score[ind] > common_var['camera']['confidence_threshold']:
                        classes_ids.append(ind)
                        confidences.append(confidence)
                        cx, cy, w, h = row[:4]
                        x1 = int((cx - w / 2) * x_scale)
                        y1 = int((cy - h / 2) * y_scale)
                        width = int(w * x_scale)
                        height = int(h * y_scale)
                        box = np.array([x1, y1, width, height])
                        boxes.append(box)

            indices = cv2.dnn.NMSBoxes(boxes, confidences, common_var['camera']['confidence_threshold'], common_var['camera']['confidence_threshold'])
            for i in indices:
                x1, y1, w, h = boxes[i]
                label = classes[classes_ids[i]]
                conf = confidences[i]
                text = label + " {:.2f}".format(conf)
                cv2.rectangle(color_img, (x1, y1), (x1 + w, y1 + h), (255, 0, 0), 2)
                cv2.putText(color_img, text, (x1, y1 - 2), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 255), 2)

            cv2.imshow('Raw', bayer_img)
            cv2.imshow('Color', color_img)

            if boxes and not isFound:
                # Save images if a "phone" is detected
                if (label == common_var['camera']['detection_classes'] and
                    conf>common_var['camera']['confidence_threshold']):
                    print(f"Found class {label} with confidence {conf:.2f}")
                    common_event['triggerESPAlarm'].set()
                    common_event['objectDetectedEvent'].set()
                    isFound = True # if an object is detected, it won't trigger anymore
                    """
                    # Save the raw Bayer image
                    if not os.path.exists("stream_out/raw"):
                        os.makedirs("stream_out/raw")
                    cv2.imwrite(f"stream_out/raw/img_{count:06d}.png", bayer_img)
                    
                    # Save the color image with detection
                    if not os.path.exists("stream_out/debayer"):
                        os.makedirs("stream_out/debayer")
                    cv2.imwrite(f"stream_out/debayer/img_{count:06d}.png", color_img)
                    """

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
    
    print("Crazy Camera Process Terminating")
    if common_event['crazyAbortEvent'].is_set():
        print("Aborting Camera")
        common_event['cameraAbortEvent'].set()
    
    common_event['finishCrazyTelegram'].set()
    common_event['finishCrazyCamera'].set()
    return