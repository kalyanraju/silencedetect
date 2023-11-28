from flask import Flask, request, jsonify
import numpy as np
import io
import wave

app = Flask(__name__)

@app.route('/non_silence_duration', methods=['POST'])
def non_silence_duration():
    if 'file' not in request.files:
        return jsonify(error='No file part'), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify(error='No selected file'), 400

    try:
        audio = io.BytesIO(file.read())
        wf = wave.open(audio, 'rb')
        n_channels, _, framerate, n_frames, _, _ = wf.getparams()
        frames = wf.readframes(n_frames)

        audio_array = np.frombuffer(frames, dtype=np.int16)
        if n_channels == 2:
            audio_array = audio_array.reshape(-1, 2).mean(axis=1)
        
        amplitude = np.abs(audio_array)
        ref = 32768  # Max 16-bit signed integer value
        amplitude_dB = 20 * np.log10(np.where(amplitude == 0, np.finfo(float).eps, amplitude) / ref)
        threshold_dB = -20
        non_silence = amplitude_dB > threshold_dB
        non_silence_duration = np.sum(non_silence) / framerate

        return jsonify(duration=non_silence_duration)
    except wave.Error as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run()
