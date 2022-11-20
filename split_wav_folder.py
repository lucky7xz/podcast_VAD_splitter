import os, random, time, shutil
from tqdm import tqdm

import librosa
import soundfile as sf
import glob

from VAD_wav_splitter import generate_splits

def split_podcast_folder(dirName, max_len, close_th, testing=False):

  folder_start_time = time.time()

  total_folder_duration = 0
  dur_print_switch = False

  resample_switch = 0

  file_list = glob.glob(dirName+"/*")
  wav_list = glob.glob(dirName+"/*.wav")


  print(" All Files len: ", len(file_list),"\n", " WAV Files len : ", len(wav_list), "\n",)
  print("Folder: ", dirName)
  

#-------------------------------------------------------------------------
  if set(wav_list) == set(file_list) and len(wav_list) > 0:
   
      print("\n All files in Folder are in .wav Format. Checking the sample rate (we need 16k) \n")

      sr_test_pick = random.choice([wav for wav in wav_list])
      sr_test1 = librosa.get_samplerate(sr_test_pick)
      sr_test_pick = random.choice([wav for wav in wav_list])
      sr_test2 = librosa.get_samplerate(sr_test_pick)
      sr_test_pick = random.choice([wav for wav in wav_list])
      sr_test3 = librosa.get_samplerate(sr_test_pick)

      # here we can do a for _ in 3 loop and check with all()


      if sr_test1 != 16000 or sr_test2 != 16000 or sr_test3 != 16000:

        print("No. We need to resample our data. SR of random picks :", sr_test1, sr_test2, sr_test3)
        print("mp3 to wav conversion is slow with librosa and torchaudio. Consider other software in pre-step.")

      else:

        print("Samplerate is 16k. No need to resample. SR of random picks :", sr_test1, sr_test2, sr_test3)
  
  else:

      print("\n Some/all files in Folder are not in .wav Format. Only .wav files are supported. \n")
      # print files that are not .wav
      print("Files that are not .wav: ", set(file_list) - set(wav_list))
      print("Please convert them to .wav and try again. \n") 
      return

#--------------------------------------------------------------------------
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
      
      for file in old_wav_files: 
        #os.remove(file)
        shutil.rmtree(file) # use for windows       
      
      #for file in old_wav_files: os.remove(file)

#--------------------------------------------------------------------------
  for wav_file in wav_list:

    start_time = time.time()
    wav_name = os.path.basename(wav_file).replace(".wav","")

    print("----file: ", wav_name) # for debugging
    
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

    generate_splits(split_dirName, wav_file, max_len, close_th, 0) # close_th should probably be adjusted with custom segment-merge function
    #generate_splits(dirName, wav_file, 210, 1.65, 0)

    print("Split", pivot, "/", list_len)
    pivot += 1
    
    print("---" ,time.time() - start_time , " seconds  for splitting " + wav_file + "---"  + "\n")
  
  old_vad_files = glob.glob("vad_files/*")
  old_temp_files = glob.glob("temp_files/*")
  old_checkpoint_files = glob.glob("pretrained_model_checkpoints/*")
  for file in old_vad_files: os.remove(file)
  for file in old_temp_files: os.remove(file)
  for file in old_checkpoint_files: os.remove(file)

  print("---" ,time.time() - folder_start_time , " seconds  for splitting entire folder --- \n")



def split_podcast_folders(path_to_folders, max_len, close_th, testing=False):

    split_done = []


    with open (path_to_folders, "r") as f:
        folder_names = f.readlines()
        folder_names = [x.strip() for x in folder_names]

        length = len(folder_names)
    
    fcount = 1

    for folder_name in folder_names:
        if folder_name[0] == "#":
            continue
        else:
            split_podcast_folder(folder_name, max_len, close_th, testing)
            split_done.append(folder_name)
            print("Split Done: ", split_done, fcount,"/",length)

    with open("split_done.txt", "w") as f:
        for item in split_done:
            f.write(item)
      
    
    #clean_temp_files()
    