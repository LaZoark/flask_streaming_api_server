from flask import Flask, Response, stream_with_context, render_template
import cv2, time

app = Flask(__name__)
video = cv2.VideoCapture(0)   # 從視訊鏡頭擷取影片

@app.route('/')
def index():
    try:
        # return "Please go to => http://localhost:5000/video_feed"
        # return "Please go to => http://nycu-wisepaas.onthewifi.com:5000/video_feed"
        return render_template("index.html")
    except GeneratorExit:
        print('close')


def gen(video):
    try:
        while True:
            success, image = video.read()
            ret, jpeg = cv2.imencode('.jpg', image)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    except GeneratorExit:
        # global video
        # video.release()
        # video = cv2.VideoCapture(0)
        print('close')
               
@app.route('/stream')
def video_feed():
    global video
    return Response(gen(video),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
def gen_cap(video):
    success, image = video.read()
    ret, jpeg = cv2.imencode('.jpg', image)
    frame = jpeg.tobytes()
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/capture')
def capture():
    global video
    return Response(gen_cap(video),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/debug')
def stream():
    def gen():
        try:
            i = 0
            while True:
                data = 'this is line {}'.format(i)
                print(data)
                yield data + '<br>'
                i += 1
                time.sleep(1)
        except GeneratorExit:
            print('closed')

    return Response(stream_with_context(gen()))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
# When everything done, release the capture
    video.release()
