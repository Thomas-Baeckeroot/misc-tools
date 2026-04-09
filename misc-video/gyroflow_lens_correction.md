# Gyroflow Lens Correction Tool

## Context

Script to extract a frame from a RunCam Thumb 2 drone video at a given timecode and apply lens distortion correction using the exact Gyroflow calibration profile (OpenCV fisheye model).

## Workflow

1. Extract frame from MP4 at timecode using `ffmpeg`
2. Apply fisheye undistortion using OpenCV with Gyroflow calibration parameters
3. Output PNG for manual rotation + crop in GIMP

## Gyroflow Calibration Profile (Runcam Thumb2 wide, 3840x2160, calibrated by Eddy)

- **Model**: OpenCV fisheye (4 coefficients), asymmetrical
- **Pixel focal length**: `fx=1818.428733127828`, `fy=1818.800090510473`
- **Focal center**: `cx=1919.392429274946`, `cy=1144.922449884292`
- **Distortion coefficients**: `[0.1349079411166253, -0.2008114276310018, 0.1734474039997024, -0.0633174053277392]`

## Key decisions

- `balance=1.0` in `estimateNewCameraMatrixForUndistortRectify` to keep all pixels (black borders accepted — user crops manually in GIMP after rotation)
- `cv2.INTER_LANCZOS4` for best quality interpolation
- Output format: PNG (lossless)

## Environment

- Python venv in `.venv` (`source .venv/bin/activate`)
- Dependencies: `opencv-python`, `numpy`
- FFmpeg required on system (`brew install ffmpeg`)

## FFmpeg-only alternative (approximate, for quick use)

```bash
ffmpeg -ss HH:MM:SS -i input.MP4 -frames:v 1 \
  -vf "pad=iw+800:ih+800:(ow-iw)/2:(oh-ih)/2:black,lenscorrection=k1=-0.34:k2=0.10" \
  -qmin 1 -q:v 1 output.png
```

These k1/k2 values are empirical approximations — the OpenCV fisheye method is more accurate.
