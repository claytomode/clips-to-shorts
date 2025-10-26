import whisper_timestamped as whisper
import ffmpeg
import os

def transcribe_audio(audio_path):
    """
    Transcribes the audio file and returns word-level timestamps.
    """
    print("Loading Whisper model (large-v3)...")
    
    model = whisper.load_model("large-v3", device="cuda") 
    
    print("Transcribing...")
    
    result = whisper.transcribe(
        model, 
        audio_path, 
        language="en",
        temperature=0.0
    )
    
    all_words = []
    for segment in result.get('segments', []):
        all_words.extend(segment.get('words', []))

    if not all_words:
        print("Warning: No words were transcribed.")

    return all_words

def format_ass_time(seconds):
    """Converts seconds (float) to an ASS subtitle time format (H:MM:SS.ss)."""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"

def generate_ass_file(words, output_path):
    """
    Generates an ASS subtitle file from a list of whisper word timestamps.
    This file defines the 'Shorts-style' captions.
    """
    
    style_header = """
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Impact,100,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,5,0,2,10,10,30,1
"""
    events_header = """
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(style_header)
        f.write(events_header)
        
        for word_info in words:
            text = word_info.get('text', '').upper()
            start_time = word_info.get('start')
            end_time = word_info.get('end')
            
            if start_time is None or end_time is None:
                continue
                
            start_str = format_ass_time(start_time)
            end_str = format_ass_time(end_time)
            
            line = f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text}\n"
            f.write(line)
    
    print("Generated temporary subtitle file.")

def create_video_with_captions(video_path):
    """
    Burns the generated captions onto the video file using ffmpeg-python.
    """
    all_words = transcribe_audio(video_path)
    if not all_words:
        print("No words transcribed, skipping caption generation.")
        return video_path

    final_video_path = f"final_{video_path}"
    subtitle_file_path = f"temp_subs_{os.path.basename(video_path)}.ass"

    try:
        generate_ass_file(all_words, subtitle_file_path)

        print("Burning subtitles onto video (this will be fast)...")
        
        input_video = ffmpeg.input(video_path)
        video_stream = input_video.video
        audio_stream = input_video.audio

        fonts_dir_path = 'C\\:/Windows/Fonts' 
        
        video_with_subs = ffmpeg.filter(
            video_stream,
            'subtitles',
            filename=subtitle_file_path,
            fontsdir=fonts_dir_path,
            force_style='1'
        )

        output_stream = ffmpeg.output(
            video_with_subs, 
            audio_stream, 
            final_video_path, 
            **{'c:v': 'h264_nvenc', 'c:a': 'copy'}
        )
        
        print("Running FFmpeg command:")
        ffmpeg.run(output_stream, overwrite_output=True)
        
        print("Successfully burned captions onto video.")
        return final_video_path

    except ffmpeg.Error as e:
        print("\n--- FFMPEG ERROR (Captioning) ---")
        print("STDERR:", e.stderr.decode('utf8'))
        print("----------------------------------\n")
        raise e
    finally:
        if os.path.exists(subtitle_file_path):
            os.remove(subtitle_file_path)
            print("Cleaned up temporary subtitle file.")