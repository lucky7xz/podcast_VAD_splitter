#----- Imports ----

import os, glob, time, json
from natsort import natsorted

#from pprint import pprint


import nemo.collections.asr as nemo_asr
#asr_model = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained("nvidia/stt_en_conformer_transducer_xlarge") # should work bit better, but takes a bit longer
asr_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained("stt_en_conformer_ctc_large") # most tested

#---Load Punctuation model

from deepmultilingualpunctuation import PunctuationModel
model = PunctuationModel()

#--------------------------------------------------
# check if files exist in folders!


# folder_key = "huberman_lab_split" #ibm_sst_split

def transcribe_splitPodcast_folder(folder_key):
 
    '''
    input : podcast folder keys from log with split_done == True

    for each ep subfolder(containing segments of a single ep) in a split folder:

        - Transcribe all wav files in a folder and concat
        - Add punctuation.

    '''

    start_time = time.time()

    split_sub_folders = glob.glob(folder_key + "_split/*")

    # find out which subfolders have been transcribed already
    # deduce the subfolders that need to be transcribed
    # use join path
    
    with open ("transcription_log.json", "r") as f:
          log = json.load(f)

    ep_names_done = [key for key in log[folder_key]["files"].keys() 
                    if log[folder_key]["files"][key]["split_done"] == True
                    and log[folder_key]["files"][key]["transcription_done"] == True] 
                    
                    # if this key doesn't exist, we have a problem
                    # in the split function, if we have a key, it has already been split and thus split_done == True
                    # but transcription_done is not initialized, so it is None.. which can lead to problems
                    # damn. if we init it, we might overwrite the transcription_done == True and do it again...

    print("Files with split_done == True and transcription_done == True  in this folder: ", len(ep_names_done), "\n")
  
    ep_folder_iterations = [x for x in split_sub_folders if os.basename(x) not in ep_names_done]

    text_folder = folder_key + "_text"

    try:
        # create text Directories
        os.mkdir(text_folder)
        print("Text Directory Created")
  
    except FileExistsError:

        print("Directory " , text_folder ,  " already exists")


#--- Transcribe segments and add punctuation

    for ep_path in ep_folder_iterations:
    
        sub_start = time.time()

        wav_files = glob.glob(ep_path+ "/*")
        wav_files = natsorted(wav_files)
        
        ep_name = os.path.basename(ep_path)
        output_text = ""

        for wav_file in wav_files:
        
            # transcribe wav file
            text = asr_model.transcribe([wav_file])[0]
        
            # concatenate text
            output_text += text + " "

        # add punctuation
        
        output_text = model.restore_punctuation(output_text)
        
        transc_time = round(time.time() - sub_start / 60, 2)
        #join path
        with open(os.path.join(text_folder,ep_name) + ".txt", "w") as f:
        
            f.write(output_text)

        # add information to log

        with open ("transcription_log.json", "r") as f:
            log = json.load(f)
        
        log[folder_key]["files"][ep_name]["transcription_done"] = True
        log[folder_key]["files"][ep_name]["transcription_time_min"] = transc_time

        with open ("transcription_log.json", "w") as f:
            json.dump(log, f, indent = 4, sort_key=True)
        
        print("EP named " + ep_path + " took " , time.time()-sub_start , "sec") #whops
    print("\n Whole folder took " , time.time()- start_time , "sec")

