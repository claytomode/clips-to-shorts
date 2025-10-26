import os
import twitch_downloader
import ui_helpers
import video_editor
import caption_generator
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    print("--- FATAL ERROR ---")
    print("TWITCH_CLIENT_ID or TWITCH_CLIENT_SECRET not found.")
    print("Please make sure you have a '.env' file in the same directory,")
    print("and it contains:")
    print("TWITCH_CLIENT_ID=your_id_here")
    print("TWITCH_CLIENT_SECRET=your_secret_here")
    print("-------------------")
    exit()

def main():
    print("Welcome to the Twitch Clip-to-TikTok Bot!")
    
    login_name = input("Enter the streamer's Twitch Username: ")
    
    print("Authenticating with Twitch...")
    auth_token = twitch_downloader.get_auth_token(CLIENT_ID, CLIENT_SECRET)
    if not auth_token:
        print("Failed to authenticate. Double-check your TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET in the .env file.")
        return

    print(f"Looking up Broadcaster ID for '{login_name}'...")
    broadcaster_id = twitch_downloader.get_broadcaster_id_from_name(
        login_name, 
        CLIENT_ID, 
        auth_token
    )
    if not broadcaster_id:
        return
    
    print(f"Found Broadcaster ID: {broadcaster_id}")

    recent_clips_list = twitch_downloader.get_clip_data(
        broadcaster_id, CLIENT_ID, auth_token, mode='recent'
    )

    print("\n--- PROCESSING: Most Recent Clip ---")
    
    if not recent_clips_list:
        print("No recent clips found. Exiting.")
        return

    try:
        downloaded_clip_path = twitch_downloader.download_clip_from_list(recent_clips_list)
        if downloaded_clip_path is None:
            print("Failed to download any recent clip.")
            return

        print(f"Clip downloaded to: {downloaded_clip_path}")

        print("\nA UI window will open. Please select the regions.")
        webcam_coords, gameplay_coords = ui_helpers.get_rois(downloaded_clip_path)

        print(f"Webcam region: {webcam_coords}")
        print(f"Gameplay region: {gameplay_coords}")

        print("Cropping and stacking video for TikTok...")
        tiktok_clip_path = video_editor.format_for_tiktok(
            downloaded_clip_path, 
            webcam_coords, 
            gameplay_coords
        )
        print(f"TikTok version saved to: {tiktok_clip_path}")

        print("Starting transcription and caption generation...")
        final_video_path = caption_generator.create_video_with_captions(
            tiktok_clip_path
        )
        
        print("\n--- DONE: Most Recent Clip ---")
        print(f"Final video with captions saved to: {final_video_path}")
        
        os.remove(downloaded_clip_path)
        os.remove(tiktok_clip_path)
        print("Cleaned up intermediate files.")

    except Exception as e:
        print(f"\nAn error occurred while processing the recent clip: {e}")
        import traceback
        traceback.print_exc()
        if 'downloaded_clip_path' in locals() and os.path.exists(downloaded_clip_path):
            os.remove(downloaded_clip_path)
        if 'tiktok_clip_path' in locals() and os.path.exists(tiktok_clip_path):
            os.remove(tiktok_clip_path)
    
    print("\n--- All processing complete! ---")

if __name__ == "__main__":
    main()