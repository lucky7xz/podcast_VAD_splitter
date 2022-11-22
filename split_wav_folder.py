import os, random, time, glob, shutil
import librosa

import json

from VAD_wav_splitter import generate_splits, gpu_split





def split_podcast_folder(dirName, max_len, close_th, testing=False):

  folder_start_time = time.time()
  
  file_list = glob.glob(dirName+"/*")
  wav_list = glob.glob(dirName+"/*.wav")


  #create new json, or import existing json.
  if True:
    pass #-------- !!!!!
  # read in transcription_log.json
  # also output transcriptions to podcastName_transc

  else:
    #create new csv file
    pass

     #split_log = folder, ep, done, gpu_split, split_count, total_time, split_time, aprox_total_time



  # clean up checkpoint files created by VAD model (if any)
  if os.path.exists("pretrained_model_checkpoints"):
    cp_list = glob.glob("pretrained_model_checkpoints/*")
    for file in cp_list: os.remove(file)

  print("-------- Folder to be split: ", dirName, "--------")
  print("All Files len: ", len(file_list),"\n", 
        "  WAV Files len : ", len(wav_list), "\n")
  

#-------------------- Check files to be split --------------------
  if set(wav_list) == set(file_list) and len(wav_list) > 0:
   
      print("\n All files in Folder are in .wav Format. Picking 4 random files to check sample rate (we need 16k) \n")

      sr_test_picks = [random.choice([wav for wav in wav_list]),
                       random.choice([wav for wav in wav_list]),
                       random.choice([wav for wav in wav_list]),
                       random.choice([wav for wav in wav_list])] 

      sr_of_picks = [librosa.get_samplerate(sr_test_pick) for sr_test_pick in sr_test_picks]

      # while we're at it, let's get the duration of the random files

      duration_of_picks = [librosa.get_duration(filename=sr_test_pick) for sr_test_pick in sr_test_picks] 


      if not all(sr == 16000 for sr in sr_of_picks):

        print("Some wav. files need resampling. SR of random picks :", sr_of_picks)
        print("Sometimes other SRs could work too, but 16k is optimal \n")

      else:

        print("Samplerate of random picks is 16k. No need to resample. SR of random picks :", sr_of_picks)
        print("Aprox. duration of all .wav files in folder:", (sum(duration_of_picks)/4)* len(wav_list) / 60 / 60 , "hours \n")
 
  else:

      print("Some/all files in Folder are not in .wav Format. Only .wav files are supported. \n")
      print("Files that are not .wav: ", set(file_list) - set(wav_list))
      print("Please convert them to .wav and try again. Only .wav files are allowed in folders! \n") 
      return


#-----------------------Initiate Splitting-----------------------
  wav_list = glob.glob(dirName+"/*.wav")

  split_dirName = dirName + "_split"

  list_len = len(wav_list)
  pivot = 1

  if not os.path.exists(split_dirName):
      # Create split Directory
      os.mkdir(split_dirName)
      print("Directory " , split_dirName ,  " Created ") 

  else:
      print("Directory " , split_dirName ,  " already exists")
      print("Deleting old files")
      old_wav_files = glob.glob(split_dirName + "/*")
      

      # REMOVE - WE CHECK FOR FILES
      for file in old_wav_files: shutil.rmtree(file) ######
        
   
