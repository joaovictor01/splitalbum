from pydub import AudioSegment
import json
import unicodedata
import subprocess
import os
import sys
import time
from pathlib import *
import shutil
from PIL import Image
import mad

musics = []
numero_musicas = 0
album_duration = 0
end_album = 0
MUSIC_FOLDER = Path.home().joinpath('Música')


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'  # colocar no final do texto para marcar onde acaba
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def help():
    print("You should have a tracks.txt with a list of musics and respective start time inside parenthesis")
    print("Formats of tracklist accepted:")
    print("Music Name (00:00)")
    print("00:00 - Music Name")
    print("Music Name - 00:00")
    print("Usage: python splitalbum.py /path/to/album")


def menu():
    print(bcolors.HEADER+'1 - Download album'+bcolors.ENDC)
    print(bcolors.HEADER+'2 - Split downloaded album'+bcolors.ENDC)
    print(bcolors.HEADER+'3 - Tag musics'+bcolors.ENDC)
    print(bcolors.HEADER+'0 - Exit'+bcolors.ENDC)
    opt = int(input(bcolors.WARNING+bcolors.BOLD +
                    "Choose an option: "+bcolors.ENDC))

    if opt == 1:
        download_album()
    elif opt == 2:
        filepath = input(bcolors.WARNING+bcolors.BOLD +
                         "Enter the path of the album here: "+bcolors.ENDC)
        filepath = MUSIC_FOLDER.joinpath(filepath)
        os.chdir(filepath)
        read_tracklist(filepath)
    elif opt == 3:
        author = input(bcolors.WARNING +
                       "Enter the name of the author here: "+bcolors.ENDC)
        album = input(bcolors.WARNING +
                      "Enter the name of the album here: "+bcolors.ENDC)
        path = input(bcolors.WARNING +
                     "Enter the path of the folder here: "+bcolors.ENDC)
        try:
            subprocess.run(
                ["tagmusics", "-f", path, "-a", author, "-A", album])
            print(bcolors.BOLD+bcolors.OKGREEN +
                  "Musics tagged successfully"+bcolors.ENDC)
        except:
            print(bcolors.FAIL+"Error tagging"+bcolors.ENDC)
    elif opt == 0:
        return


def seconds_to_timestamp(sec):
    return time.strftime('%H:%M:%S', time.gmtime(sec))


def timestamp_to_seconds(timestamp):
    if len(timestamp.split(":")) == 2:
        aux = timestamp.split(":")
        seconds = int(aux[0])*60 + int(aux[1])
        return seconds
    elif len(timestamp.split(":")) == 3:
        aux = timestamp.split(":")
        seconds = int(aux[0])*60*60 + int(aux[1])*60 + int(aux[2])
        return seconds


def get_media_duration(media_path):
    mf = mad.MadFile(str(media_path.joinpath('album.mp3')))
    track_length_miliseconds = mf.total_time()
    album_duration = track_length_miliseconds*1000

    end_album = time.strftime('%H:%M:%S', time.gmtime(album_duration))
    return end_album


def tag_musics(author, album, folder_path):
    try:
        subprocess.run(["tagmusics", "-f", folder_path,
                        "-a", author, "-A", album])
        return 1
    except:
        return 0


def split_album(filename, musics):
    with open("musics.json", "w+") as musics_json:
        json.dump(musics, musics_json)

    for music in musics:
        name = music["name"].strip(" ")+".mp3"
        start = music["start"]
        end = music["end"]

        subprocess.run(['ffmpeg', '-i', filename.joinpath('album.mp3'), '-vn',
                        '-acodec', 'copy', '-ss', start, '-to', end, name])

        print(bcolors.WARNING+bcolors.BOLD +
              "Album splitted successfully! Want to tag the musics now? (Y/n)"+bcolors.ENDC)
        opt = input()
        if opt.startswith("n") or opt.startswith("N"):
            return
        else:
            author = input(bcolors.WARNING+bcolors.BOLD +
                           "Insert the name of the author here: "+bcolors.ENDC)
            album = input(bcolors.WARNING+bcolors.BOLD +
                          "Insert the name of the album here: "+bcolors.ENDC)

            res = tag_musics(author, album, filename)
            if res:
                print(bcolors.BOLD+bcolors.OKGREEN +
                      "Musics tagged successfully!"+bcolors.ENDC)
            else:
                print(bcolors.FAIL+"Error tagging the musics!"+bcolors.ENDC)


def read_tracklist(filename):
    lines = []
    # tracklist mode 1
    # Music Name (00:00)
    # tracklist mode 2
    # 00:00 - Music Name
    # tracklist mode 3
    # Music Name - 00:00

    with open(filename.joinpath('tracks.txt'), "r") as tracklist_file:
        for line in tracklist_file.readlines():
            lines.append(line)

    linha = lines[0]
    if linha[0].isdigit():
        tracklist_mode = 2
        format_tracklist_type2(filename, lines)
    elif linha.split("-")[1].strip()[0].isdigit():
        tracklist_mode = 3
        format_tracklist_type3(filename, lines)
    else:
        tracklist_mode = 1
        format_tracklist_type1(filename, lines)


