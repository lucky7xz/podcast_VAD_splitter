#----- Imports ----
from split_wav_folder import split_podcast_folder

import os, glob, time

from tqdm import tqdm

from natsort import natsorted
from pprint import pprint



# (cpu / cuda)
#--- Load ASR model - how to specify device? --- is crucial for speed

import nemo.collections.asr as nemo_asr
asr_model = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained("nvidia/stt_en_conformer_transducer_xlarge") #a tiny bit better, but takes a bit longer
#asr_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained("stt_en_conformer_ctc_large")

#---Load Punctuation model

from deepmultilingualpunctuation import PunctuationModel
model = PunctuationModel()

#--------------------------------------------------
# check if files exist in folders!


# folder_name = "huberman_lab_split" #ibm_sst_split

#generate_splits(dirName, wav_file, 210, 1.65, 0)

def transcribe_splitPodcast_folders():
  # transcribe

    start_time = time.time()

    text_folder = folder_name+"_text"
    sub_folders = glob.glob(folder_name + "/*")


    try:
        # create text Directories
        os.mkdir(text_folder)
        print("Text Directory Created")
  
    except FileExistsError:

        old_text_files = glob.glob(text_folder + "/*")
        for file in old_text_files: os.remove(file)


    for fname in sub_folders:
    
        sub_start = time.time()

        wav_files = glob.glob(fname+ "/*")
        wav_files = natsorted(wav_files)

        output_text = ""

        for wav_file in wav_files:
        
            # transcribe wav file
            text = asr_model.transcribe([wav_file])[0]
        
            # concatenate text
            output_text += text + " "

            # add punctuation
            output_text = model.restore_punctuation(output_text)


        with open(text_folder + "/" + fname.split("/")[1] + ".txt", "w") as f:
        
            f.write(output_text)

    
        print("EP named " + fname + " took " , time.time()-sub_start , "sec") #whops
    print("\n Whole folder took " , time.time()- start_time , "sec")

