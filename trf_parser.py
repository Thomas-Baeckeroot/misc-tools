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
        log.error(f"File {filename} not found")
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

        # Show hex dump of first 128 bytes for debugging
        log.debug("First 128 bytes of file (hex dump):")
        for i in range(0, min(128, len(data)), 16):
            hex_str = ' '.join(f'{b:02x}' for b in data[i:i + 16])
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i + 16])
            log.debug(f"  {i:04x}: {hex_str:<48} |{ascii_str}|")

        # Parse header
        header = parse_trf_header(data)
        if header:
            log.info(f"Magic: {header['magic']}")
            if 'frame_count' in header:
                log.warning(f"Frame count (from header): {header['frame_count']} - This seems incorrect!")

        # FIXME Below values are hard-coded for testing
        # Expected frames based on video duration
        # 4mn 35s @ 59.94 fps = 275.51s * 59.94 = ~16,514 frames
        expected_frames = 16514
        log.info(f"Expected frames for 4m35s @ 59.94fps: ~{expected_frames:,}")

        # Calculate what record size would make sense
        for header_size in [16, 20, 24, 32, 64]:
            record_size = (file_size - header_size) / expected_frames
            log.debug(f"If header={header_size}B: record size would be {record_size:.1f}B per frame")

        # Try to detect the actual structure
        possible_sizes = [24, 32, 48, 52, 64, 96, 128, 256, 512, 1024, 2048, 2752, 2756, 2760]
        header_sizes = [16, 20, 24, 32, 64, 128, 256]

        best_config = None
        all_configs = []

        log.debug("Testing different header/record size combinations...")

        for header_size in header_sizes:
            for record_size in possible_sizes:
                # Calculate expected frame count
                data_size = file_size - header_size
                if data_size % record_size == 0:
                    frame_count = data_size // record_size
                    # Keep track of all valid configurations
                    if 100 < frame_count < 1000000:
                        diff_frames = abs(frame_count - expected_frames)
                        all_configs.append((diff_frames, header_size, record_size, frame_count))

                        if diff_frames < 100:  # Close to expected
                            log.info(
                                f"  GOOD MATCH: header={header_size}B, record={record_size}B → {frame_count:,} frames (diff: {frame_count - expected_frames:+,})")

                        # Try to parse a few frames to validate
                        valid = True
                        test_transforms = []
                        num_test_frames = min(20, frame_count)

                        log.debug(
                            f"  Testing config: header={header_size}B, record={record_size}B → {frame_count:,} frames")

                        for i in range(num_test_frames):
                            offset = header_size + i * record_size
                            if offset + record_size > len(data):
                                valid = False
                                log.debug(f"    Failed: offset {offset} + {record_size} exceeds file size")
                                break

                            # Try to parse as floats
                            num_floats = min(record_size // 4, 16)
                            try:
                                values = struct.unpack(f'<{num_floats}f', data[offset:offset + num_floats * 4])

                                # Log first few values for debugging
                                if i < 3:
                                    log.debug(f"    Frame {i} first 6 floats: {values[:6]}")

                                # Basic sanity check on first 3 values (dx, dy, da)
                                if any(math.isnan(v) or abs(v) > 10000 for v in values[:3]):
                                    valid = False
                                    log.debug(f"    Failed: invalid values in frame {i}")
                                    break
                                test_transforms.append(values[:3])
                            except Exception as e:
                                valid = False
                                log.debug(f"    Failed to parse: {e}")
                                break

                        if valid and test_transforms:
                            # Calculate RMS to check if values are reasonable
                            dx_rms = math.sqrt(sum(t[0] ** 2 for t in test_transforms) / len(test_transforms))
                            dy_rms = math.sqrt(sum(t[1] ** 2 for t in test_transforms) / len(test_transforms))
                            log.debug(f"    RMS values: dx={dx_rms:.2f}, dy={dy_rms:.2f}")

                            if dx_rms < 1000 and dy_rms < 1000:  # Reasonable threshold
                                best_config = (header_size, record_size, frame_count)
                                if diff_frames < 10:  # Very close match
                                    log.info(f"    → EXCELLENT match! Using this configuration.")
                                    break
                                else:
                                    log.info(f"    → Valid configuration found!")

            if best_config and abs(best_config[2] - expected_frames) < 10:
                break

        # Show best configurations found
        if all_configs:
            log.info("")
            log.info("Top 5 configurations by frame count match:")
            for diff, h, r, f in sorted(all_configs)[:5]:
                log.info(f"  header={h}B, record={r}B → {f:,} frames (diff from expected: {f - expected_frames:+,})")

        if best_config:
            header_size, record_size, frame_count = best_config
            log.info("")
            log.info("Using detected structure:")
            log.info(f"  Header size: {header_size} bytes")
            log.info(f"  Record size: {record_size} bytes ({record_size // 4} floats per frame)")
            log.info(f"  Frame count: {frame_count:,}")

            # Log what might be in the large record
            if record_size > 48:
                log.info(f"  Note: Large record size ({record_size}B) suggests vidstab stores additional data")
                log.info(f"        Possible contents: motion vectors, feature points, confidence scores, etc.")

            # Parse all transforms (or a subset for large files)
            transforms = []
            max_frames_to_parse = min(frame_count, 100000)  # Limit for memory

            log.info("")
            log.info(f"Parsing {max_frames_to_parse:,} frames...")

            parse_errors = 0
            for i in range(max_frames_to_parse):
                offset = header_size + i * record_size
                if offset + record_size > len(data):
                    log.warning(f"Unexpected end of file at frame {i}")
                    break

                try:
                    # Just extract first 3 floats (dx, dy, da)
                    values = struct.unpack('<3f', data[offset:offset + 12])
                    transform = list(values)

                    # Log samples and anomalies
                    if i < 10 or i % 1000 == 0:
                        log.debug(
                            f"  Frame {i:5d}: dx={transform[0]:7.3f}, dy={transform[1]:7.3f}, da={transform[2]:7.3f}")

                    if any(abs(v) > 100 for v in transform[:2]) or abs(transform[2]) > 3.14:
                        log.warning(
                            f"  Frame {i:5d}: Large transform detected: dx={transform[0]:.1f}, dy={transform[1]:.1f}, da={transform[2]:.3f}")

                    transforms.append(transform)
                except Exception as e:
                    parse_errors += 1
                    if parse_errors < 10:
                        log.error(f"Error parsing frame {i}: {e}")

            if parse_errors > 0:
                log.warning(f"Total parse errors: {parse_errors}")

            if len(transforms) < frame_count:
                log.info(f"Parsed {len(transforms):,} frames out of {frame_count:,}")
        else:
            log.warning("")
            log.warning("Could not detect valid structure!")
            log.info("This might be due to:")
            log.info("  1. Unknown TRF format version")
            log.info("  2. Corrupted file")
            log.info("  3. Non-standard vidstab build")

            log.info("")
            log.info("Falling back to default parsing (assuming 24 bytes per record)...")
            transforms = analyze_trf_data(data, header)

    if transforms:
        log.info("")
        log.info(f"Successfully parsed {len(transforms):,} transforms")

        # Show distribution of values
        if len(transforms) > 100:
            dx_vals = [t[0] for t in transforms[:1000]]
            dy_vals = [t[1] for t in transforms[:1000]]
            da_vals = [t[2] for t in transforms[:1000]]

            log.debug("Value distribution (first 1000 frames):")
            log.debug(f"  dx: min={min(dx_vals):.3f}, max={max(dx_vals):.3f}, median={sorted(dx_vals)[500]:.3f}")
            log.debug(f"  dy: min={min(dy_vals):.3f}, max={max(dy_vals):.3f}, median={sorted(dy_vals)[500]:.3f}")
            log.debug(f"  da: min={min(da_vals):.3f}, max={max(da_vals):.3f}, median={sorted(da_vals)[500]:.3f}")

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
