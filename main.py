
from split_wav_folder import split_podcast_folders
import os
#from transcribe_pod_folders import transcribe_splitPodcast_folders

from speechbrain.pretrained import VAD
#--- Split wav files into segments
def read_and_split():
 
    # read text file that contains the paths to the wav file folders
    with open("podcast_folders.txt", "r") as f:
        podcast_folders = f.readlines()
    
    
    podcast_folders = [x.strip() for x in podcast_folders]

    max_len = 400 # max length of segments in seconds
    close_th = 1.65 # threshold for merging segments (in seconds)


    # Init json file for logging split info (and maybe transcription info)
    if os.path.exists("transcription_log.json"):
        pass

    else:
        with open("transcription_log.json", "w") as f:
            f.write("{}")

    split_podcast_folders("podcast_folders.txt", max_len, close_th)


read_and_split()
#clear_split_done() # only if we want to split the same folders again

#------ Transcribe segments and add punctuation

# we can re-use the podcast_folders.txt. 
# Split folders have the same name, except for the "_split" suffix

#transcribe_splitPodcast_folders("podcast_folders.txt")

print(" The size of the split folders may be too large to keep., \n Consider deleting the split folders after transcribing them. \n Or keep them for future transcriptions with different models.")


#requirements.txt
#pip freeze > requirements.txt

#pip install -r requirements.txt


