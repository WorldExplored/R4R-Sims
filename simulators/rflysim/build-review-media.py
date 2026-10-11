"""Create review videos from preserved native PNGs; never infer acquisition time."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import imageio_ffmpeg
from PIL import Image


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        while block := source.read(8 * 1024 * 1024):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    version = subprocess.run([ffmpeg, '-version'], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    font = Path('/System/Library/Fonts/Supplemental/Arial.ttf')
    if not font.exists():
        raise FileNotFoundError('Review caption font unavailable: ' + str(font))
    result = {'method': 'All saved frames, constant 10fps playback, no audio, H264 review compression',
              'timing_limit': 'Playback uses frame ordinal, not acquisition or receiver timestamps. Native PNGs and raw clocks remain scientific evidence.',
              'ffmpeg': version, 'ffmpeg_sha256': sha(Path(ffmpeg)), 'videos': []}
    for name, relative, suffix, caption in [
        ('A1', 'A1', 'INVALID-ROTATIONS-short-capture', 'A1 native RGB / INVALID rotations, short capture / playback 10 fps'),
        ('A2', 'A2', 'INVALID-ROTATIONS', 'A2 native RGB / INVALID rotations / playback 10 fps'),
        ('B2', 'B2/rgb', 'mounted-RGB-waypoint-repeat', 'B2 mounted native RGB / waypoint repeat / playback 10 fps')]:
        root = args.input / relative
        rows = [json.loads(line) for line in (root / 'camera.jsonl').read_text().splitlines()]
        frames = [r for r in rows if r['kind'] == 'frame']
        inputs = []
        for index, row in enumerate(frames):
            if row['frame_id'] != index or row['path'] != 'frames/frame-%06d.png' % index:
                raise ValueError('Source frame sequence is not contiguous')
            source = root / row['path']
            with Image.open(source) as im:
                if im.size != (640, 480):
                    raise ValueError('Unexpected native resolution')
                im.verify()
            inputs.append({'path': str(source.resolve()), 'bytes': source.stat().st_size, 'sha256': sha(source)})
        caption_file = args.output / (name + '-caption.txt')
        caption_file.write_text(caption)
        video = args.output / (name + '-' + suffix + '.mp4')
        video_filter = 'pad=iw:ih+40:0:0:color=black,drawtext=fontfile=%s:textfile=%s:x=8:y=h-30:fontsize=14:fontcolor=white' % (font, caption_file.resolve())
        command = [ffmpeg, '-hide_banner', '-framerate', '10', '-start_number', '0', '-i',
                   str(root.resolve() / 'frames/frame-%06d.png'), '-frames:v', str(len(frames)),
                   '-vf', video_filter, '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                   '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(video.resolve())]
        encode = subprocess.run(command, capture_output=True, text=True, timeout=180)
        (args.output / (name + '-encode.log')).write_text(encode.stderr)
        if encode.returncode != 0:
            raise RuntimeError('FFmpeg encoding failed, exit%d: %s' % (encode.returncode, name))
        decode_cmd = [ffmpeg, '-hide_banner', '-i', str(video.resolve()), '-an', '-f', 'null', '-', '-progress', 'pipe:1', '-nostats']
        decode = subprocess.run(decode_cmd, capture_output=True, text=True, timeout=120)
        (args.output / (name + '-decode.log')).write_text(decode.stderr + '\n' + decode.stdout)
        counts = re.findall(r'^frame=(\d+)$', decode.stdout, re.M)
        if decode.returncode != 0 or not counts or int(counts[-1]) != len(frames):
            raise RuntimeError('Full video decode/count check failed: ' + name)
        preview = args.output / (name + '-decoded-middle.png')
        seek_s = (len(frames) // 2) / 10
        subprocess.run([ffmpeg, '-hide_banner', '-ss', str(seek_s), '-i', str(video.resolve()), '-frames:v', '1', str(preview)], capture_output=True, timeout=30, check=True)
        result['videos'].append({'name': name, 'file': str(video.resolve()), 'bytes': video.stat().st_size,
            'sha256': sha(video), 'frame_count': len(frames), 'playback_fps': 10,
            'playback_duration_s': len(frames) / 10, 'source_receiver_span_s': frames[-1]['receiver_monotonic_s'] - frames[0]['receiver_monotonic_s'],
            'native_resolution': [640, 480], 'video_resolution': [640, 520], 'annotation': '40px caption below image, native pixels not cropped',
            'includes_warmup': True, 'warmup_frames': sum(r['warmup'] for r in frames),
            'rotation_test_status': 'invalid authored degree-to-radian conversion' if name.startswith('A') else 'mounted camera, zero commanded relative rotation',
            'full_decode_exit': decode.returncode, 'decoded_frames': int(counts[-1]), 'encode_exit': encode.returncode,
            'encode_command': command, 'decode_command': decode_cmd, 'source_frames': inputs})
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps([{k: v for k, v in x.items() if k in ['name', 'frame_count', 'playback_duration_s', 'source_receiver_span_s', 'bytes']} for x in result['videos']], indent=2))


if __name__ == '__main__':
    main()
