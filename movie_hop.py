from time import strftime
import datetime
import re
import imdb

ia = imdb.IMDb()
movies_times = {}

def get_time(movie):
    obj = ia.search_movie(movie)[0]
    ia.update(obj)
    time = str(re.findall(r'\d+', obj['runtime'][0])[0])
    return time


class Movie:
    def __init__(self, name=None, time=None, showtimes=None):
        self.name = name
        self.time = time
        self.showtimes = showtimes
    def __str__(self):
        return self.name + " " + self.time + " min "
    def __repr__(self):
        return self.__str__()
    def __nonzero__(self):
        return self.name != None


def parse_line(line):
    """@return {array<string>}"""
    showtimes = []
    chars = []
    for i in range(len(line)):
        chars.append(line[i])
        if line[i] == "m":  # end of "am" or "pm"
            time = ''.join(chars)
            showtimes.append(time)
            chars = []
    return showtimes


def parse_file():
    """Return array<Movie>"""
    movies = []
    print "Fetching runtimes...\n"
    with open('paste.txt', 'r') as f:
        line = f.readline()
        mv = Movie()
        while line:
            if line[:8] == "Standard": mv.showtimes = parse_line(line[8:])
            elif line[:2] == "3D": mv.showtimes = parse_line(line[2:])
            else:
                if mv: movies.append(mv)
                name = line.strip()
                time = get_time(name)
                mv = Movie(name, time)
                movies_times[name] = time
                print(mv.name + ": " + mv.time + "min")
            line = f.readline()
        movies.append(mv)
    return movies


def get_start_end_times(movies):
    start = []
    end = []
    for mv in movies:
        for time in mv.showtimes:
            obj = datetime.datetime.strptime(time[:-2], "%H:%M")
            if "pm" in time: obj += datetime.timedelta(hours=12)
            start.append( (obj, mv.name) )
            endtime = obj + datetime.timedelta(minutes=int(mv.time))
            end.append( (endtime, mv.name) )
    return start, end


def find_close_movies(start, end):
    """Return array<datetime obj, name>"""
    result = []
    for first in end:
        for second in start:
            if first[0] < second[0] and first[1] != second[1]:  # check for same movie
                wait_time = (second[0]-first[0]).seconds/float(60)
                first_start = (first[0] + datetime.timedelta(minutes=-int(movies_times[first[1]])) ).strftime("%H:%M")
                first_label = first[1] + " (" + first_start + ") "
                second_start = second[0].strftime("%H:%M")
                second_label = second[1] + " ("+second_start + ")"
                result.append( (wait_time, first_label, second_label) )
    result.sort()
    return result


def hop():
    """Return movie pairings sorted from least to most wait time in between."""
    movies = parse_file()
    start, end = get_start_end_times(movies)
    pairs = find_close_movies(start, end)[:20]
    print "\nWait time, first movie (start time), second movie (start time)\n"
    for pair in pairs: print(str(int(pair[0])) + "min  " + pair[1] + pair[2])

hop()
