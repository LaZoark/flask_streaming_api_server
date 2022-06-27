from flask import Flask, render_template, Response, stream_with_context, jsonify, request, g, send_from_directory, render_template_string
# from flask import redirect
from markupsafe import escape
import cv2, time, os
from PIL import Image

app = Flask(__name__)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# url = 'rtsp://wisepaas:310505030@192.168.1.52:554/stream2'
# url = 'rtsp://wisepaas:310505030@nycu-wisepaas.onthewifi.com:5005/stream1'
url = 1
# url = 'http://61.220.211.130:9993/Live?channel=1443&mode=0'
# url = 'https://cctvatis4.ntpc.gov.tw/C000232'
# url = 'https://cdn-004.whatsupcams.com/hls/hr_pula01.m3u8' # 超屌不知哪個國家

# video = cv2.VideoCapture(url)
# video.set(cv2.CAP_PROP_BUFFERSIZE, 30)  # set buffer size 
# video.set(cv2.CAP_PROP_FPS, 15)
# url = r'London.mp4'

# url = 'facemask.gif'
video = cv2.VideoCapture(url)
# ret,frame = video.read() # ret=True if it finds a frame else False. Since your gif contains only one frame, the next read() will give you ret=False
# img = Image.fromarray(frame)
# img = img.convert('RGB')
# video = cv2.VideoCapture(url)
# video.set(cv2.CAP_PROP_POS_MSEC, 500)
# video.set(cv2.CAP_PROP_FPS, 20)
# video.set(cv2.CAP_PROP_BUFFERSIZE, 30)  # set buffer size 


frames = [open('facemask\\facemask-' + str(f) + '.jpg', 'rb').read() for f in range(0, 67)]
def gen_frames():
    counter = 0
    while True:
        frame = frames[counter % 67]
        counter += 1
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.1)

@app.route('/facemask_gif')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def gen(video, _remote_addr, request_start_time, _path):
    try:
        while True:
            success, image = video.read()
            # image = image[125:-125, 150:-150]
            ret, jpeg = cv2.imencode('.jpg', image)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    except GeneratorExit:
        request_time = lambda: "%.4f" % (time.time() - request_start_time)
        print(f'[Closed] Connection with {_remote_addr} after {request_time()} seconds @ {_path}')

def gen_face(video, _remote_addr, request_start_time, _path):
    try:
        while True:
            # Read the frame
            _, image = video.read()
            # image = image[125:-125, 150:-150]
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.12,
            minNeighbors=4)
            for (x, y, w, h) in faces:
                cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 0), 2)
            ret, jpeg = cv2.imencode('.jpg', image)
            # time.sleep(0.1)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    except GeneratorExit:
        request_time = lambda: "%.4f" % (time.time() - request_start_time)
        print(f'[Closed] Connection with {_remote_addr} after {request_time()} seconds @ {_path}')

def gen_cap(video):
    success, image = video.read()
    # image = image[125:-125, 150:-150]
    ret, jpeg = cv2.imencode('.jpg', image)
    frame = jpeg.tobytes()
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')



@app.route('/')
def index():
    return render_template("index.html")
@app.route("/<str>")
def unknown_path_handler(str):
    return render_template("handler.html", str=escape(str))
@app.route('/disclaimer')
def disclaimer():
    return render_template("disclaimer.html")
@app.route('/stream')
def video_stream():
    # global video
    remote_addr = request.remote_addr
    full_path = request.full_path
    return Response(gen(video, remote_addr, time.time(), full_path),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/stream_face_detection')
def video_detection():
    global video
    remote_addr = request.remote_addr
    full_path = request.full_path
    return Response(gen_face(video, remote_addr, time.time(), full_path),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/capture')
def capture():
    global video
    return Response(gen_cap(video),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/debug')
def stream():
    def gen():
        i =  0
        try:
            while True:
                data = f'this is line {i} from {request.remote_addr}'
                print(data)
                yield data + '<br>'
                i += 1
                time.sleep(1)
        except GeneratorExit:
            print(f'[Closed] Connection with {request.remote_addr} after {g.request_time()} seconds @ {request.full_path}')
    return Response(stream_with_context(gen()))

@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200


@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.4f" % (time.time() - g.request_start_time)

# @app.after_request
# def after_request():
#     g.request_start_time = time.time()
#     g.request_time = lambda: "%.4f" % (time.time() - g.request_start_time)
#     print(f'[Closed] Connection with {request.remote_addr} after {g.request_time()} seconds @ {request.full_path}')

# @app.teardown_request
# def teardown_request(error):
#     """在每一次請求之後執行，如果有異常，將異常傳入"""
#     print ("teardown_request")



@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


# ZeroSSL 認證用
app.config['UPLOAD_FOLDER'] = os.getcwd()+ '\\.well-known\\pki-validation\\' #取得伺服器目前路徑
@app.route('/.well-known/pki-validation/<path:filename>', methods=['GET', 'POST'])
def acme_challenge(filename):
    print(request.url, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=filename)


@app.route('/takephoto')
def takephoto():
    return render_template('localCamera.html')
@app.route('/takephoto_and_edit')
def Image_Editor_Capture():
    return render_template('Image_Editor_Capture.html')


if __name__ == '__main__':
    ssl = ['ssl\\certificate.crt', 'ssl\\ca_bundle.crt', 'ssl\\private.key']
    app.run(host='0.0.0.0', port=5000, debug=0, threaded=True, ssl_context=(ssl[0], ssl[2]))
    # app.run(host='0.0.0.0', port=5000, threaded=True, ssl_context=('cert.pem', 'key.pem'))
    # app.run(host='0.0.0.0', port=5000, threaded=True, )
    video.release()
