import os
import librosa
import numpy as np
import soundfile as sf
from scipy.spatial.distance import cdist
from fastdtw import fastdtw
from pydub import AudioSegment

def convert_to_wav(file, out_dir):
    output_path = os.path.join(out_dir, "converted.wav")
    with open(output_path, 'wb') as f:
        f.write(file.read())
        
    return output_path


def sync_audio(file1, file2):
    try:
        file1_path = file1.name
        wav1 = convert_to_wav(file1, os.path.dirname(file1_path))
        wav2 = convert_to_wav(file2, os.path.dirname(file1_path))

        y1, sr1 = librosa.load(wav1)
        y2, sr2 = librosa.load(wav2, sr=sr1)

        mfcc1 = librosa.feature.mfcc(y=y1, sr=sr1, n_mfcc=13)
        mfcc2 = librosa.feature.mfcc(y=y2, sr=sr1, n_mfcc=13)


        D = cdist(mfcc1.T, mfcc2.T, metric='euclidean')
        distance, path = fastdtw(mfcc1.T, mfcc2.T)

        first_match = path[0][0]
        offset_samples = int(first_match * 512)

        if offset_samples < len(y1):
            y1_sync = y1[offset_samples:]
        else:
            y1_sync = np.array([])

        wav_output_path = os.path.join(os.path.dirname(file1_path), "synced_audio.wav")
        sf.write(wav_output_path, y1_sync, sr1)

        mp3_output_path = os.path.join(os.path.dirname(file1_path), "synced_audio.mp3")
        audio = AudioSegment.from_wav(wav_output_path)
        audio.export(mp3_output_path, format="mp3", bitrate="192k")

        os.remove(wav_output_path)
        os.remove(wav2)

    except Exception as e:
        print(f"bazinga: {str(e)}")

        

file_path1 = 'audio.mp3'
file_path2 = 's.mp3'
with open(file_path1, 'rb') as file1, open(file_path2, 'rb') as file2:
    sync_audio(file1, file2)
