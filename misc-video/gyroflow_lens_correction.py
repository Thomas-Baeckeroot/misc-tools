#!/usr/bin/env python3
"""Extrait une frame d'une vidéo RunCam Thumb2 et applique la correction de distorsion Gyroflow."""

import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

# Paramètres Gyroflow (Runcam Thumb2 wide, 3840x2160, calibré par Eddy)
K = np.array([
    [1818.428733127828, 0, 1919.392429274946],
    [0, 1818.800090510473, 1144.922449884292],
    [0, 0, 1]
])

D = np.array([
    [0.1349079411166253],
    [-0.2008114276310018],
    [0.1734474039997024],
    [-0.06331740532773920]
])


def extract_frame(video_path, timestamp):
    """Extrait une frame via ffmpeg et la retourne en array numpy."""
    cmd = [
        "ffmpeg", "-ss", timestamp, "-i", str(video_path),
        "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f"Erreur ffmpeg:\n{result.stderr.decode()}", file=sys.stderr)
        sys.exit(1)
    img_array = np.frombuffer(result.stdout, dtype=np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_COLOR)


def undistort(img):
    """Applique la correction fisheye avec les paramètres Gyroflow."""
    h, w = img.shape[:2]
    # balance=1.0 → garde tous les pixels (bordures noires acceptées, crop manuel ensuite)
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
        K, D, (w, h), np.eye(3), balance=1.0
    )
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        K, D, np.eye(3), new_K, (w, h), cv2.CV_16SC2
    )
    return cv2.remap(img, map1, map2, cv2.INTER_LANCZOS4)


def main():
    parser = argparse.ArgumentParser(
        description="Extraction et correction de distorsion pour RunCam Thumb2."
    )
    parser.add_argument("video", help="Fichier vidéo source (MP4)")
    parser.add_argument("timestamp", help="Timecode à extraire (ex: 00:03:02 ou 3:02)")
    parser.add_argument("-o", "--output", help="Fichier PNG de sortie (défaut: auto)")
    args = parser.parse_args()

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Fichier introuvable : {video_path}", file=sys.stderr)
        sys.exit(1)

    # Nom de sortie par défaut : VIDEO_TIMESTAMPt_corrected.png
    if args.output:
        output_path = Path(args.output)
    else:
        ts_label = args.timestamp.replace(":", "m", 1).replace(":", "s", 1)
        output_path = video_path.with_name(f"{video_path.stem}_{ts_label}_corrected.png")

    print(f"Extraction de la frame à {args.timestamp}...")
    img = extract_frame(video_path, args.timestamp)

    print("Correction de la distorsion fisheye...")
    corrected = undistort(img)

    cv2.imwrite(str(output_path), corrected)
    print(f"Résultat : {output_path}")


if __name__ == "__main__":
    main()
