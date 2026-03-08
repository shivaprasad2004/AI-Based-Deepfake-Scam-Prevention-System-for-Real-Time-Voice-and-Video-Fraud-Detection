import os
import re
import requests
import uuid
import subprocess
import json
from urllib.parse import urlparse
from config import Config


class FileHandler:
    ALLOWED_EXTENSIONS = Config.ALLOWED_VIDEO_EXTENSIONS | Config.ALLOWED_AUDIO_EXTENSIONS
    VIDEO_EXTENSIONS = Config.ALLOWED_VIDEO_EXTENSIONS
    AUDIO_EXTENSIONS = Config.ALLOWED_AUDIO_EXTENSIONS

    @staticmethod
    def get_file_extension(filename):
        return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    @staticmethod
    def is_allowed_file(filename):
        ext = FileHandler.get_file_extension(filename)
        return ext in FileHandler.ALLOWED_EXTENSIONS

    @staticmethod
    def get_file_type(filename):
        ext = FileHandler.get_file_extension(filename)
        if ext in FileHandler.VIDEO_EXTENSIONS:
            return 'video'
        elif ext in FileHandler.AUDIO_EXTENSIONS:
            return 'audio'
        return 'unknown'

    @staticmethod
    def save_uploaded_file(file_obj):
        """Save a file from Flask request."""
        if not file_obj or not file_obj.filename:
            return None, 'No file provided'

        filename = file_obj.filename
        if not FileHandler.is_allowed_file(filename):
            return None, f'File type not allowed. Allowed: {", ".join(FileHandler.ALLOWED_EXTENSIONS)}'

        ext = FileHandler.get_file_extension(filename)
        unique_name = f'{uuid.uuid4().hex}.{ext}'
        save_path = os.path.join(Config.UPLOAD_FOLDER, unique_name)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        file_obj.save(save_path)

        file_size = os.path.getsize(save_path)
        file_type = FileHandler.get_file_type(filename)

        return {
            'path': save_path,
            'original_name': filename,
            'file_type': file_type,
            'file_size': file_size
        }, None

    # Domains that require yt-dlp for downloading
    YTDLP_DOMAINS = {
        'youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com',
        'facebook.com', 'www.facebook.com', 'fb.watch',
        'instagram.com', 'www.instagram.com',
        'twitter.com', 'x.com', 'www.twitter.com',
        'tiktok.com', 'www.tiktok.com',
        'vimeo.com', 'www.vimeo.com',
        'dailymotion.com', 'www.dailymotion.com',
        'twitch.tv', 'www.twitch.tv',
        'reddit.com', 'www.reddit.com',
    }

    @staticmethod
    def _is_streaming_url(url):
        """Check if URL is from a streaming platform that needs yt-dlp."""
        try:
            hostname = urlparse(url).hostname or ''
            return hostname in FileHandler.YTDLP_DOMAINS
        except Exception:
            return False

    @staticmethod
    def _get_ffmpeg_path():
        """Get ffmpeg binary path from imageio-ffmpeg or system PATH."""
        try:
            from imageio_ffmpeg import get_ffmpeg_exe
            return get_ffmpeg_exe()
        except ImportError:
            return 'ffmpeg'  # hope it's in PATH

    @staticmethod
    def _download_with_ytdlp(url):
        """Download video/audio from streaming platforms using yt-dlp."""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        unique_id = uuid.uuid4().hex
        ffmpeg_path = FileHandler._get_ffmpeg_path()
        output_path = os.path.join(Config.UPLOAD_FOLDER, f'{unique_id}.mp4')

        try:
            # Download low-res mp4 directly (fast) and print info as JSON
            download_cmd = [
                'yt-dlp',
                '--no-playlist',
                '--no-warnings',
                '--print-json',
                '--ffmpeg-location', ffmpeg_path,
                '-f', 'worst[ext=mp4]/bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]/worst',
                '--merge-output-format', 'mp4',
                '-o', output_path,
                url
            ]
            dl_result = subprocess.run(
                download_cmd, capture_output=True, text=True, timeout=120
            )

            if dl_result.returncode != 0:
                # Fallback: any single format
                output_path2 = os.path.join(Config.UPLOAD_FOLDER, f'{unique_id}_fb.mp4')
                fallback_cmd = [
                    'yt-dlp',
                    '--no-playlist',
                    '--no-warnings',
                    '--print-json',
                    '--ffmpeg-location', ffmpeg_path,
                    '-f', 'worst[ext=mp4]/worst',
                    '-o', output_path2,
                    url
                ]
                fb_result = subprocess.run(
                    fallback_cmd, capture_output=True, text=True, timeout=120
                )
                if fb_result.returncode != 0:
                    return None, f'yt-dlp download failed: {dl_result.stderr.strip()} | Fallback: {fb_result.stderr.strip()}'
                output_path = output_path2
                dl_result = fb_result

            # Parse info from --print-json output
            video_info = {}
            try:
                video_info = json.loads(dl_result.stdout.strip().split('\n')[-1])
            except (json.JSONDecodeError, IndexError):
                pass
            original_title = video_info.get('title', 'downloaded_video')
            duration = video_info.get('duration')

            if not os.path.exists(output_path):
                # Search for any file with the unique_id prefix
                for f in os.listdir(Config.UPLOAD_FOLDER):
                    if f.startswith(unique_id):
                        output_path = os.path.join(Config.UPLOAD_FOLDER, f)
                        break

            if not os.path.exists(output_path):
                return None, 'Download completed but output file not found'

            ext = FileHandler.get_file_extension(output_path)
            file_type = 'video' if ext in FileHandler.VIDEO_EXTENSIONS else 'audio' if ext in FileHandler.AUDIO_EXTENSIONS else 'video'
            file_size = os.path.getsize(output_path)

            return {
                'path': output_path,
                'original_name': f'{original_title}.{ext}',
                'file_type': file_type,
                'file_size': file_size,
                'duration': duration,
            }, None

        except subprocess.TimeoutExpired:
            return None, 'Download timed out (video may be too long)'
        except json.JSONDecodeError:
            return None, 'Failed to parse video information'
        except FileNotFoundError:
            return None, 'yt-dlp is not installed. Install it with: pip install yt-dlp'
        except Exception as e:
            return None, f'yt-dlp error: {str(e)}'

    @staticmethod
    def download_from_url(url):
        """Download a file from a URL. Supports direct links and streaming platforms."""
        # Check if this is a streaming platform URL (YouTube, etc.)
        if FileHandler._is_streaming_url(url):
            return FileHandler._download_with_ytdlp(url)

        # Try direct download first
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path) or 'downloaded_file'

            if not FileHandler.is_allowed_file(filename):
                # Try to get from content-disposition or content-type
                try:
                    response = requests.head(url, allow_redirects=True, timeout=10)
                    content_type = response.headers.get('Content-Type', '')
                    ext = FileHandler._ext_from_content_type(content_type)
                    if ext:
                        filename = f'downloaded_file.{ext}'
                    else:
                        # Fallback: try yt-dlp as last resort for unknown URLs
                        return FileHandler._download_with_ytdlp(url)
                except requests.RequestException:
                    # If HEAD request fails, try yt-dlp
                    return FileHandler._download_with_ytdlp(url)

            ext = FileHandler.get_file_extension(filename)
            unique_name = f'{uuid.uuid4().hex}.{ext}'
            save_path = os.path.join(Config.UPLOAD_FOLDER, unique_name)
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

            response = requests.get(url, stream=True, timeout=120)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(save_path)
            file_type = FileHandler.get_file_type(filename)

            return {
                'path': save_path,
                'original_name': filename,
                'file_type': file_type,
                'file_size': file_size
            }, None

        except requests.RequestException as e:
            return None, f'Failed to download from URL: {str(e)}'

    @staticmethod
    def download_from_drive(drive_url):
        """Download a file from Google Drive public link."""
        try:
            file_id = FileHandler._extract_drive_id(drive_url)
            if not file_id:
                return None, 'Invalid Google Drive URL'

            download_url = f'https://drive.google.com/uc?export=download&id={file_id}'

            session = requests.Session()
            response = session.get(download_url, stream=True, timeout=120)

            # Handle large file confirmation
            for key, value in response.cookies.items():
                if key.startswith('download_warning'):
                    download_url = f'{download_url}&confirm={value}'
                    response = session.get(download_url, stream=True, timeout=120)
                    break

            # Try to get filename from content-disposition
            cd = response.headers.get('Content-Disposition', '')
            filename_match = re.search(r'filename="?([^";\n]+)"?', cd)
            filename = filename_match.group(1) if filename_match else 'drive_file.mp4'

            ext = FileHandler.get_file_extension(filename)
            if not ext or ext not in FileHandler.ALLOWED_EXTENSIONS:
                content_type = response.headers.get('Content-Type', '')
                ext = FileHandler._ext_from_content_type(content_type) or 'mp4'
                filename = f'drive_file.{ext}'

            unique_name = f'{uuid.uuid4().hex}.{ext}'
            save_path = os.path.join(Config.UPLOAD_FOLDER, unique_name)
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(save_path)
            file_type = FileHandler.get_file_type(filename)

            return {
                'path': save_path,
                'original_name': filename,
                'file_type': file_type,
                'file_size': file_size
            }, None

        except Exception as e:
            return None, f'Failed to download from Google Drive: {str(e)}'

    @staticmethod
    def _extract_drive_id(url):
        """Extract file ID from various Google Drive URL formats."""
        patterns = [
            r'/file/d/([a-zA-Z0-9_-]+)',
            r'id=([a-zA-Z0-9_-]+)',
            r'/open\?id=([a-zA-Z0-9_-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def _ext_from_content_type(content_type):
        mapping = {
            'video/mp4': 'mp4',
            'video/avi': 'avi',
            'video/x-msvideo': 'avi',
            'video/quicktime': 'mov',
            'video/webm': 'webm',
            'audio/mpeg': 'mp3',
            'audio/wav': 'wav',
            'audio/x-wav': 'wav',
            'audio/ogg': 'ogg',
            'audio/flac': 'flac',
            'audio/mp4': 'm4a',
        }
        for key, val in mapping.items():
            if key in content_type:
                return val
        return None

    @staticmethod
    def cleanup_file(file_path):
        """Remove a file after processing."""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass
