import subprocess
import os
import sys

def get_video_duration(video_path):
    """Get the duration of the video using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        duration = float(result.stdout.strip())
        print(f"📏 Video duration: {duration:.2f} seconds")
        return duration
    except Exception as e:
        print(f"❌ Error retrieving duration: {e}")
        sys.exit(1)

def split_video(video_path, hw_accel="cuda"):
    """Splits the video into two equal duration halves using hardware acceleration."""
    if not os.path.isfile(video_path):
        print(f"❌ Error: File '{video_path}' not found.")
        sys.exit(1)

    # Extract base filename (without extension)
    base_name, ext = os.path.splitext(video_path)
    output1 = f"{base_name}-1{ext}"
    output2 = f"{base_name}-2{ext}"

    # Get video duration
    duration = get_video_duration(video_path)
    half_duration = duration / 2

    # Hardware acceleration mapping
    hw_decoders = {
        "cuda": "h264_cuvid",
        "vaapi": "h264_vaapi",
        "amf": "h264_amf"
    }
    hw_decoder = hw_decoders.get(hw_accel, None)

    # First half
    cmd1 = ["ffmpeg", "-y"]
    if hw_decoder:
        cmd1 += ["-hwaccel", hw_accel, "-c:v", hw_decoder]
    cmd1 += ["-i", video_path, "-t", str(half_duration), "-c:v", "copy", "-c:a", "copy", output1]

    # Second half
    cmd2 = ["ffmpeg", "-y"]
    if hw_decoder:
        cmd2 += ["-hwaccel", hw_accel, "-c:v", hw_decoder]
    cmd2 += ["-i", video_path, "-ss", str(half_duration), "-c:v", "copy", "-c:a", "copy", output2]

    print(f"🚀 Splitting first half: {output1}")
    subprocess.run(cmd1, stdout=sys.stdout, stderr=sys.stderr)

    print(f"🚀 Splitting second half: {output2}")
    subprocess.run(cmd2, stdout=sys.stdout, stderr=sys.stderr)

    print(f"✅ Done! \n 1️⃣ {output1} \n 2️⃣ {output2}")

# Run script from command line
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python split_video.py <input_video.mp4>")
        sys.exit(1)

    input_file = sys.argv[1]
    split_video(input_file)
