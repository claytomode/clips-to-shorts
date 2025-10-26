from moviepy import TextClip, CompositeVideoClip, ColorClip
import sys
import os

print("Testing TextClip syntax (Test 6)...")

# Define the full path to the font
IMPACT_FONT_PATH = r"C:\Windows\Fonts\impact.ttf"

# Suppress moviepy's stdout progress bars for this test
os.environ["IMAGEMAGICK_BINARY"] = "disable" # Hack to quiet ImageMagick check

try:
    # --- This is the new, corrected syntax ---
    txt_clip = TextClip(
        text="THIS IS A TEST",
        fontsize=100,         # <-- THE FIX
        color='white',
        font=IMPACT_FONT_PATH,
        stroke_color='black', 
        stroke_width=5      
        # We are NOT setting 'size'
    )
    
    # Use the new .with_... methods
    txt_clip = (
        txt_clip
        .with_duration(2)
        .with_position(('center', 'center'))
    )

    # Create a simple black background
    bg_clip = ColorClip(size=(1080, 1920), color=(0,0,0), duration=2)

    final_video = CompositeVideoClip([bg_clip, txt_clip])

    # Try to render it
    print("Syntax OK. Attempting test render...")
    final_video.write_videofile(
        "test_output.mp4", 
        codec="h264_nvenc", # Use GPU
        logger=None # Suppress verbose output
    )
    
    print("\n--- SUCCESS! ---")
    print("test_output.mp4 was created. The new syntax is correct.")
    print("You can now safely update caption_generator.py")

except Exception as e:
    print(f"\n--- TEST FAILED ---")
    print(f"An error occurred: {e}")
    print("Do not update the main script. There is still an error.")
    import traceback
    traceback.print_exc() # Print full error
    sys.exit(1)
finally:
    # Clean up the environment variable
    if "IMAGEMAGICK_BINARY" in os.environ:
        del os.environ["IMAGEMAGICK_BINARY"]