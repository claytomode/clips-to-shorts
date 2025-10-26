# Twitch Clip to TikTok Formatter 🎬

This Python script automates the process of fetching a recent Twitch clip, reformatting it for vertical platforms like TikTok/Shorts (stacking webcam and gameplay), and adding word-by-word animated captions.

---

## Features

* Fetches the most recent downloadable clip for a specified Twitch streamer.
* Uses a visual UI (OpenCV) to let you select the webcam and gameplay regions for cropping (first run only, ideally).
* Crops and stacks the selected regions into a 9:16 vertical video format using `ffmpeg`.
* Transcribes the audio using OpenAI's Whisper (`large-v3` model by default) with GPU acceleration (CUDA).
* Generates word-level timestamps using `whisper-timestamped`.
* Creates an `.ass` subtitle file with styling similar to popular short-form content.
* Burns the subtitles onto the video using `ffmpeg` and NVENC.

