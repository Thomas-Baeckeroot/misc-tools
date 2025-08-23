#!/bin/bash

# Expérience d'ajustements manuels des niveaux:
# Min(noir)      gamma?     Max(blanc)
#    22           1.30         217
#    37           1.30         208
#    65           2.00         211?
#    70           2.50         200
#    42           1.00         188
#   100           2.00         200
#    58           1.50         185
#    60			 ~1 		   210
# Correction pour les plans:
#    85           1.50         220
#   100           1.2          220	


folder="/home/thomas/Images/Scanned documents - temp !AE!"
cd "$folder"
pwd

for filename in *.pdf
do
	echo Converting file \"$filename\"...
	[ -e "$filename" ] || continue
	dest_jpg="${filename/.png/.jpg}"
	dest_web_jpg="${filename/.png/_web.jpg}"
	# Convert all .png to .jpg
	convert -auto-level -quality 40 "$filename" "$dest_web_jpg"
	if ! command -v trash-put &> /dev/null
	then
		echo "WARNING: 'trash-put' command not found. Please install it using: sudo apt install trash-cli"
		# exit 1
	fi
	# if below trash-put fails, please 'sudo apt install trash-cli'
	convert -auto-level "$filename" "$dest_jpg" && trash-put "$filename"
	# If failing below: sudo apt install trash-cli
done

for filename in *.png
do
	echo Converting file \"$filename\"...
	[ -e "$filename" ] || continue

	file_processed="${filename/.png/_processed.png}"
	# Tests for values of -contrast-stretch :
	# 2%x85% to 2%x90% White paper not 100% white and file size bigger than 92%
	# 2%x92% BEST for text, some white paper not 100% white but best file size
	# 2%x94% to 2%x96% Only from 96% white paper is fully white but other text are burnt
	convert -auto-level -contrast-stretch 2%x90% "$filename" "$file_processed"

	dest_web_jpg="${filename/.png/_web.jpg}"
	# Convert all .png to .jpg
	convert -auto-level -quality 40 "$file_processed" "$dest_web_jpg"
	# if below trash-put fails, please 'sudo apt install trash-cli'

	dest_avif="${filename/.png/.avif}"
	# If failing below because of avifenc': sudo apt install libavif-tools
	# If failing below because of trash-put': sudo apt install trash-cli
	avifenc --qcolor 30 --jobs all "$file_processed" "$dest_avif" && trash-put "$filename" && trash-put "$file_processed"
done
