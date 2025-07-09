This repo just contains some day-to-day scripts usefull for some tasks...

---

### concatenate_MP4_gcsv.sh

Some action cameras (like RunCam Thumb2 , etc...) capture .MP4 video file and .gcsv gyro data file.  
In some settings, we can record multiple set of files of each 1, 3 or 5 minutes.  
This script allows to merge multiple sequences in one longer one. Merging the videos files together on one side (ffmpeg)
and merging .gcsv files together on the other side.

---

### trf stats

vidstab module of ffmpeg creates trf file. This python script just allows to get statistics from generated files.
.trf files can be created from different parameters (scale, luminosity, ...), we just want to know which parameters are the good ones.

---
