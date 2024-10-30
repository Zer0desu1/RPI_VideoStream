import cv2

url = "http://192.168.1.17:8080/video_feed"  

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Could not read frame.")
        break
    
    cv2.imshow('Video Stream', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
