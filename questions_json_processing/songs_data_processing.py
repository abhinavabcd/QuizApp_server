import json
import random

def random_insert(lst, item):
    lst.insert(random.randrange(len(lst)+1), item)
    
def check_and_get_options(answer, list_options , count=4, insert_answer=True):
    while(True):
        retry = False
        k = random.sample(list_options, count-1)
        for i in k:
            if (i in answer):
                retry= True
        if(not retry):
            if(insert_answer):
                random_insert(k,answer)
            return k 



movies = json.loads(open("./song_data.json").read())
likes = []
for movie in movies.keys():
	for song in movies[movie].get("songs",[]):
		try:
			likes.append(int(song["fb_likes"]))
		except:
			pass

# songs and movies with min 30 likes will consider
movie_song = []

for movie in movies.keys():
    for song in movies[movie].get("songs",[]):
            try:
                if(int(song["fb_likes"])+(movies[movie].get("year_of_release",2000)-2000) >= 60):
                    movie_song.append([movie, song])
            except:
                    pass

questions = []
count = 0
all_movies = movies.keys()

all_music_directors = []
for movie in movies:
    movie = movies[movie]
    if(movie.get("music_directors",None)):
        movie["music_directors"] = a = (" and ".join(movie["music_directors"])).strip()
        if(a):
            all_music_directors.append(a)

for movie, song in movie_song:
    if(song.get("lyricists",[])):
        song.get("lyricists").sort()
        a = song["lyricists"].pop()
        if(song["singers"]):
            song["lyricists"] = " and ".join([' , '.join(song["lyricists"]), a])
        else:
            song["lyricists"] = a
        
    if(song.get("singers",[])):
        song.get("singers").sort()
        a = song["singers"].pop()
        if(song["singers"]):
            song["singers"] = " and ".join([' , '.join(song["singers"]), a])
        else:
            song["singers"] = a
            

def get_all_lyricists(movie_song):
    temp = {}
    for i in map( lambda x: x[1].get("lyricists",[]), movie_song):
        if(i):
            temp[i] = True
    return temp.keys()

def get_all_songs(movie_song):
    temp = {}   
    for i in map( lambda x: x[1].get("singers",[]), movie_song):
        if(i):
            temp[i] = True
    return temp.keys()




all_lyricists = get_all_lyricists(movie_song)
all_singers = get_all_songs(movie_song)
all_songs = map(lambda x : x[1]["name"] , movie_song)


 
for movie,song in movie_song:
    lyr = song.get("lyricists",None)
    if(lyr!=None):
        y = movies[movie].get("year_of_release",None)
        answer = lyr
        options = check_and_get_options(answer , all_lyricists,4)
        d = "Who wrote the lyrics for the song '"+song['name']+"' from '"+movie+("("+str(y)+")" if y else "")+"'"
        question = ["lyr_"+str(count),0 ,d , [], options , answer, "" , "" , 10, 10 , ['song','lyricists']]
        questions.append(question)
        count+=1
        print question

count = 0
for movie,song in movie_song:
    count+=1
    d = "'"+song["name"]+"' song title is from which movie ?"
        ##    options = check_and_get_options(map(lambda x:x["name"], movies[movie]["song"] ), all_songs, 4 , False)
    options = check_and_get_options(movie, all_movies , 4 )
    question = ["song_movie_"+str(count),0 ,d , [], options , movie, "" , "" , 10, 10 , ['song']]
    print question
    questions.append(question)

count = 0
for movie,song in movie_song:
    count+=1
    y = movies[movie].get("year_of_release",None)
    d = "Who are the singers for the song '"+song['name']+"' from '"+movie+("("+str(y)+")" if y else "")+"'"
    singer = song["singers"]
    options = check_and_get_options(singer, all_singers , 4)
    question = ["song_movie_"+str(count),0 ,d , [], options , singer, "" , "" , 10, 10 , ['singer','movie']]
    count+=1
    print question
    questions.append(question)

count = 0
for title in set(map(lambda x: x[0] , movie_song)):
    movie = movies[title]
    if(movie.get("music_directors",None)):
        d = "who is the music director of movie '"+title+"'"
        options = check_and_get_options(movie["music_directors"],all_music_directors,4)
        answer = movie["music_directors"]
        question = ["music_director_"+str(count),0 ,d , [], options , answer, "" , "" , 10, 10 , ['music_director','movie']]
        count+=1
        print question
        questions.append(question)
