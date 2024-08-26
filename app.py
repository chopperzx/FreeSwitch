from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

def run_paddlespeech_asr(audio_path):
    # 调用 PaddleSpeech 的命令行工具进行语音识别
    process = subprocess.Popen(
        ['paddlespeech', 'asr', '--lang', 'zh', '--model', 'conformer_wenetspeech', '--input', audio_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(input='Y\n')
    
    if process.returncode != 0:
        print(f"Error: {stderr}")
        return "Error in processing"
    
    return stdout.strip()

def run_paddlespeech_tts(text, output_path):
    # 调用 PaddleSpeech 的命令行工具进行文本转语音
    subprocess.run(['paddlespeech', 'tts', '--input', text, '--output', output_path])

@app.route('/asr', methods=['POST'])
def asr():
    # 从POST请求中获取音频文件
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    
    audio_file = request.files['audio']
    audio_path = 'temp_audio.wav'
    audio_file.save(audio_path)  # 保存上传的音频文件
    
    result = run_paddlespeech_asr(audio_path)
    return jsonify({'text': result})

@app.route('/tts', methods=['POST'])
def tts():
    # 从POST请求中获取文本信息
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text']
    output_path = 'output_audio.wav'
    
    run_paddlespeech_tts(text, output_path)
    with open(output_path, 'rb') as f:
        audio_data = f.read()
    
    return audio_data, 200, {'Content-Type': 'audio/wav'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