def format_tracklist_type3(filename, lines):
    numero_musicas = 0
    end_album = get_media_duration(filename)
    musics = []

    for line in lines:
        if len(line.strip()) == 0:
            continue
        else:
            numero_musicas += 1

    i = 0
    for line in lines:
        if len(line.strip()) == 0:
            continue

        music = {}
        title = line.split("-")[0]
        start = line.split("-")[1]
        music["name"] = title.strip()
        music["start"] = start.strip()

        if i+1 == numero_musicas:
            music["end"] = end_album

        if i > 0:
            end = timestamp_to_seconds(start) - 1
            end = seconds_to_timestamp(end)
            musics[i-1]["end"] = end

        musics.append(music)
        i += 1
    split_album(filename, musics)


def format_tracklist_type2(filename, lines):
    numero_musicas = 0
    end_album = get_media_duration(filename)
    musics = []

    for line in lines:
        if len(line.strip()) == 0:
            continue
        else:
            numero_musicas += 1

    i = 0
    for line in lines:
        if len(line.strip()) == 0:
            continue

        music = {}
        title = line.split("-")[1]
        start = line.split("-")[0]
        music["name"] = title.strip()
        music["start"] = start.strip()

        if i+1 == numero_musicas:
            music["end"] = end_album

        if i > 0:
            end = timestamp_to_seconds(start) - 1
            end = seconds_to_timestamp(end)
            musics[i-1]["end"] = end

        musics.append(music)
        i += 1
    split_album(filename, musics)


def format_tracklist_type1(filename, lines):
    musics = []
    end_album = get_media_duration(filename)
    numero_musicas = len(lines)

    i = 0
    for line in lines:
        music = {}
        name = line.split('(')[0]
        music_init = line.split('(')[1].strip('\n').strip(' ').strip(')')

        # convert the start of the music to seconds
        if len(music_init.split(":")) == 2:
            aux = music_init.split(":")
            init_seconds = int(aux[0])*60 + int(aux[1])
        elif len(music_init.split(":")) == 3:
            aux = music_init.split(":")
            init_seconds = int(aux[0])*60*60 + int(aux[1])*60 + int(aux[2])
        else:
            print(bcolors.FAIL+"Error identifying timestamps"+bcolors.ENDC)
            return

        # if it's the last track of the album
        if i+1 == numero_musicas:
            music_end = end_album
            music = {
                "name": unicodedata.normalize('NFC', name),
                "start": music_init,
                "end": music_end
            }
        else:
            music = {
                "name": unicodedata.normalize('NFC', name),
                "start": music_init
            }

        # set the end of the previous music to one seconds before the start of the current track
        if i > 0:
            musics[i-1]["end"] = seconds_to_timestamp(init_seconds - 1)

        musics.append(music)
        i += 1

    split_album(filename, musics)


def download_album():
    # youtube-dl -f mp4 -o 'video.%(ext)s' --write-info-json "$url"
    url = input(bcolors.WARNING+bcolors.BOLD +
                "Paste the url of the album here: "+bcolors.ENDC)
    os.chdir(MUSIC_FOLDER)
    album_name = ''

    # download the album and as "album.mp3" and the info-json as "album.info.json"
    subprocess.run([
        "youtube-dl",
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "-o",
        "album.%(ext)s",
        "--write-info-json",
        url
    ])

    # get the album title from the json with the video information
    with open('album.info.json', 'r') as album_info_file:
        album_info = json.load(album_info_file)
        album_name = album_info['title']

    # Move the album to a folder with the album name
    album_folder = album_name.replace(" ", "_").replace(
        "[", "-").replace("]", "").replace("(", "-").replace(")", "")

    MUSIC_FOLDER.joinpath(album_folder).mkdir(parents=True, exist_ok=True)
    shutil.copy(str(MUSIC_FOLDER.joinpath('album.mp3')),
                str(MUSIC_FOLDER.joinpath(album_folder)))
    os.chdir(MUSIC_FOLDER.joinpath(album_folder))

    # Download the video thumbnail
    thumbnail_url = subprocess.run([
        "youtube-dl",
        "--get-thumbnail",
        url
    ], capture_output=True)
    thumbnail_url = thumbnail_url.stdout.decode('utf-8').strip('\n')
    subprocess.run(["wget", "-O", "cover.webp", thumbnail_url])

    # Save the thumnail as the album cover (cover.jpg)
    album_cover = Image.open('cover.webp').convert('RGB')
    album_cover.save('cover.jpg', 'jpeg')


def main():
    menu()


if __name__ == "__main__":
    main()
