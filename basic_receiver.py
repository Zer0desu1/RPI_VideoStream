import cv2 as cv
import time

url = "http://192.168.1.17:8080/video_feed"

# Attempt to open the video stream
cap = cv.VideoCapture(url)

# Retry opening the video stream until successful
while not cap.isOpened():
    print("Error: Could not open video stream. Retrying in 2 seconds...")
    time.sleep(2)  
    cap = cv.VideoCapture(url)

print("Video stream opened successfully.")


# Main loop to read frames
while True:
    ret, frame = cap.read()  # Read a frame from the video stream (Not working properly sorry :C )
    
    if not ret:
        print("Error: Could not read frame. Retrying...")
        continue  #worse part of this code :(

    # Edge detection
    edges = cv.Canny(frame, threshold1=100, threshold2=200)
   
  


    cv.imshow('Original Video Stream', frame)
    cv.imshow('Edge-Detected Video Stream', edges)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
