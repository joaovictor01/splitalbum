#/bin/bash

# Put all files from an album in a separate folder and run the script
# set the path to the folder with -f
# set the artist name with -a
# set the album name with -A

while getopts f:a:A: option
do
case "${option}"
in
	f) FILEPATH=${OPTARG};;
	a) ARTIST=${OPTARG};;
	A) ALBUM=${OPTARG};;
esac
done

FILEPATH="$FILEPATH/*.mp3"
for f in $FILEPATH
do
	filename=$(basename "$f")
	echo $filename
	title=$(cut -d "." -f1 <<< $filename)
	echo $title
	id3v2 "$f" -a "$ARTIST" -A "$ALBUM" -t "$title"
done


