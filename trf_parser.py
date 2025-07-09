#!/usr/bin/env python3
"""
Simple parser for VidStab TRF (transform) binary files
Usage: python3 trf_parser.py file1.trf [file2.trf]
"""

import logging
import math
import os
import struct
import sys

logging.basicConfig(
    # filename=utils.get_home() + "/tmp/logfile.log",
    level=logging.DEBUG,
    format='%(asctime)s\t%(levelname)s\t%(filename)s:%(lineno)d\t%(message)s')
log = logging.getLogger("sort_photos.py")  # %(name)s


def export_to_ascii(transforms, output_file):
    """Export transforms to ASCII format (similar to old TRF format)"""
    with open(output_file, 'w') as f:
        # Write header
        f.write(f"# VidStab transform data\n")
        f.write(f"# Frame count: {len(transforms)}\n")

        # Write transform data
        for i, t in enumerate(transforms):
            # Format: frame_num dx dy da [other_params]
            f.write(f"{i} {t[0]:.6f} {t[1]:.6f} {t[2]:.6f}\n")


def detect_trf_format(filename):
    """Detect if TRF file is ASCII or binary format"""
    with open(filename, 'rb') as f:
        first_bytes = f.read(4)

    # Check for binary magic number
    if first_bytes == b'TRF1':
        return 'binary'

    # Try to decode as ASCII
    try:
        with open(filename, 'r') as f:
            first_line = f.readline()
            # ASCII format usually starts with comments or numbers
            if first_line.startswith('#') or first_line[0].isdigit():
                return 'ascii'
    except:
        pass

    return 'unknown'


def parse_ascii_trf(filename):
    """Parse ASCII format TRF file"""
    transforms = []

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments
            if line.startswith('#') or not line:
                continue

            parts = line.split()
            if len(parts) >= 4:  # frame_num dx dy da
                transforms.append([
                    float(parts[1]),  # dx
                    float(parts[2]),  # dy
                    float(parts[3])  # da
                ])

    return transforms