#------------------------------------------------------------------
  for wav_file in wav_list:



    start_time = time.time()

    print("\n--- Splitting: ", wav_file, "...")
    wav_name = os.path.basename(wav_file).replace(".wav","")

    
    try:
      # create aux Directories
        os.mkdir("vad_files")
        os.mkdir("temp_files")
        print("Aux Directories Created")
  
    except FileExistsError:

      old_vad_files = glob.glob("vad_files/*")
      old_temp_files = glob.glob("temp_files/*")
      for file in old_vad_files: os.remove(file)
      for file in old_temp_files: os.remove(file)

    try:
      # Create split sub-Directory
        #subdirName = dirName + "/" + wav_name
        subdirName = os.path.join(split_dirName, wav_name)
        os.mkdir(subdirName)
        print("Directory " , subdirName ,  " Created ") 

    except FileExistsError:
        print("Directory " , subdirName ,  " already exists")
        old_dir_files = glob.glob(subdirName+"/*")
        for file in old_dir_files: os.remove(file)

    # max len (in seconds), close_th, count (needs to be zero)

    generate_splits(split_dirName, wav_file, max_len, close_th, 0) 
    #generate_splits(dirName, wav_file, 210, 1.65, 0) # close_th should probably be adjusted when new custom segment-merge function is used

    print("Split", pivot, "/", list_len)
    #EDIT prep dict for json

    pivot += 1
    
    print("---" ,time.time() - start_time , " seconds  for splitting " + wav_file + "---"  + "\n")



  # Folder is split. Delete aux Directories

  old_vad_files = glob.glob("vad_files/*")
  old_temp_files = glob.glob("temp_files/*")
  old_checkpoint_files = glob.glob("pretrained_model_checkpoints/*")
  for file in old_vad_files: os.remove(file)
  for file in old_temp_files: os.remove(file)
  for file in old_checkpoint_files: os.remove(file)

  print("---" ,time.time() - folder_start_time , " seconds  for splitting entire folder --- \n(some files might be done in prev iterations, check sum of ep logs to determine true duration)  \n")



def split_podcast_folders(path_to_folders, max_len, close_th, testing=False):


    with open (path_to_folders, "r") as f:
        folder_names = f.readlines()
        folder_names = [x.strip() for x in folder_names]

        length = len(folder_names)
    
    fcount = 1

    for folder_name in folder_names:
        
        #load transcripton _log json

        with open("transcription_log.json", "r") as f:
            log = json.load(f)

        #check if folder name is in the set of keys in the log
        
        if folder_name in log.keys():
        
            if log[folder_name]["split_done"] == True:
              print("Folder", folder_name, "already split. Skipping...")
            
          #
            elif log[folder_name]["split_done"] == False: 

              #continue splitting episodes
              split_podcast_folder(folder_name, max_len, close_th, testing)

             # if function terminates, update split_done to True in log file
             #--------update log
              with open("transcription_log.json", "r") as f:
                log = json.load(f)

            log[folder_name]["split_done"] = True
            log[folder_name]["split_count"] = len(log[folder_name]["files"].keys())
            
            with open("transcription_log.json", "w") as f:
                json.dump(log, f)
          #--------------------
        
        else:

          #--- initiate log dict for folder
            log[folder_name] = {"files":{}, "split_done": False, "ep_count":0, "aprox_podcast_duration_hrs": 0}

            # update json
            with open("transcription_log.json", "w") as f:
                json.dump(log, f)

            split_podcast_folder(folder_name, max_len, close_th, testing)
          
          # if function terminates, update split_done to True in log file
          #--------update log
            with open("transcription_log.json", "r") as f:
                log = json.load(f)

            log[folder_name]["split_done"] = True
            log[folder_name]["split_count"] = len(log[folder_name]["files"].keys())
            
            with open("transcription_log.json", "w") as f:
                json.dump(log, f)
          #--------------------

            print("Folder", folder_name, "split. Progress:", fcount, "/", length)

# contienue cuz done, continue with nex ep, init as 0, if non-existet before.


def clear_split_done(): #EDIT 
    if os.path.exists("split_done.txt"): #EDIT
        os.remove("split_done.txt") #EDIT
        print("split_done.txt deleted") #EDIT
    else:
        print("split_done.txt does not exist")




    '''

json dict


podcasts {

  "on_with kara": files:


                          VMASSCVV: title, split_done, split_type, split_count, split_duration, transcription, transcription_type




                      

                  split_done:
                  split_type:
                  transc_done:
                  transc_type:
                  aprox_podcast_duration:

}

main. init .json

_folders -  init podcast_name, set split done

__folder - add info about episode, add info about whole folder


'''
