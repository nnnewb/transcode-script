# 批量转码脚本

## 为啥写这玩意儿

收藏的视频太多了，搭建好的emby对某些视频容器会播放出问题，于是写个脚本控制转码。

## 用途

发现指定目录（包括子目录）下的视频，通过指定参数进行转码，但不会由低码率转高码率。

## 使用方法

```
Usage: transcode [OPTIONS]

Options:
  -i, --input-file FILE           指定输入的文件或目录。
  -d, --discover DIRECTORY        指定要主动发现输入文件的目录。
  -o, --out-dir DIRECTORY         指定输出的目录。未指定则输出至源文件目录下。
  -c:v, --vcodec [h264_amf|h264_nvenc|h264_qsv|libx264|libx264rgb|hevc_amf|hevc_nvenc|hevc_qsv|libx265]
                                  指定使用视频编码器。
  -c:a, --acodec [aac]            指定使用音频编码器。
  --hwaccel [dxva2|d3d11va|cuda|qsv|cuvid]
                                  选择使用的硬件加速方式。
  --container [mp4|mkv]           指定视频封装容器。
  --move-origin DIRECTORY         转码完成或，移动原始文件到指定目录。
  --help                          Show this message and exit.
```

## 转码规则

### 比特率计算

比特率计算公式

|质量|公式|
|---|---|
|极低|`(width * height * 3) / 4`|
|低|`(width * height * 3) / 2`|
|中|`(width * height * 3)`|
|高|`(width * height * 3) * 2`|
|极高|`(width * height * 3) * 4`|


如果原视频比特率低于计算的比特率则无条件选择源视频比特率，这是为了防止比特率低转高造成体积膨胀且无益于视频质量。

如果原视频比特率高于计算的比特率则由高转低。

### movflags

对所有视频都会添加`-movflags +faststart`。

### 编码方式

可以自己改 config.yml 加入其他编码器，我挑了几个常用的放进去。默认会使用`h264_amf`转码，因为**AMD YES**。

### 封装容器

允许 mkv 和 mp4，反正存储分发都够了。想要其他容器改config.yml就是。

### 硬件加速

默认 `dxva2` 加速。有需要改config.yml。

### 输出文件命名

输出文件会重命名成以下格式。

`<源文件名>-[<分辨率>]-[<视频编码器>]-[<音频编码器>]-[<视频码率>].<输出容器后缀名>`

举例来说，使用如下参数转码会输出这样的文件。

`transcode -c:a aac -c:v hevc_amf -container mp4 -i ./a.flv -o ./`

输出文件

`a-[1280x720]-[hevc_amf]-[aac]-[1233kbps].mp4`
