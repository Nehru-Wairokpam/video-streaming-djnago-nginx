# videos/views.py
import os
from django.shortcuts import render, redirect
from django.conf import settings
from .models import Video
from .forms import VideoForm
import subprocess

def video_list(request):
    videos = Video.objects.all()
    return render(request, 'videos/video_list.html', {'videos': videos})

def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()  # Save the video to the database
            process_video(video)  # Process the video for HLS streaming
            return redirect('video_list')  # Redirect to video list after upload
    else:
        form = VideoForm()
    
    return render(request, 'videos/upload.html', {'form': form})

def process_video(video):
    # Process the uploaded video with FFmpeg to generate HLS streams
    video_path = os.path.join(settings.MEDIA_ROOT, video.video_file.name)
    stream_name = os.path.splitext(os.path.basename(video.video_file.name))[0]
    output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', stream_name)
    
    os.makedirs(output_dir, exist_ok=True)

    # FFmpeg command to generate HLS (360p and 720p)
    ffmpeg_command = f"ffmpeg -i {video_path} " \
                     f"-c:v libx264 -b:v 300k -s 640x360 -f hls -hls_time 10 -hls_list_size 5 {output_dir}/360p.m3u8 " \
                     f"-c:v libx264 -b:v 800k -s 1280x720 -f hls -hls_time 10 -hls_list_size 5 {output_dir}/720p.m3u8"

    # Run FFmpeg
    subprocess.call(ffmpeg_command, shell=True)

    # Create master playlist
    create_master_playlist(output_dir, stream_name)

    # Save the stream URLs to the database
    video.hls_master_url = f"/media/hls/{stream_name}/master.m3u8"
    video.hls_360p_url = f"/media/hls/{stream_name}/360p.m3u8"
    video.hls_720p_url = f"/media/hls/{stream_name}/720p.m3u8"
    video.save()

def create_master_playlist(output_dir, stream_name):
    master_playlist_path = os.path.join(output_dir, "master.m3u8")
    with open(master_playlist_path, 'w') as f:
        f.write("#EXTM3U\n")
        f.write("#EXT-X-STREAM-INF:BANDWIDTH=300000,RESOLUTION=640x360\n")
        f.write(f"/media/hls/{stream_name}/360p.m3u8\n")
        f.write("#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=1280x720\n")
        f.write(f"/media/hls/{stream_name}/720p.m3u8\n")
