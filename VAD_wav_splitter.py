
import os, random, string

from VAD_output_config import VAD_file_config, vad_pre_print


import librosa
import soundfile as sf
from speechbrain.pretrained import VAD


# needed for new. if we only call function below, we get TypeError from VAD
VAD = VAD.from_hparams(source="speechbrain/vad-crdnn-libriparty", savedir="pretrained_models/vad-crdnn-libriparty")
#VAD = VAD.from_hparams(source="speechbrain/vad-crdnn-libriparty", savedir="pretrained_models/vad-crdnn-libriparty", run_opts={"device":"cuda"})

# use cpu or gpu for splitting 


def setup_split_device(dev="cpu", VAD=VAD):

    if dev == "cpu":
        #VAD = VAD.from_hparams(source="speechbrain/vad-crdnn-libriparty", savedir="pretrained_models/vad-crdnn-libriparty")
        pass
    elif dev == "gpu":
        VAD = VAD.from_hparams(source="speechbrain/vad-crdnn-libriparty", savedir="pretrained_models/vad-crdnn-libriparty", run_opts={"device":"cuda"})
        #bam bam @ yaml. check before calling function with dev="gpu"
        # not ready yet
    else:
        print("Please choose between cpu or gpu for splitting")
  
    return dev

def generate_splits(split_path,wav_file, max_len, close_th, count, testing=False): #1.25
  
  """
  Generate splits from a wav file

  close_th -> closing threshold (in seconds)
  count -> used to keep track of file numbering during recursion (needs to be 0 when calling the function !!!)
  max_len -> maximum length of a split (in seconds). Tuned to 210 seconds for the current dataset. max_len < ~60 seconds is not recommended atm  
  split_path -> path to the split folder

  """

  
  # Initial model run takes time, this is useful in testing.
        #testing = True
          # might be obsolote now
  
  if os.path.exists("vad_files/VAD_file_0.txt") and testing :
    
    vad_edit = VAD_file_config("vad_files/VAD_file_0.txt")

  else:
    
    
    boundaries = VAD.get_speech_segments(wav_file) # returns a list of speech boundaries
    boundaries = VAD.merge_close_segments(boundaries, close_th) # used to merge close segments
                      # |-------->  This should be replaced by costum function @ VAD_boundaries_config.py

    VAD.save_boundaries(boundaries, 
                        save_path='vad_files/VAD_file_' + str(count)+'.txt', 
                        print_boundaries=False) # save boundaries to file

  
    vad_edit = VAD_file_config('vad_files/VAD_file_' + str(count)+'.txt') # edit boundaries file for easier processing
 

  vad_pre_print(vad_edit, max_len) # print boundaries for overview/ debugging

  #remove path of wav file, remove .wav extension and remove Xtemp-tag (if present)
  wav_name = wav_file.split("/")[-1].replace(".wav","").split("Xtemp")[0]
                            
# often, difficult fragments are not split correctly (eg. 300s_seg - > 296s_seg & 3s_seg).
  while len(vad_edit) < 3:   # This is a workaround for that.
                           

    print("\n Prev segment unchanged. Energy split > \n")
    # Problem valuable seconds in the while loop at the end. that is problematic

    if close_th > 0.30: close_th -= 0.05
          
    boundaries = VAD.energy_VAD(wav_file,boundaries)
    boundaries = VAD.merge_close_segments(boundaries, close_th)
    
    VAD.save_boundaries(boundaries, 
                        save_path='vad_files/VAD_file_' + str(count)+'.txt',
                        print_boundaries=False)
    
    vad_edit = VAD_file_config('vad_files/VAD_file_' + str(count)+'.txt')
    vad_pre_print(vad_edit, max_len)



  for seg in vad_edit: # split wav file into segments from vad_edit (list of boundaries)

    # SEG  =:  0:NR    ; 1:START_POS   ; 2:END_POS ; 3:TYPE ;   4:LEN 

    if seg[3] == 1: # if speech segment (otherwise we skip the segment completely)

      # get offset and length
      seg_offset = seg[1]

      if seg_offset > 0.2 : seg_offset -= 0.2 # subtract 0.2 seconds from offset to avoid clipping

      # add 0.6 seconds to the end of the segment to avoid clipping (not perfect, but atm not a problem. Might be changed in the future)
      seg_len = seg[4] + 0.60 
      
      # if the length of the segment is smaller than max_len, we can just save the segment as is, and move on to the next segment
      if seg[4] < max_len:
        #print("seg 4 ", seg[4], max_len)
        
        y, sr = librosa.load(wav_file, sr=16000,
                             offset = seg_offset, 
                             duration = seg_len) # note we use seg_len, not seg[4] here
        
        wav_seg_path = split_path + "/" + wav_name + "/" + wav_name + "_" + str(count) +".wav" # create path for the split wav file
        sf.write(wav_seg_path, y ,sr) # write wav file form segment (y) to path (wav_seg_path) with sample rate (sr)

        count += 1

        print("Written", wav_seg_path, 
              "File Size:", os.path.getsize(wav_seg_path), 
              "Len:",  seg_len)
        
    

        if  os.path.getsize(wav_seg_path) < 500: # if the file is empty (less than 500 bytes)
          print(" WritingError --. File size is too small.\n") # print error message
          # used for debugging, prob not needed in the future

      else:

        print("Segment too long. Let's split it up...")
        y, sr = librosa.load(wav_file , sr=16000, offset = seg_offset, duration = seg_len) 

        #Creates a random string to be used for temp files (unlikely to repeat)
        temp_count = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        
        # use temp_count (after Xtemp tag) to avoid overwriting files
        temp_seg_path = "temp_files/" +wav_name + "Xtemp_" + str(temp_count) +".wav"

        
        sf.write(temp_seg_path, y ,sr)
        print("Written", temp_seg_path, "File Size:", os.path.getsize(temp_seg_path), "Len:",  seg_len)
       

        # generate splits recursively, update count
        count = generate_splits(split_path,temp_seg_path, max_len, close_th, count)
        

  return count # return count to keep track of the number of segments
