#! /usr/bin/python3
#USAGE: python3 lookingForSofia.py "MY_IG_USERNAME" "MY_IG_PASSWORD" "IG_SCHOOL_PROFILE"
import instaloader
import threading
import sys

class IG:
    def __init__(self):
        #quiet=True
        self.L = instaloader.Instaloader(
                            save_metadata=False,
                            download_pictures=True,
                            download_videos=False,
                            download_video_thumbnails=True,
                            download_comments=False,
                            download_geotags=False,
                            post_metadata_txt_pattern="")

    def checkProfile(self, profile, resume=False):
        
        metadata= [] #reset profile's information at every cycle
        matched = False

        metadata.append(profile.username.lower())
        metadata.append(profile.biography.lower())
        metadata.append(profile.full_name.lower())
    
        for data in metadata:
            if matched == True: break
            for sub in subStrs:
                if sub in data:
                    print(profile.username)
                    matched = True
                    break

    def checkProfiles(self, followers, close=False):
    #download n profiles
        
        threads = []

        for follower in followers:

            profile = instaloader.Profile.from_username(self.L.context, follower)

            thread = threading.Thread(target=self.checkProfile, args=[profile])
            thread.start()
            threads.append(thread)


        # for thread in threads: thread.start()
        for thread in threads: thread.join()

        if close == True: self.L.close()

def getFollowers(username):
    #returns followers list
    #temporary instaloader instance to get followers. Credentials needed
    #only here
    myUsername = sys.argv[1] 
    myPassword = sys.argv[2] 

    L = instaloader.Instaloader()
    L.login(myUsername, myPassword)
    
    print("fetching followers...")
    # '<Profile noegurieri (5677279416)>'
    followers = [str(follower).split()[1] for follower in instaloader.Profile.from_username(L.context, username).get_followers()]
    print("finished fetching followers")

    L.close()
    return followers



subStrs = ["sofia", "sofy", "sophy", "sophia", "sof", "sophja"] 

followers = getFollowers(sys.argv[3])
totFollowers = len(followers)
MAX_PER_THREAD = 30
MAX_THREADS = 3
i = 0 #contatore follower parsati
flag = True

def checkProfiles(followers, batchFinished=False):

    ig = IG()
    ig.checkProfiles(followers)


while i < totFollowers and flag:
    
    #reset
    j = 0 #contatore followe assegnati per thread
    threads = []

    while j < MAX_THREADS and flag: #init phase
        
        thread = threading.Thread(target = checkProfiles, args= [followers[i:min(i+MAX_PER_THREAD, totFollowers)]])
        threads.append(thread)
        thread.start()
        j+=1
        if i + MAX_PER_THREAD >= totFollowers: flag = False #tutti i followers già in coda per essere analizzati
        else: i+=MAX_PER_THREAD

    for thread in threads: thread.join()
