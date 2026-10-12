#!/bin/bash
# Build a cut: picture (engine.py) + sound/captions (audio.py), then grade, mux and web encodes.
# Usage: FFMPEG=/path/to/ffmpeg ./build.sh <main|c30|c15|vertical>
set -euo pipefail
cd "$(dirname "$0")"
CUT=$1; OUT=../work/out; mkdir -p "$OUT"
AUD=$CUT; [ "$CUT" = vertical ] && AUD=main
python3 engine.py "$CUT" "$OUT/$CUT.picture.mp4"
[ -f "$OUT/$AUD.wav" ] || python3 audio.py "$AUD" "$OUT/$AUD.wav"
# Grade: navy shadows, blue-biased highlights, -8% saturation, soft vignette, fine grain
GRADE="eq=saturation=0.92:contrast=1.03:gamma=0.98,colorbalance=rs=-0.03:bs=0.05:rm=-0.01:bm=0.02,vignette=angle=PI/5:mode=forward,noise=alls=3:allf=t"
"$FFMPEG" -v error -y -i "$OUT/$CUT.picture.mp4" -i "$OUT/$AUD.wav" -vf "$GRADE" \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -profile:v high -c:a aac -b:a 256k -movflags +faststart -shortest "$OUT/$CUT.master.mp4"
echo "master: $OUT/$CUT.master.mp4"
