import ffmpeg

def format_for_tiktok(input_path, webcam_coords, gameplay_coords):
    """
    Crops/stacks the video using the ffmpeg-python library for a clean, fast approach.
    """
    output_clip_path = f"tiktok_format_{input_path}"

    wc_x = webcam_coords[0]
    wc_y = webcam_coords[1]
    wc_w = webcam_coords[2] - webcam_coords[0]
    wc_h = webcam_coords[3] - webcam_coords[1]
    
    gp_x = gameplay_coords[0]
    gp_y = gameplay_coords[1]
    gp_w = gameplay_coords[2] - gameplay_coords[0]
    gp_h = gameplay_coords[3] - gameplay_coords[1]

    input_stream = ffmpeg.input(input_path)
    video_stream = input_stream.video
    audio_stream = input_stream.audio

    webcam_clip = (
        video_stream
        .crop(wc_x, wc_y, wc_w, wc_h)
        .filter('scale', w=1080, h=840)
    )
    
    gameplay_clip = (
        video_stream
        .crop(gp_x, gp_y, gp_w, gp_h)
        .filter('scale', w=1080, h=1080) # Changed from .scale()
    )

    stacked_video = ffmpeg.filter([webcam_clip, gameplay_clip], 'vstack', inputs=2)

    output_stream = ffmpeg.output(
        stacked_video, 
        audio_stream, 
        output_clip_path, 
        **{'c:v': 'h264_nvenc', 'c:a': 'copy'}
    )

    print("Cropping and stacking with ffmpeg-python (this should be fast)...")
    
    try:
        ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
        
        print("ffmpeg-python processing complete.")
        return output_clip_path
        
    except ffmpeg.Error as e:
        print("\n--- FFMPEG ERROR ---")
        print("STDERR:", e.stderr.decode('utf8'))
        print("----------------------\n")
        raise e
    except FileNotFoundError:
        print("\n--- FFMPEG ERROR ---")
        print("ffmpeg.exe not found. Make sure it's installed and in your system's PATH.")
        print("You can download it from https://ffmpeg.org/download.html")
        print("----------------------\n")
        raise