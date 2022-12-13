import os, random, time, glob, shutil
import librosa

import json

from VAD_wav_splitter import generate_splits, setup_split_device



def split_podcast_folder(dirName, max_len, close_th, testing=False):

  # EDIT FOR GPU
  device = setup_split_device("cpu") # "gpu" for cuda

  folder_start_time = time.time()
  
  file_list = glob.glob(dirName+"/*")
  wav_list = glob.glob(dirName+"/*.wav")


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

        #--------update log
        with open ("transcription_log.json", "r") as f:
          log = json.load(f)

        aprox_duration = round((sum(duration_of_picks)/4)* len(wav_list) / 3600, 2)


        log[dirName]["aprox_podcast_duration_hrs"] = aprox_duration

        with open ("transcription_log.json", "w") as f:
          json.dump(log, f, indent=4, sort_keys=True)
        #--------------------


        print("Aprox. duration of all .wav files in folder:", round(aprox_duration,2) , "hours \n")
 
  else:

      print("Some/all files in Folder are not in .wav Format. Only .wav files are supported. \n")
      print("Files that are not .wav: ", set(file_list) - set(wav_list))
      print("Please convert them to .wav and try again. Only .wav files are allowed in folders! \n") 
      return


#-----------------------Initiate Splitting-----------------------
  wav_list = glob.glob(dirName+"/*.wav")
  
  
  with open("transcription_log.json", "r") as f:
    log = json.load(f)
  
  print("Computing wav files that need to be split (according to log)...")
  wav_names_done = [key for key in log[dirName]["files"].keys() if log[dirName]["files"][key]["split_done"] == True ]

  print("Files with split_done == True  in this folder: ", len(wav_names_done), "\n")
  
  #wav_names_done (not) X wav_list = wav_paths_left
  wav_file_iteration = [wav_file for wav_file in wav_list if os.path.basename(wav_file).replace(".wav","") not in wav_names_done]

  
  list_len = len(wav_list) - len(wav_names_done)
  pivot = 1

  split_dirName = dirName + "_split" # new folder for split episodes  

  if not os.path.exists(split_dirName):
      # Create split Directory
      os.mkdir(split_dirName)
      print("Directory " , split_dirName ,  " Created ") 

  else:
      print("Directory " , split_dirName ,  " already exists")
      split_subFolders = glob.glob(split_dirName + "/*")
      #print("Subfolders in split folder: ", split_subFolders) # for debugging

      print("Deleting files in unfinised folders...")
      
      #split_subFolder_names = [os.path.basename(subFolder) for subFolder in split_subFolders]
     
      # if file in wav_file_iteration (with split_done = False) is in split_subFolders, it means split was interrupted
      bad_wav_folders = [path for path in split_subFolders if os.path.basename(path).replace(".wav","") in [os.path.basename(file).replace(".wav","") for file in wav_file_iteration]] 
      
      print("   :",(bad_wav_folders))

      #   delete all files in bad_wav_folders (.rmtree removes individual wav splits too)
      for file in bad_wav_folders: shutil.rmtree(file) ######
      print("Deleted files in unfinised folders...")
  

#------------------------------------------------------------------
  for wav_file in wav_file_iteration:



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
      
        subdirName = os.path.join(split_dirName, wav_name)
        os.mkdir(subdirName)
        print("Directory " , subdirName ,  " Created ") 

    except FileExistsError:
        # this exceptions will never be raised (i think)
        print("Directory " , subdirName ,  " already exists")
        

    #---- max len (in seconds), close_th, count (needs to be zero)-------------------

    generate_splits(split_dirName, wav_file, max_len, close_th, 0)
    
    #generate_splits(dirName, wav_file, 210, 1.65, 0) # close_th should probably be adjusted when new custom segment-merge function is used


    #--------------------------------------------------------------------------------

    split_time = round((time.time() - start_time) / 60, 2)
    split_count = len(glob.glob(subdirName+"/*"))

    with open ("transcription_log.json", "r") as f:
      log = json.load(f)

# VMASSCVV: title, split_done, split_type, split_count, split_duration, transcription, transcription_type

    #create entry for episode in log. split time is in minutes
    log[dirName]["files"][wav_name] = {"title": "", "split_done": True, "file_split_count":split_count, "split_time_min": split_time, "split_type":device, "transc_type": "", "transc_done": False}

    with open ("transcription_log.json", "w") as f:
      json.dump(log, f, indent=4, sort_keys=True)
  
    print("Split episode", pivot, " out of ", list_len, "(left out of total in folder)")


    print("---" ,split_time, " minutes  for splitting " + wav_file + "---"  + "\n")
    pivot += 1


  # Folder is split. Delete aux Directories

  old_vad_files = glob.glob("vad_files/*")
  old_temp_files = glob.glob("temp_files/*")
  old_checkpoint_files = glob.glob("pretrained_model_checkpoints/*")
  for file in old_vad_files: os.remove(file)
  for file in old_temp_files: os.remove(file)
  for file in old_checkpoint_files: os.remove(file)

  print("---" ,time.time() - folder_start_time , " seconds  for splitting entire folder --- \n(some files might be done in prev iterations, check sum of ep logs to determine true duration)  \n")


#---------------------------------------------------------------------------------------------------------  
#---------------------------------------------------------------------------------------------------------

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
            log[folder_name]["ep_count"] = len(log[folder_name]["files"].keys())
            
            with open("transcription_log.json", "w") as f:
                json.dump(log, f, indent=4, sort_keys=True)
          #--------------------
        
        else:

          #--- initiate log dict for folder (aprox_podcast_duration is added in split_podcast_folder function)
            log[folder_name] = {"files":{}, "split_done": False, "ep_count":0, "transc_done": False, "aprox_podcast_duration_hrs": 0}

            # update json
            with open("transcription_log.json", "w") as f:
                json.dump(log, f, indent=4, sort_keys=True)

            split_podcast_folder(folder_name, max_len, close_th, testing)
          
          # if function terminates, update split_done to True in log file
          #--------update log
            with open("transcription_log.json", "r") as f:
                log = json.load(f)

            log[folder_name]["split_done"] = True
            log[folder_name]["ep_count"] = len(log[folder_name]["files"].keys())
            
            with open("transcription_log.json", "w") as f:
                json.dump(log, f, indent=4, sort_keys=True)
          #--------------------

            print("Folder", folder_name, "split. Progress:", fcount, "/", length)



    '''

json dict structure and init


podcasts {

  "on_with kara": files:


                          VMASSCVV: title, split_done, split_type, split_count, split_duration, transcription, transcription_type




                      

                  split_done:
                  split_type:
                  transc_done:
                  transc_type:
                  aprox_podcast_duration:

}

main. create empty .json

split_folders -  init podcast_name = key, set split done, set ep count

split__folder - set aprox folder duration, add info about episode - set etc /episode


'''
