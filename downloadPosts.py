#! /usr/bin/python3
#USAGE: python3 downloadPosts.py "MY_IG_USERNAME" "MY_IG_PASSWORD" "IG_SCHOOL_PROFILE"
import instaloader
import threading
import sys
import time

def printGetTime():
    currentTime = time.strftime("%H:%M:%S", time.localtime())
    print(currentTime)
    return currentTime

def download(followers):

    global pubblic
    global private

    ig = IG()
    pubb, priv = ig.downloadProfiles(followers)

    printStatMutex.acquire()

    pubblic +=pubb
    private +=priv

    # consistency of data
    print(f"\n\n{pubblic}/{totFollowers} pubblic profiles")
    print(f"{private}/{totFollowers} private profiles\n\n")
    print(f"{pubblic + private}/{totFollowers} parsed")

    printStatMutex.release()


def getFollowers(username):
    #returns followers list
    #temporary instaloader instance to get followers. Credentials needed
    #only here
    myUsername = sys.argv[1] 
    myPassword = sys.argv[2]

    temp = instaloader.Instaloader()
    temp.login(myUsername, myPassword)

    # '<Profile noegurieri (5677279416)>'
    followers = [str(follower).split()[1] for follower in instaloader.Profile.from_username(temp.context, username).get_followers()]

    temp.close()
    return followers

startTime = printGetTime()

MAX_PER_THREAD = 30
MAX_THREADS = 3

pubblic = 0
private = 0
printStatMutex = threading.Lock()

#global variables
followers = getFollowers(sys.argv[3]) #read only
totFollowers = len(followers) #read only
mutex = threading.Lock()
i = 0 
hasFollowersToParse = True


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

    def getNextFollowers(self):
        global i
        global hasFollowersToParse
        global mutex
        #global followers
        #global totFollowers
        #global MAX_PER_THREAD
        #global MAX_THREADS

        mutex.acquire()
        
        if hasFollowersToParse == False:
            mutex.release()
            return False

        followersToReturn = followers[i:min(i+MAX_PER_THREAD, totFollowers)]
        if i + MAX_PER_THREAD >= totFollowers: hasFollowersToParse = False
        else: i+=MAX_PER_THREAD

        mutex.release()

        return followersToReturn


    def downloadPosts(self, profile, resume=False):
        #Download posts of a profile. returns 0 on success, 1 else

        count = 0
        posts = profile.get_posts()

        try:
            self.L.download_profilepic(profile)
            count +=1
            for post in posts:
                # print(post.tagged_users)
                self.L.download_post(post, profile.username)
                count+=1
            print(f"\n{profile.username}: {count}\n")

        # except instaloader.exceptions.LoginRequiredException: 
        except: print(f"\nEXCEPTION {profile.username}: {count}\n")

    def downloadProfiles(self, followers):
        #download n profiles

        threads = []
        pubblic = 0
        private = 0

        for follower in followers:

            profile = instaloader.Profile.from_username(self.L.context, follower)
            #profile.mediacount returns number of posts. Only posts are pubblic
            if profile.is_private == False and profile.mediacount != 0:

                pubblic+=1
                print(f"{profile.username} started")
                thread = threading.Thread(target=self.downloadPosts, args=[profile])
                thread.start()
                threads.append(thread)

            else:
                private+=1
                print(f"{profile.username} either private or no posts")

        # for thread in threads: thread.start()
        for thread in threads: thread.join()

        nextFollowers = self.getNextFollowers()
        if nextFollowers == False:
            self.L.close()
            return pubblic, private

        else:
            pubb, priv = self.downloadProfiles(nextFollowers) #recursion
            return pubblic + pubb, private + priv








threads = []
j = 0
while j < MAX_THREADS and hasFollowersToParse: #init phase

    mutex.acquire()

    thread = threading.Thread(target = download, args= [followers[i:min(i+MAX_PER_THREAD, totFollowers)]])
    threads.append(thread)
    thread.start()
    j+=1
    if i + MAX_PER_THREAD >= totFollowers: hasFollowersToParse = False
    else: i+=MAX_PER_THREAD

    mutex.release()

for thread in threads: thread.join()

finishTime = printGetTime()
print(startTime, finishTime)
