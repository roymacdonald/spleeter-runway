import runway
import librosa

import base64
from io import BytesIO as IO
import soundfile

from spleeter.utils.audio.adapter import get_default_audio_adapter
from spleeter.separator import Separator


class audio(runway.BaseType):
    def __init__(
        self,
        description=None,
        channels=1,
        default_output_format=None
    ):
        super(audio, self).__init__('audio', description=description)
        self.channels = channels

    def deserialize(self, value):
        audio = value[value.find(",")+1:]
        audio = base64.decodestring(audio.encode('utf8'))
        buffer = IO(audio)
        data, sr = soundfile.read(buffer)
        return data, sr

    def serialize(self, value):
        data, sr = value
        buffer = IO()
        soundfile.write(buffer, data, sr, format='WAV', subtype='PCM_16')
        body = base64.b64encode(buffer.getvalue()).decode('utf8')
        return 'data:audio/wav;base64,{body}'.format(body=body)

    def to_dict(self):
        ret = super(audio, self).to_dict()
        ret['channels'] = self.channels
        return ret
@runway.setup(options={"stems": runway.category(description="Number of stems to extract",
                                                choices=['2', '4', '5'],
                                                default='2')})
def setup(opts):
    return Separator('spleeter:' + opts['stems'] + 'stems')


from spleeter.utils.audio.adapter import get_default_audio_adapter

@runway.command('split', inputs={'audio': audio}, outputs={'vocals': audio})
def synth(separator, inputs):
    soundfile.write('temp.wav', inputs['audio'][0], inputs['audio'][1], format='WAV', subtype='PCM_32')
    audio_loader = get_default_audio_adapter()
    sample_rate = 44100
    waveform, _ = audio_loader.load('temp.wav', sample_rate=sample_rate)
    prediction = separator.separate(waveform)
    return {
        'vocals': (prediction['vocals'], sample_rate)
    }


if __name__ == "__main__":
    runway.run()

