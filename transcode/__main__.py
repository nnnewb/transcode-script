import sys
from logging import basicConfig, getLogger
from pathlib import PurePath, Path
from typing import Sequence

import click
import ffmpy
from ffmpeg import Error

from transcode.config import config
from transcode.pypath import PyPath
from transcode.util import detect_video_best_bitrate, discover_source_media, move_origin as move_origin_, \
    detect_video_best_resolution

basicConfig(level='DEBUG', format='%(levelname)7s - %(asctime)18s - %(name)8s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

logger = getLogger('transcode')


@click.command()
@click.option('-i', '--input-file', type=PyPath(dir_okay=False, exists=True), multiple=True, help="指定输入的文件或目录。")
@click.option('-d', '--discover', type=PyPath(exists=True, file_okay=False, dir_okay=True), help='指定要主动发现输入文件的目录。')
@click.option('-o', '--out-dir', type=PyPath(file_okay=False, exists=True), help="指定输出的目录。未指定则输出至源文件目录下。")
@click.option('-c:v', '--vcodec', type=click.Choice(config.available_video_codec), default='h264_amf',
              help="指定使用视频编码器。")
@click.option('-c:a', '--acodec', type=click.Choice(config.available_audio_codec), default='aac', help="指定使用音频编码器。")
@click.option('--hwaccel', type=click.Choice(config.available_hardware_accelerate_method), default='dxva2',
              help='选择使用的硬件加速方式。')
@click.option('--container', type=click.Choice(config.available_container), default='mp4', help="指定视频封装容器。")
@click.option('--move-origin', type=PyPath(file_okay=False, dir_okay=True, exists=True), help='转码完成或，移动原始文件到指定目录。')
def main(input_file: Sequence[PurePath], discover: PurePath, out_dir: PurePath, vcodec: str, acodec: str,
         hwaccel: str, container: str, move_origin: PurePath):
    sources = input_file
    if len(sources) == 0:
        if not discover:
            click.echo(file=sys.stderr, message='应该至少指定一个输入文件。')
        else:
            sources = [f for f in discover_source_media(Path(discover))]

    for src in sources:
        try:
            bit_rate = detect_video_best_bitrate(Path(src))
            resolution = detect_video_best_resolution(Path(src))
            dst = None
            if out_dir:
                dst = PurePath(f'{out_dir}/{src.stem}'
                               f'-[{resolution[0]}x{resolution[1]}]'
                               f'-[{vcodec}]'
                               f'-[{acodec}]'
                               f'-[{int(bit_rate / 1024)}kbps]'
                               f'.{container}')
            else:
                dst = PurePath(f'{src.parent}/{src.stem}.{container}')

            ff = ffmpy.FFmpeg(
                global_options=[f'-hwaccel {hwaccel}', '-y'],
                inputs={
                    str(src): None
                }, outputs={
                    str(dst): [
                        '-c:v', f'{vcodec}',
                        '-c:a', f'{acodec}',
                        '-b:v', f'{bit_rate}',
                        '-profile_tier', 'high',
                        '-movflags', '+faststart'
                    ]
                })

            logger.info(f'转码指令：{ff.cmd}')
            ffmpeg_log = open('ffmpeg-stderr.txt', mode='w+', encoding='utf-8')
            ff.run(stderr=ffmpeg_log)

            if move_origin:
                move_origin_(Path(src), Path(move_origin.joinpath(src.name)))
        except Error as e:
            logger.error(f'无法处理的文件：{src}')


if __name__ == "__main__":
    main()
