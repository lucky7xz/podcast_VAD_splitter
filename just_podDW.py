
import urllib.request
import os
import requests
import re
from tqdm import tqdm




xml_url_dict ={"lex_fridman":"https://lexfridman.com/feed/podcast/",
                "politics_weekly_uk":"https://www.theguardian.com/politics/series/politicsweekly/podcast.xml",
                "australian_politics":"https://www.theguardian.com/australia-news/series/australian-politics-live/podcast.xml",
                "pitchfork_economics":"https://feeds.megaphone.fm/PPY5667678674",
                "politics_weekly_america":"https://www.theguardian.com/politics/series/politics-weekly-america/podcast.xml",
                "science_weekly":"https://www.theguardian.com/science/series/science/podcast.xml",
                "chips_with_everything":"https://www.theguardian.com/technology/series/chips-with-everything/podcast.xml",
            
               # "the_economist":"https://rss.acast.com/theeconomist",
               #'intel_from_theEconomist':"https://rss.acast.com/intelligencefromtheeconomist",
                "huberman_lab":"https://feeds.megaphone.fm/hubermanlab",
                "borrowed_future":"https://feeds.megaphone.fm/RM1336580306",
                "on_with_kara_swisher":"https://feeds.megaphone.fm/VMP1684715893",


                "ologies":"https://feeds.simplecast.com/FO6kxYGj",
            

                "strict_scrutiny":"https://feeds.simplecast.com/EyrYWMW2",
                "civics_101":"https://feeds.simplecast.com/jiCMS8G_",
                "pod_save_america":"https://feeds.simplecast.com/dxZsm5kX",
            
               
               
               #some xml have inverted enclosure structure, so you need different regex to catch files------------------
               
               
               
               }



olo = xml_url_dict['ologies']
dir_name = 'ologies'

hub = xml_url_dict['huberman_lab']
dir_name = 'huberman_lab'
    

civics = xml_url_dict['civics_101']
dir_name = 'civics_101'

#----
pivot =  civics
#last dir name

#chips with everything
#@ podcasts to dw - tier 1
# huberman
# borrowed future

'''
https://podbay.fm/p/strict-scrutiny
https://podbay.fm/p/on-with-kara-swisher
https://podbay.fm/p/ologies-with-alie-ward
https://podbay.fm/p/civics-101
https://podbay.fm/p/ted-talks-daily
https://podbay.fm/p/the-jimmy-dore-show
https://podbay.fm/p/the-dave-ramsey-show
https://podbay.fm/p/huberman-lab
https://podbay.fm/p/pod-save-america
'''





print("Podcat pivot name:",pivot)
#------------------get the xml file------------------
r = requests.get(pivot)
json_data = r.text


regex = '<item>(.*?)</item>'
pattern = re.compile(regex, re.DOTALL)
item_list = pattern.findall(json_data)
#item_list = item_list.split('/n/t/t')


# check the items in the list
count = 0
print("\nPrinting Demo items")
for item in tqdm(item_list):
    if count % 100 == 0:
        #print(item)
        print('-----------')
        count += 1



#------------------get the mp3 files------------------
r_title = re.compile(r'<title>(.+?)</title>')
r_link = re.compile('<enclosure url=\"(.*?)\"')
r_link_B = re.compile('<enclosure(?:.*?)url=\"(.*?)\"')


# switch to directory on D: drive, in the podcast folder

os.chdir('D:\\podcasts\\')


#check if file exists
if not os.path.exists(dir_name):
    os.makedirs(dir_name)


aux_count = 0

for item in tqdm(item_list):
   

    title = r_title.findall(item)[0].replace('&#8211;','-')
    link = r_link.findall(item) #link = r_link.findall(item)[0
    

    
    if len(link) == 0:
        print("RE switch !")
        link = r_link_B.findall(item)[0]

    else:
        link = r_link.findall(item)[0]
    
    print(len(link),link)
    mp3_name = link.split('/')[-1] #depending on the file name, you may need to change this

    if "?updated=" in mp3_name:
        mp3_name = mp3_name.split('?updated=')[0]

    if '?aid=rss' in mp3_name:
        mp3_name = mp3_name.split('?aid=rss')[0]
        mp3_name = mp3_name.replace('.mp3','_'+str(aux_count)+'.mp3')
        aux_count += 1

#check if file dir_name+'/'+mp3_name already exist, skip if it does

    if os.path.isfile(dir_name+'/'+mp3_name):
        print(dir_name+'/'+mp3_name,' already exist, skip')
        continue

    else : urllib.request.urlretrieve(link, dir_name+'/'+mp3_name)
     # show download speed
    print('Downloaded', mp3_name, 'at', link)

    # with open(dir_name+'/'+mp3_name, "wb") as f:
    #     print("Downloading %s" % mp3_name)
    #     response = requests.get(link, stream=True)
    #     total_length = response.headers.get('content-length')
  

    
