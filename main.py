#read text file that contains the paths to the wav file folders
import glob, os

from split_wav_folder import split_podcast_folders
#from transcribe_pod_folders import transcribe_splitPodcast_folders


#--- Split wav files into segments
def read_and_split():
    # read text file that contains the paths to the wav file folders
    with open("podcast_folders.txt", "r") as f:
        podcast_folders = f.readlines()

    # remove whitespace characters like `\n` at the end of each line
    podcast_folders = [x.strip() for x in podcast_folders]


    max_len = 210 # max length of segments in seconds
    close_th = 1.65 # threshold for merging segments (in seconds)

    split_podcast_folders("podcast_folders.txt", max_len, close_th)


read_and_split()

#------ Transcribe segments and add punctuation

# we can re-use the podcast_folders.txt. 
# Split folders have the same name, except for the "_split" suffix

#transcribe_splitPodcast_folders("podcast_folders.txt")

print(" The size of the split folders may be too large to keep., \n Consider deleting the split folders after transcribing them. \n Or keep them for future transcriptions with different models.")


#requirements.txt
#pip freeze > requirements.txt

#pip install -r requirements.txt


