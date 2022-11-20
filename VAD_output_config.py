def VAD_file_config(vad_text_source, max_len = 0): # 0 till in use

  ''' 
  Read the VAD file (speechbrain boundaries) and return the split config
  Mostly cosmetic changes to the file, but also some minor changes to the boundaries

  '''
  with open(vad_text_source, "r") as f:
    vad_text = f.read()

# Type 0 - non-speech ; Type 1 - speech
  vad_text = vad_text.replace("NON_SPEECH","0")
  vad_text = vad_text.replace("SPEECH","1")

  # Text to list
  vad_text = vad_text.split("\n")
  vad_hints = ""


  vad_text_edit_temp = []
  vad_text_edit = []

  j = 1

  for line in vad_text:

    if line == "":
      break

    seg_type = int(line.split(" ")[-1]) # 0 - non-speech ; 1 - speech

    start = float(line.split(" ")[2])
    end = float(line.split(" ")[4])
    speech_len_sec = round(end - start, 3)

    vad_text_edit_temp.append([j, start, end, seg_type, speech_len_sec])
    j += 1


  # should be able to re-merge segments, so that we almost reach max_len seconds per segment, and minimize the amount of segments, which would be nice for the accuracy of the model
  # we do this by merging segments of the all types (speech or non-speech), as long as the len of the segment sum is smaller than max_len
  # Later : use linked list. if the pivot is not too long, we check if we can merge it with the next segment
        # or hashmap. probably hashmap. max_len is needed for that.
    # !!! For now:
    

    vad_text_edit = vad_text_edit_temp

  return vad_text_edit
  

def vad_pre_print(vad_text_edit, max_len):

    # prints the VAD file as for split overview

    print("\nNR    ; START    ; END ;  TYPE ;    LEN \n")

    # Find maximal length of all segments
    n = max(len(str(x)) for l in vad_text_edit for x in l)

    # Print the rows
    for row in vad_text_edit:

       line = ''.join(str(x).ljust(n + 2) for x in row)
      
       if row[-1] > max_len:
          line = line + "- Too Long"
       print(line)
  
    print("#----------------------")