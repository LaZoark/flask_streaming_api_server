import cv2

url = "http://123:123@nycu-wisepaas.onthewifi.com/?action=stream"
# url = 0

# cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
cap = cv2.VideoCapture(url, cv2.CAP_ANY)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Display the resulting frame
    cv2.imshow('frame', frame)
    # img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()