"""
build_audio.py -- tao ambient.mp3 va click.mp3 cho game.

Nguon (ca hai deu la CC0 / public domain, dung thuong mai tu do):
  ambient: "Cathedral in the forest (ambient loop)" - congusbongus
           https://opengameart.org/content/cathedral-in-the-forest-ambient-loop
  click  : "Interface Sounds" (glass_002.ogg) - Kenney
           https://opengameart.org/content/interface-sounds

Chay lai:  python scripts/build_audio.py
Can: ffmpeg, numpy.
"""

import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "assets" / "audio"
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("audio_src")


def decode(path: Path) -> np.ndarray:
    """Doc file audio bat ky -> numpy float32 mono, SR=44100."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "quiet", "-i", str(path),
         "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def write_wav(path: Path, data: np.ndarray) -> None:
    pcm = np.clip(data, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def loop_crossfade(x: np.ndarray, length: int, xfade: int) -> np.ndarray:
    """Cat x thanh vong lap dai `length` mau, moi noi bang crossfade equal-power.

    Thay cho fade-in/fade-out tuan tu: fade tuan tu tren file phat lap se tao
    mot khoang lang 4 giay o moi vong. Crossfade choan 2 giay dau va 2 giay
    cuoi len nhau nen vong lap lien mach, khong co choi, khong bi hut am.
    """
    if len(x) < length + xfade:
        raise ValueError("nguon qua ngan")
    y = x[:length].copy()
    t = np.linspace(0.0, 1.0, xfade, endpoint=False)
    fade_in = np.sin(t * np.pi / 2) ** 2      # equal power 0 -> 1
    fade_out = np.cos(t * np.pi / 2) ** 2     # equal power 1 -> 0
    y[:xfade] = x[:xfade] * fade_in + x[length:length + xfade] * fade_out
    return y


def db(x: float) -> float:
    return 20.0 * np.log10(max(x, 1e-12))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)

    # ---------- ambient ----------
    src = SRC / "forest_2.ogg"
    x = decode(src)
    print(f"ambient nguon: {len(x)/SR:.1f}s")

    length = 120 * SR      # 120 giay
    xfade = 2 * SR         # 2 giay crossfade o moi noi vong lap
    y = loop_crossfade(x, length, xfade)

    # chuan hoa dinh truoc khi encode, loudnorm se chinh muc do sau
    y = y / max(np.abs(y).max(), 1e-9) * 0.89
    write_wav(tmp / "ambient.wav", y)
    print(f"ambient sau cat: {len(y)/SR:.1f}s")

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(tmp / "ambient.wav"),
        "-af", "loudnorm=I=-22:TP=-3:LRA=11",
        "-c:a", "libmp3lame", "-b:a", "80k", "-ac", "1", "-ar", "44100",
        "-write_xing", "1",
        str(OUT / "ambient.mp3"),
    ], check=True)

    # ---------- click ----------
    c = decode(SRC / "kenney" / "Audio" / "glass_002.ogg")
    peak_i = int(np.abs(c).argmax())
    start = max(0, peak_i - int(0.004 * SR))       # giu 4ms pre-transient
    cut = c[start:]
    # cat khi da tat han (duoi -60 dB)
    env = np.abs(cut)
    thr = env.max() * 1e-3
    nz = np.where(env > thr)[0]
    cut = cut[: nz[-1] + 1]
    cut = np.concatenate([cut, np.zeros(int(0.025 * SR))])   # duoi lang cho encoder
    cut = cut / max(np.abs(cut).max(), 1e-9) * 0.5           # dinh -6 dBFS
    cut = np.concatenate([np.zeros(int(0.002 * SR)), cut])   # 2ms silent attack
    write_wav(tmp / "click.wav", cut)
    print(f"click: {len(cut)/SR*1000:.0f}ms, dinh {db(np.abs(cut).max()):.1f} dBFS")

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(tmp / "click.wav"),
        "-c:a", "libmp3lame", "-b:a", "96k", "-ac", "1", "-ar", "44100",
        str(OUT / "click.mp3"),
    ], check=True)

    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()


if __name__ == "__main__":
    main()
