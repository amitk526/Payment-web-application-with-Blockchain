import cv2  
import numpy as np 
import pyzbar.pyzbar as pyzbar

# img = cv2.imread("pysource_qrcode.png")

# decodeObjects = pyzbar.decode(img)

# print(decodeObjects)

# for obj in decodeObjects:
#     print("Data:", obj.data)

# cv2.imshow("Image",img) # displaying the image
# cv2.waitKey(5000)  # To keep the image open 

cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_COMPLEX

while True:
    _, frame = cap.read()

    decodedObjects = pyzbar.decode(frame)
    for obj in decodedObjects:
        # print("Data", obj.data) 
        cv2.putText(frame, str(obj.data), (50,50), font, 3,(255,0,0),3)
    
    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1)
    if key == 27:   #27 is "esc" key ; on pressing "esc" it will exit exit the frame
        break
