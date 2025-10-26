import httpx
import os
import yt_dlp
from datetime import datetime, timezone, timedelta

AUTH_URL = "https://id.twitch.tv/oauth2/token"
CLIPS_URL = "https://api.twitch.tv/helix/clips"
USERS_URL = "https://api.twitch.tv/helix/users"

def get_auth_token(client_id, client_secret):
    """Gets an app access token from Twitch."""
    auth_params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    try:
        with httpx.Client() as client:
            auth_response = client.post(AUTH_URL, data=auth_params)
            auth_response.raise_for_status() 
            return auth_response.json()['access_token']
    except httpx.RequestError as e:
        print(f"Error getting auth token: {e}")
        return None

def get_broadcaster_id_from_name(login_name, client_id, token):
    """Looks up a broadcaster's numerical ID from their login name."""
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {token}'
    }
    params = {'login': login_name}
    
    try:
        with httpx.Client() as client:
            r = client.get(USERS_URL, headers=headers, params=params)
            r.raise_for_status()
            data = r.json().get('data', [])
        
        if not data:
            print(f"Could not find user with login name: {login_name}")
            return None
        
        return data[0]['id']
        
    except httpx.RequestError as e:
        print(f"Error getting user ID: {e}")
        return None

def get_clip_data(broadcaster_id, client_id, token, mode='top'):
    """
    Fetches a list of clip data from Twitch.
    mode='top': Gets all-time top 5 clips.
    mode='recent': Gets top 5 clips from the last 24 hours.
    """
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {token}'
    }
    params = {
        'broadcaster_id': broadcaster_id,
        'first': 5
    }

    if mode == 'recent':
        print("Fetching clips from the last 24 hours...")
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=1)
        
        params['started_at'] = start_time.isoformat().replace('+00:00', 'Z')
        params['ended_at'] = end_time.isoformat().replace('+00:00', 'Z')
    else:
        print("Fetching all-time top clips...")
        
    try:
        with httpx.Client() as client:
            r = client.get(CLIPS_URL, headers=headers, params=params)
            r.raise_for_status()
            clips_data = r.json().get('data', [])

        if not clips_data:
            print(f"No clips found for mode: {mode}")
            return None
        
        return clips_data

    except httpx.RequestError as e:
        print(f"Error getting clips list: {e}")
        return None

def download_clip_from_list(clips_data_list):
    """
    Takes a list of clip data and tries to download one using yt-dlp.
    Returns the file path of the first successful download.
    """
    if not clips_data_list:
        print("No clip data provided to download.")
        return None

    for clip in clips_data_list:
        clip_webpage_url = clip['url']
        clip_id = clip['id']
        file_name = f"downloaded_clip_{clip_id}.mp4"

        print(f"Attempting to download clip: {clip['title']} (from {clip_webpage_url})")

        ydl_opts = {
            'outtmpl': file_name,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'quiet': True,
            'noplaylist': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([clip_webpage_url])
            
            print(f"Successfully downloaded clip: {clip['title']}")
            return file_name
        
        except Exception as e:
            print(f"Download failed for this clip: {e}")
            if os.path.exists(file_name):
                os.remove(file_name)
            print("Trying next clip...")
            continue

    print("Could not download any of the provided clips.")
    return None