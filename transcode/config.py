import yaml


class Config:
    def __init__(self):
        self._cfg = yaml.load(open('config.yml', mode='r', encoding='utf-8'), Loader=yaml.SafeLoader)

    @property
    def available_container(self):
        return self._cfg['container']

    @property
    def available_video_codec(self):
        return self._cfg['video_codec']

    @property
    def available_audio_codec(self):
        return self._cfg['audio_codec']

    @property
    def available_hardware_accelerate_method(self):
        return self._cfg['hardware_accelerate']

    @property
    def detect_source_container(self):
        return self._cfg['detect_source']


config = Config()