def parse_trf_header(data):
    """Parse TRF file header"""
    if len(data) < 20:
        return None

    # Check magic number
    magic = data[:4].decode('ascii', errors='ignore')
    if magic != 'TRF1':
        log.info(f"Warning: Unexpected magic number: {magic}")
        return None

    # Try to parse header structure (this is reverse-engineered)
    # TRF format may vary, this is an educated guess
    try:
        header_info = {
            'magic': magic,
            'version': struct.unpack('<I', data[4:8])[0],
            'frame_count': struct.unpack('<I', data[8:12])[0],
            'data_size': struct.unpack('<I', data[12:16])[0],
        }
        return header_info
    except:
        return {'magic': magic, 'estimated_frames': len(data) // 24}


def analyze_trf_data(data, header):
    """Extract transformation data from TRF file"""
    # Skip header (estimated 20 bytes)
    data_start = 20

    if header and 'frame_count' in header:
        frame_count = header['frame_count']
    else:
        # Estimate frame count based on file size
        # Each transform typically has 6 floats (24 bytes): dx, dy, da, zoom, etc.
        frame_count = (len(data) - data_start) // 24

    transforms = []

    try:
        for i in range(frame_count):
            offset = data_start + i * 24
            if offset + 24 > len(data):
                break

            # Try to unpack as 6 floats (little-endian)
            values = struct.unpack('<6f', data[offset:offset + 24])
            transforms.append(values[:3])  # Take first 3: dx, dy, da
    except:
        # Fallback: try different structures
        try:
            for i in range(frame_count):
                offset = data_start + i * 12  # 3 floats only
                if offset + 12 > len(data):
                    break
                values = struct.unpack('<3f', data[offset:offset + 12])
                transforms.append(values)
        except:
            log.info("Could not parse transform data")
            return []

    return transforms


def calculate_stability_metrics(transforms):
    """Calculate stability metrics from transform data"""
    if not transforms:
        return {}

    dx_values = [t[0] for t in transforms]
    dy_values = [t[1] for t in transforms]
    da_values = [t[2] for t in transforms if len(t) > 2]

    def rms(values):
        return math.sqrt(sum(x * x for x in values) / len(values))

    def mean_abs(values):
        return sum(abs(x) for x in values) / len(values)

    metrics = {
        'frame_count': len(transforms),
        'dx_rms': rms(dx_values),
        'dy_rms': rms(dy_values),
        'dx_mean_abs': mean_abs(dx_values),
        'dy_mean_abs': mean_abs(dy_values),
        'dx_range': (min(dx_values), max(dx_values)),
        'dy_range': (min(dy_values), max(dy_values)),
    }

    if da_values:
        metrics.update({
            'da_rms': rms(da_values),
            'da_mean_abs': mean_abs(da_values),
            'da_range': (min(da_values), max(da_values)),
        })

    # Overall instability index
    instability = metrics['dx_rms'] + metrics['dy_rms']
    if 'da_rms' in metrics:
        instability += metrics['da_rms']
    metrics['instability_index'] = instability

    return metrics


def analyze_trf_file(filename):
    """Analyze a single TRF file"""
    if not os.path.exists(filename):
        log.info(f"Error: File {filename} not found")
        return None

    log.info(f"=== Analysis of {filename} ===")

    # Get file size
    file_size = os.path.getsize(filename)
    log.info(f"File size: {file_size:,} bytes ({file_size / 1024 / 1024:.1f} MB)")

    # Detect format
    file_format = detect_trf_format(filename)
    log.info(f"File format: {file_format}")

    if file_format == 'ascii':
        transforms = parse_ascii_trf(filename)
    else:  # binary or unknown, try binary
        with open(filename, 'rb') as f:
            data = f.read()

        # Parse header
        header = parse_trf_header(data)
        if header:
            log.info(f"Magic: {header['magic']}")
            if 'frame_count' in header:
                log.info(f"Frame count (from header): {header['frame_count']}")

        # Try to detect the actual structure
        # Common structures: 24 bytes (6 floats), 32 bytes (8 floats), 48 bytes (12 floats)
        possible_sizes = [24, 32, 48, 52, 64]
        header_sizes = [16, 20, 24, 32]  # Possible header sizes

        best_config = None
        for header_size in header_sizes:
            for record_size in possible_sizes:
                # Calculate expected frame count
                data_size = file_size - header_size
                if data_size % record_size == 0:
                    frame_count = data_size // record_size
                    # Sanity check: reasonable frame count
                    if 100 < frame_count < 1000000:
                        log.info(f"  Testing: header={header_size}B, record={record_size}B → {frame_count:,} frames")

                        # Try to parse a few frames to validate
                        valid = True
                        test_transforms = []
                        for i in range(min(10, frame_count)):
                            offset = header_size + i * record_size
                            if offset + record_size > len(data):
                                valid = False
                                break

                            # Try to parse as floats
                            num_floats = record_size // 4
                            try:
                                values = struct.unpack(f'<{num_floats}f', data[offset:offset + record_size])
                                # Basic sanity check on values
                                if any(math.isnan(v) or abs(v) > 10000 for v in values[:3]):
                                    valid = False
                                    break
                                test_transforms.append(values[:3])
                            except:
                                valid = False
                                break

                        if valid and test_transforms:
                            # Calculate RMS to check if values are reasonable
                            dx_rms = math.sqrt(sum(t[0] ** 2 for t in test_transforms) / len(test_transforms))
                            if dx_rms < 1000:  # Reasonable threshold
                                best_config = (header_size, record_size, frame_count)
                                log.info(f"    → Valid configuration found!")
                                break

            if best_config:
                break

        if best_config:
            header_size, record_size, frame_count = best_config
            log.info("")
            log.info("Detected structure:")
            log.info(f"  Header size: {header_size} bytes")
            log.info(f"  Record size: {record_size} bytes ({record_size // 4} floats per frame)")
            log.info(f"  Frame count: {frame_count:,}")

            # Parse all transforms (or a subset for large files)
            transforms = []
            max_frames_to_parse = min(frame_count, 100000)  # Limit for memory

            for i in range(max_frames_to_parse):
                offset = header_size + i * record_size
                if offset + record_size > len(data):
                    break

                num_floats = record_size // 4
                try:
                    values = struct.unpack(f'<{num_floats}f', data[offset:offset + record_size])
                    # Take first 3 values (dx, dy, da)
                    transform = list(values[:3])

                    # Validate and fix extreme values
                    for j in range(len(transform)):
                        if math.isnan(transform[j]) or abs(transform[j]) > 10000:
                            transform[j] = 0.0  # Reset extreme values

                    transforms.append(transform)
                except:
                    break

            if len(transforms) < frame_count:
                log.info(f"  (Parsed {len(transforms):,} frames for analysis)")
        else:
            log.info("")
            log.info("Could not detect valid structure, falling back to default parsing...")
            transforms = analyze_trf_data(data, header)

    if transforms:
        log.info("")
        log.info(f"Successfully parsed {len(transforms):,} transforms")

        # Filter out invalid values for metrics
        valid_transforms = []
        for t in transforms:
            if len(t) >= 3 and all(not math.isnan(v) and abs(v) < 10000 for v in t[:3]):
                valid_transforms.append(t)

        if valid_transforms:
            log.info(
                f"Valid transforms: {len(valid_transforms):,} ({len(valid_transforms) / len(transforms) * 100:.1f}%)")

            # Calculate metrics only on valid transforms
            metrics = calculate_stability_metrics(valid_transforms)

            log.info("")
            log.info("Stability Metrics:")
            log.info(f"  Horizontal (dx): RMS={metrics['dx_rms']:.6f}, Mean abs={metrics['dx_mean_abs']:.6f}")
            log.info(f"  Vertical (dy): RMS={metrics['dy_rms']:.6f}, Mean abs={metrics['dy_mean_abs']:.6f}")

            if 'da_rms' in metrics:
                log.info(f"  Angular (da): RMS={metrics['da_rms']:.6f}, Mean abs={metrics['da_mean_abs']:.6f}")

            log.info(f"  Instability Index: {metrics['instability_index']:.6f} (lower = better)")

            # Show sample of valid data
            log.info("")
            log.info("Sample transforms (first 5 valid):")
            for i, t in enumerate(valid_transforms[:5]):
                log.info(f"  Frame {i}: dx={t[0]:.4f}, dy={t[1]:.4f}, da={t[2]:.4f}")

            # Add frame count to metrics
            metrics['frame_count'] = len(transforms)
            metrics['valid_frame_count'] = len(valid_transforms)

            return metrics
        else:
            log.info("No valid transform data found")
            return None
    else:
        log.info("Could not parse transform data")
        return None


def compare_trf_files(file1, file2):
    """Compare two TRF files"""
    log.info("")
    log.info("=" * 50)
    log.info("COMPARISON SUMMARY")
    log.info("=" * 50)

    metrics1 = analyze_trf_file(file1)
    log.info("")
    metrics2 = analyze_trf_file(file2)

    if metrics1 and metrics2:
        log.info("")
        log.info("=== Comparison Results ===")
        log.info(f"Frame count: {metrics1['frame_count']} vs {metrics2['frame_count']}")

        # Compare instability indices
        if metrics1['instability_index'] < metrics2['instability_index']:
            better = file1
            diff = metrics2['instability_index'] - metrics1['instability_index']
        else:
            better = file2
            diff = metrics1['instability_index'] - metrics2['instability_index']

        log.info("")
        log.info("Instability Index:")
        log.info(f"  {file1}: {metrics1['instability_index']:.6f}")
        log.info(f"  {file2}: {metrics2['instability_index']:.6f}")
        log.info(f"  Difference: {diff:.6f}")
        log.info(f"  Better file: {better}")

        improvement_pct = (diff / max(metrics1['instability_index'], metrics2['instability_index'])) * 100
        log.info(f"  Improvement: {improvement_pct:.1f}%")


def main():
    if len(sys.argv) < 2:
        log.info("Usage: python3 trf_parser.py <command> [arguments]")
        log.info("")
        log.info("Commands:")
        log.info("  analyse <file.trf>           Analyze a single TRF file")
        log.info("  compare <file1.trf> <file2.trf>  Compare two TRF files")
        log.info("")
        log.info("This script analyzes VidStab TRF binary files and extracts")
        log.info("transformation data to evaluate stabilization quality.")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "analyse" or command == "analyze":  # Support both spellings
        if len(sys.argv) < 3:
            log.info("Error: 'analyse' command requires a TRF file")
            log.info("Usage: python3 trf_parser.py analyse <file.trf>")
            sys.exit(1)

        file1 = sys.argv[2]
        analyze_trf_file(file1)

    elif command == "compare":
        if len(sys.argv) < 4:
            log.info("Error: 'compare' command requires two TRF files")
            log.info("Usage: python3 trf_parser.py compare <file1.trf> <file2.trf>")
            sys.exit(1)

        file1 = sys.argv[2]
        file2 = sys.argv[3]
        compare_trf_files(file1, file2)

    else:
        log.info(f"Error: Unknown command '{command}'")
        log.info("")
        log.info("Available commands:")
        log.info("  analyse - Analyze a single TRF file")
        log.info("  compare - Compare two TRF files")
        log.info("")
        log.info("Run 'python3 trf_parser.py' for full usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
