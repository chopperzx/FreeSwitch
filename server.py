from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 定义底层 PaddleSpeech API 的地址
ASR_API_URL = 'http://localhost:5000/asr'
TTS_API_URL = 'http://localhost:5000/tts'

@app.route('/process_asr', methods=['POST'])
def process_asr():
    # 接收音频文件并转发给 ASR API
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio = request.files['audio']
    
    # 将音频文件发送到底层 ASR API
    response = requests.post(ASR_API_URL, files={'audio': audio})
    
    if response.status_code == 200:
        return response.json(), 200
    else:
        return jsonify({'error': 'ASR processing failed'}), response.status_code

@app.route('/process_tts', methods=['POST'])
def process_tts():
    # 接收文本并转发给 TTS API
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    response = requests.post(TTS_API_URL, json={'text': data['text']})
    
    if response.status_code == 200:
        # 返回生成的音频文件
        return response.content, 200, {'Content-Type': 'audio/wav'}
    else:
        return jsonify({'error': 'TTS processing failed'}), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
