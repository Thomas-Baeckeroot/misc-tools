#!/bin/bash

# Script to concatenate RunCam Thumb2 video files (MP4) and gyroscope data files (GCSV)
# Usage: ./concatenate_MP4_gcsv.sh 0043 0044

function concatenate_MP4() {
    local video_file_a="Thumb2_$1.MP4"
    local video_file_b="Thumb2_$2.MP4"
    local video_out="Thumb2_$1+$2.MP4"
    
    # Check if input files exist
    if [[ ! -f "$video_file_a" ]]; then
        echo "Error: Video file $video_file_a not found" >&2
        return 1
    fi
    
    if [[ ! -f "$video_file_b" ]]; then
        echo "Error: Video file $video_file_b not found" >&2
        return 1
    fi
    
    # Create temporary file list for ffmpeg
    local temp_list="/tmp/concatenate_MP4_list_$$.txt"
    printf "file '%s'\nfile '%s'" "$video_file_a" "$video_file_b" > "$temp_list"
    
    echo "Concatenating video files: $video_file_a + $video_file_b -> $video_out"
    
    # Use ffmpeg to concatenate videos
    if ffmpeg -f concat -safe 0 -i "$temp_list" -c copy "$video_out" -y; then
        echo "Video concatenation successful: $video_out"
        rm -f "$temp_list"
        return 0
    else
        echo "Error: Video concatenation failed" >&2
        rm -f "$temp_list"
        return 1
    fi
}

function concatenate_gcsv() {
    local giro_file_a="Thumb2_$1.gcsv"
    local giro_file_b="Thumb2_$2.gcsv"
    local giro_out="Thumb2_$1+$2.gcsv"
    
    # Check if input files exist
    if [[ ! -f "$giro_file_a" ]]; then
        echo "Error: Gyroscope file $giro_file_a not found" >&2
        return 1
    fi
    
    if [[ ! -f "$giro_file_b" ]]; then
        echo "Error: Gyroscope file $giro_file_b not found" >&2
        return 1
    fi
    
    echo "Concatenating gyroscope files: $giro_file_a + $giro_file_b -> $giro_out"
    
    # Merge the two GCSV files
    # First file: copy entirely
    # Second file: skip header lines (from "GYROFLOW IMU LOG" to "t,gx,gy,gz,ax,ay,az")
    cat "$giro_file_a" > "$giro_out"
    
    # Find the line number after the data header line "t,gx,gy,gz,ax,ay,az"
    local header_end_line=$(grep -n "^t,gx,gy,gz,ax,ay,az" "$giro_file_b" | cut -d: -f1)
    
    if [[ -n "$header_end_line" ]]; then
        # Skip all header lines including the data header
        tail -n +$((header_end_line + 1)) "$giro_file_b" >> "$giro_out"
    else
        # Fallback: assume standard 9-line header
        tail -n +2 "$giro_file_b" >> "$giro_out"
    fi
    
    if [[ $? -eq 0 ]]; then
        echo "Gyroscope concatenation successful: $giro_out"
        return 0
    else
        echo "Error: Gyroscope concatenation failed" >&2
        return 1
    fi
}

function concatenate_MP4_gcsv() {
    # Validate input parameters
    if [[ -z "$1" || -z "$2" ]]; then
        echo "Error: Both file IDs are required" >&2
        return 1
    fi
    
    # Check if file IDs are numeric (4 digits expected)
    if [[ ! "$1" =~ ^[0-9]{4}$ || ! "$2" =~ ^[0-9]{4}$ ]]; then
        echo "Error: File IDs must be 4-digit numbers (e.g., 0043)" >&2
        return 1
    fi
    
    echo "Starting concatenation process for files $1 and $2"
    
    # Concatenate MP4 files
    if concatenate_MP4 "$1" "$2"; then
        echo "MP4 concatenation completed successfully"
    else
        echo "Error: MP4 concatenation failed" >&2
        return 1
    fi
    
    # Concatenate GCSV files
    if concatenate_gcsv "$1" "$2"; then
        echo "GCSV concatenation completed successfully"
    else
        echo "Error: GCSV concatenation failed" >&2
        return 1
    fi
    
    echo "All concatenation operations completed successfully"
    return 0
}

# Main script execution
if [[ $# -eq 0 ]]; then
    printf "RunCam Thumb2 File Concatenation Script\n"
    printf "=======================================\n\n"
    printf "This script concatenates MP4 video files and GCSV gyroscope data files.\n\n"
    printf "Usage:\n"
    printf "  %s <file_id_1> <file_id_2>\n\n" "$0"
    printf "Examples:\n"
    printf "  %s 0043 0044\n" "$0"
    printf "  %s 0001 0002\n\n" "$0"
    printf "Alternative usage (sourcing the script):\n"
    printf "  source %s\n" "$0"
    printf "  concatenate_MP4_gcsv 0043 0044\n\n"
    printf "Requirements:\n"
    printf "  - ffmpeg must be installed and available in PATH\n"
    printf "  - Input files must exist in current directory\n"
    printf "  - File IDs must be 4-digit numbers\n"
    exit 0
else
    concatenate_MP4_gcsv "$1" "$2"
    exit $?
fi
