import os
import re
import shutil
from pathlib import Path

import ffmpeg

from transcode.config import config


def probe_stream(path: Path, stream_type: str = 'video'):
    probe = ffmpeg.probe(filename=str(path))
    return next((stream for stream in probe['streams'] if stream['codec_type'] == stream_type), None)


def detect_video_best_bitrate(path: Path, quality: str = 'medium', prefer_src: bool = True) -> int:
    """
    detect best bit rate for video encoding. Source stream bit
    rate lower then calculated bit rate will choose source bit rate
    prevent low-to-high trans code.

    best bit rate calculation rules:

    VERY-LOW-QUALITY        (w * h * 3) / 4
    LOW-QUALITY             (w * h * 3) / 2
    MEDIUM-QUALITY          (w * h * 3)
    HIGH-QUALITY            (w * h * 3) * 2
    ULTRA-HIGH-QUALITY      (w * h * 3) * 4

    :param path: input source path
    :param quality: oen of very-low, low, medium, high, higher
    :param prefer: one of source, calc
    :return: best bit rate
    """
    bit_rate_rules = {
        'very-low': lambda w, h: (w * h * 3) / 4,
        'low': lambda w, h: (w * h * 3) / 2,
        'medium': lambda w, h: (w * h * 3),
        'high': lambda w, h: (w * h * 3) * 2,
        'ultra-high': lambda w, h: (w * h * 3) * 4,
    }
    video_stream = probe_stream(path)
    width = int(video_stream['width'])
    height = int(video_stream['height'])

    calc_bitrate = bit_rate_rules[quality](width, height)
    src_bitrate = int(video_stream['bit_rate']) if 'bit_rate' in video_stream else calc_bitrate

    if src_bitrate < calc_bitrate:
        return src_bitrate if prefer_src else calc_bitrate
    return calc_bitrate


def discover_source_media(path: Path):
    pattern = '|'.join(config.detect_source_container)
    pattern = r'\.({})$'.format(pattern)
    pattern = re.compile(pattern)
    for root, dirs, files in os.walk(path, topdown=True):
        for file in files:
            if pattern.findall(file):
                yield Path(f'{root}/{file}')
        for d in dirs:
            for f in discover_source_media(Path(f'{root}/{d}')):
                yield f


def move_origin(src: Path, dst: Path):
    counter = 0
    while dst.exists():
        dst = dst.with_name(f'{src.stem}.{counter}.{src.suffix}')
        counter += 1
    return shutil.move(src, dst)


def detect_video_best_resolution(path: Path):
    video_stream = probe_stream(path)
    return int(video_stream['width']), int(video_stream['height'])
