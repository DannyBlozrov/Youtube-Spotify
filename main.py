import requests
import spotipy
import time
import googleapiclient
from googleapiclient.discovery import build
#---------------------- youtube API and spotify API links---------------------


#https://developer.spotify.com/dashboard/applications/645b9968a7984ab0bd84c023c10c2a31
def yttime2secs(songlength:str)->int:
    """

    :param len: a string like PT4M12S that represents youtube video length
    :return: the time of youtube video in seconds
    """
    a=songlength.split("M")
    #a[0]- minutes
    #a[1] -seconds
    for letter in a[0]:
        if not (letter.isdigit()):
            a[0]=a[0].replace(letter,"")
    if (a[1]!=""):
        for letter in a[1]:
            if not (letter.isdigit()):
                a[1]=a[1].replace(letter,"")
    #print(a)
    if(a[1]!=""):
        return 60*int(a[0])+int(a[1])
    return 60*int(a[0])
def videoid_to_name_dur(videoid:str)->(str,int):
    """

    :param videoid: a video id
    :return: a tuple of the song name and its duration in seconds
    """
    try:
        a = youtube.videos().list(part='snippet,contentDetails', id=videoid)
        responce = a.execute()
        if not responce['items']:
            return None,None
        song_name = responce['items'][0]['snippet']['title']
        song_length = responce['items'][0]['contentDetails']['duration']
        song_length_int=yttime2secs(song_length)
        return song_name,song_length_int
    except:
        return None,None


######-------------------------Project goals-------------------------------------------------
## This project takes a url of a playlist.
#it creates a playlist on spotify,given a username and password(will need authentication later on)
# after taking url, it decomposes into videos.
# Each video is parsed, and then by the 'id' or 'title' we use the spotify search for same song.
#after finding said song(we can measure the difference in time,if its approx same length, we will deduce it is the same song)
#we will add said song into the playlist.
#once we iterated through the entire youtube playlist- we are done



if __name__ == '__main__':
    try:
        yt_api_key = 'AIzaSyDvXxKrz2IIHsns3kdHddEHlLGpYdYDpSU'
        spoti_client_id = '645b9968a7984ab0bd84c023c10c2a31'
        spoti_client_secret = '5ca3d5cadfcd48deb11e204a52e223b1'
        dashboard_uri = 'https://open.spotify.com/'
        scope = 'playlist-modify-private,playlist-modify-public'
        try:
            youtube=build(serviceName='youtube',version='v3',developerKey=yt_api_key,num_retries=3)
            time.sleep(1)
        except:
            print("Crashed at youtube build stage")

        #the scope allows us to create a playlist and insert songs

        #--------------------- user input----------------------------
        yt_playlist_url=input("Insert youtube playlist URL\n")
        youtube_playlist_id=yt_playlist_url.split("list=")[1]
        print("Youtube playlist id =",youtube_playlist_id)
        spotify_playlist_name=input("Enter Spotify playlist name\n")
        spotify_playlist_description=input("enter Spotify playlist description\n")
        #-------------------- spotify create playlist-------------------------------
        auth=spotipy.oauth2.SpotifyOAuth(client_id=spoti_client_id,client_secret=spoti_client_secret,redirect_uri=dashboard_uri,scope=scope)
        token=auth.get_access_token(as_dict=False)
        sp=spotipy.Spotify(oauth_manager=auth)
        spotify_user=sp.me()
        spotify_id=spotify_user['id']
        spotify_playlist=sp.user_playlist_create(spotify_id,spotify_playlist_name,public=False,description=spotify_playlist_description)
        spotify_playlist_id=spotify_playlist['id']
        #-------------------------------LOOP YOUTUBE PLAYLIST--------------------------
        youtube_playlist=youtube.playlists().list(part='contentDetails,id',id=youtube_playlist_id)
        youtube_playlist=youtube_playlist.execute()
        youtube_playlist=youtube_playlist['items'][0]
        youtube_playlist_size=int(youtube_playlist['contentDetails']['itemCount'])
        songs_converted=0
        page_token=None
        #we search for the playlist id and take the first result in items.
        while(songs_converted<youtube_playlist_size):

            my_pl = youtube.playlistItems().list(part='snippet,contentDetails', playlistId=youtube_playlist_id,maxResults=50,pageToken=page_token)
            pl_responce = my_pl.execute()
            try:
                page_token=pl_responce['nextPageToken']
            except:
                page_token=None
            print("page token=",page_token)
            for item in pl_responce['items']:
                #each item here is a song
                vid_id=item['snippet']['resourceId']['videoId']
                songname,songlen=videoid_to_name_dur(vid_id)
                print(songname)
                try:
                    song_search=sp.search(songname,limit=3,type='track')
                    spotify_first_song = song_search['tracks']['items'][0]['external_urls']['spotify']
                    sp.playlist_add_items(spotify_playlist_id, items=[spotify_first_song])
                    songs_converted+=1
                except:
                    songs_converted+=1
                    continue
    except:
        print("ERROR,crashed somewhere")
