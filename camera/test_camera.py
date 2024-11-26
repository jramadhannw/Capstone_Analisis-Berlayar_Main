import cv2

cap = cv2.VideoCapture("rtsp://admin:Qwerty123456@192.168.1.64:554/Streaming/Channels/101")
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
