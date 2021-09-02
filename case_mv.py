import os
import threading
from flask import Flask, render_template, request, jsonify, Response
from datetime import datetime
from mv import *
import traceback

VERBOSE = True
status_msg = ""
keep_streaming = False

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

keep_pipeline = True
params_update_allowed = False
camera = Camera()
cropper = Crop()
background_substractor = SubstractBackground()
faceDetector = DetectFaces()
binarizer = Binarize()
lambda_block = Lambda()
streammer = Streammer()

def status(msg):
    global status_msg
    status_msg = msg
    if VERBOSE:
        print(msg)

def pipeline():
    global keep_pipeline
    global params_update_allowed
    frame = None
    frame_last = None
    fgbg = cv2.createBackgroundSubtractorMOG2()

    while True:
        while keep_pipeline and not params_update_allowed:
            try:
                # OK:
                frame_last = frame
                frame = camera.read()

                # OK:
                frame = cropper.crop(img=frame)
                last_cropped_frame = frame

                # Esta estratégia aplicada diretamente concedeu um resultado bastante instável.
                # frame = background_substractor.subtractBackground_MV(img_current=frame, img_last=frame_last)

                frame = background_substractor.subtractBackground(img_current=frame, mog2_bgsub=fgbg)

                # OK - Lento demais!
                frame = binarizer.binarize(img=frame)

                # Implementado isso aqui em lambda:
                # frame = faceDetector.detectFaces(img=frame)

                # OK:
                lambda_code = lambda_block.code
                if lambda_block.enabled:
                    exec(lambda_code)

                # OK:
                streammer.stream(img=frame)

            except Exception as e:
                status("Erro no pipeline")
                print("Exp: ", e)
                traceback.print_exc()
                keep_pipeline = False
        try:
            if keep_pipeline == False:
                params_update_allowed = True
        except:
            pass

def updateBlockParams(block_type, block_params):

    if block_type == 'camera':
        camera.enabled = True if bool(block_params['id_cam_en']) else False
        camera.camera_channel = int(block_params['id_cam_channel'])
        camera.camera_exposure_us = int(block_params['id_cam_exposure'])

    elif block_type == 'crop':
        cropper.enabled = True if bool(block_params['id_crop_en']) else False
        cropper.x = int(block_params['id_crop_x'])
        cropper.y = int(block_params['id_crop_y'])
        cropper.dx = int(block_params['id_crop_dx'])
        cropper.dy = int(block_params['id_crop_dy'])

    elif block_type == 'background_substract':
        background_substractor.enabled = True if bool(block_params['id_sub_en']) else False

    elif block_type == 'binarize':
        binarizer.enabled = True if bool(block_params['id_binarize_en']) else False
        binarizer.r = float(block_params['id_binarize_r'])
        binarizer.g = float(block_params['id_binarize_g'])
        binarizer.b = float(block_params['id_binarize_b'])
        binarizer.k = float(block_params['id_binarize_k'])

    elif block_type == 'lambda':
        lambda_block.enabled = True if bool(block_params['id_lambda_en']) else False
        lambda_block.setCodeB64(code_b64=block_params['id_lambda_code'])

    elif block_type == 'stream':
        streammer.enabled = True if bool(block_params['id_stream_en']) else False

def updatePipelineParameters(params):
    print("params = ", params)
    global keep_pipeline
    global params_update_allowed
    keep_pipeline = False
    while params_update_allowed == False:
        waiting = True

    for block in params:
        block_params = {}
        block_type = ""
        if block is not None:
            for pair in block:
                if isinstance(pair, dict):
                    for k, v in pair.items():
                        block_params[k] = v
                else:
                    block_type = pair
            updateBlockParams(block_type=block_type, block_params=block_params)

    keep_pipeline = True
    params_update_allowed = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/atualiza_pipeline', methods=['POST', 'GET'])
def atualiza_pipeline_view():
    if request.method == "POST":
        pipeline_parameters = request.get_json()
        updatePipelineParameters(params=pipeline_parameters)
    results = {'backend_fb': "Got pipeline parameters at: {}".format(datetime.now())}
    return jsonify(results)

@app.route('/video_feed')
def video_feed():
    return Response(
        streammer.gen(),
        mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":

    t1 = threading.Thread(target=pipeline)
    t1.daemon = True
    t1.start()

    app.static_folder = 'static'
    app.run(debug=False, threaded=True, use_reloader=False)

    t1.join()
