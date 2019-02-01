##This is a set of tools to parse and organize the Star Trek
##scripts from
##
##https://www.kaggle.com/gjbroughton/start-trek-scripts
##
##(no typo in the url above). For more details, see the readme.
##
##This code is licensed under the GPL [figure it out].


import os
import pandas as pd
import json
from pandas.io.json import json_normalize
pd.set_option('max_colwidth',25)
pd.set_option('max_columns',7)
import math
import random
import re

episode_list = pd.read_csv('episode_index_sorted.csv',index_col=['series','episode'])

def main():
    with open('all_series_lines.json') as f:
        d = json.load(f)
    shows = []
    for ser in d.keys():
        episodes = []
        for episode in d[ser].keys():
            characters = []
            for character in d[ser][episode].keys():
                char_lines = pd.DataFrame([[ser, episode, character, line] for line in d[ser][episode][character]], columns = ['ser', 'episode', 'character', 'line']) 
                characters.append(char_lines)
            episode_lines = pd.concat(characters, sort=False)
            episodes.append(episode_lines)
        ser_lines = pd.concat(episodes, sort=False)
        shows.append(ser_lines)
    return pd.concat(shows, sort=False)

def get_sowpods():
    with open('sowpods.txt') as f:
        words = f.readlines()
    return [w[:-1] for w in words]

class Episode():
    def __init__(self, series, number, text):
        self.series = series
        self.number = number
        while '\n ' in text or ' \n' in text:
            text = text.replace('\n ', '\n').replace(' \n', '\n')
        r1 = re.search(r'\{[^)}]+?\]',text)
        while r1 != None:
            text = (text[:r1.start()] + '['
                    + text[r1.start()+1:])
            r1 = re.search(r'\{[^)}]+?\]',text)
        r2 = re.search(r'\[[^\]\{]+?\}',text)
        while  r2 != None:
            text = (text[:r2.end()-1] + ']'
                    + text[r2.end():])
            r2 = re.search(r'\[[^\]\{]+?\}',text)
        r3 = re.search(r'\[[^\](]+?\)',text)
        while r3 != None:
            text = (text[:r3.end()-1] + ']'
                    + text[r3.end():])
            r3 = re.search(r'\[[^\](]+?\)',text)
        self.delimited_text = text

        self.scenes = self.find_scene_breaks()
        
        for r in (('\n', ' '), ('\r', ' '), (':', ': ')):
            raw_text = text.replace(*r)
        self.raw_text = raw_text.split()

        self.title = self.better_title()
        self.stardate = self.get_stardate()
        self.airdate = self.get_airdate()


    def get_title(self):
        return ' '.join(find_repeat(self.raw_text[:100]))

    def better_title(self):
        return episode_list.loc[(self.series,self.number)].title

    def get_stardate(self):
        segment = self.raw_text[:100]
        if 'Stardate:' in segment:
            return segment[segment.index('Stardate:')+1]
        elif 'Mission' in segment and 'Original' in segment:
            return ' '.join(segment[segment.index('Mission')+2:segment.index('Original')])
        else:
            return 'Not given'
        
    def get_airdate(self):
        i,j=0,0
        for word in self.raw_text[:100]:
            if 'Airdate' in word:
                i = self.raw_text.index(word)
                for item in self.raw_text[i:100]:
                    if re.search('[0-9]{4}',item):
                        j = self.raw_text.index(item)+1
                        break
                break
        if i == j == 0:
            return 'Not given'
        return ' '.join(self.raw_text[i+1:j])

    def find_scene_breaks(self):
        T = self.delimited_text
        scenes = []
        if 'Previously on' in T[:200]:
            T = T[:T.find('Previously on')+14]+']\n'+T[T.find('Previously on')+14:]
        if 'previously on' in T[:200]:
            T = T[:T.find('previously on')+14]+']\n'+T[T.find('previously on')+14:]
        if 'Previously, on' in T[:200]:
            T = T[:T.find('Previously, on')+15]+']\n'+T[T.find('Previously, on')+15:]
        if 'previously, on' in T[:200]:
            T = T[:T.find('previously, on')+15]+']\n'+T[T.find('previously, on')+15:]
        if 'Last time on' in T[:200]:
            T = T[:T.find('Last time on')+13]+']\n'+T[T.find('Last time on')+13:]
        T = T[T.find('\n['):]
        while True:
            scene_name = T[T.find('[')+1:T.find(']\n')].replace('\n', ' ')
            T = T[T.find(']\n')+1:]
            if '\n[' not in T or ']\n' not in T:
                scenes.append((scene_name,T))
                break
            else:
                next_scene = T.find('\n[')
                while T[T[next_scene:].find(']')+next_scene+1] != '\n':
                    next_scene = (T[T[next_scene:].find(']')+1+next_scene:].find('\n[')
                                  + T[next_scene:].find(']')+1+next_scene)
            scenes.append((scene_name,T[:next_scene]))
            T = T[next_scene:]
        return scenes
        
def title_list(series):
    with open('..\\Python\\startrek\\all_scripts_raw.json') as f:
        d = json.load(f)
    titles = []
    for episode in d[series].keys():
        e = Episode(series, 0, d[series][episode])
        print(e.title)
    return titles

def initial_segment(series, episode,length):
    with open('..\\Python\\startrek\\all_scripts_raw.json') as f:
        d = json.load(f)
    raw_text = d[series]['episode '+str(episode)].replace('\n',' ').replace('\r',' ').split()
    return raw_text[:length]

def build_episode_table(filename):
    with open(filename) as f:
        d = json.load(f)
    shows = []
    for series in d.keys():
        episodes = []
        for ep in d[series].keys():
            e = Episode(series, int(ep[ep.find(' '):]), d[series][ep])
            episode = pd.DataFrame([[series, e.number, e.title, e.stardate,
                                     e.airdate]], columns=['series','episode',
                                                           'title','stardate','airdate'])
            episodes.append(episode)
        shows.append(pd.concat(episodes))
    return pd.concat(shows).set_index(['series','episode'])
            

def find_repeat(l): #return first sublist that occurs twice consecutively
    for i in range(len(l)):
        for j in range(1,min(i,len(l)-i)):
            if l[i-j:i] == l[i:i+j]:
                return l[i:i+j]
    return ['Title', 'error']

def scene_split(scene): #splits a scene of an Episode into (character, line) pairs
    pieces = re.split(r"(\n[-A-Z0-9\n ']+(\[[-A-Za-z0-9\n ']+\])?:)", scene[1])
    return list(zip(pieces[1::3],pieces[3::3]))

def ep_details(series,episode):
    with open('..\\Python\\startrek\\all_scripts_raw.json') as f:
        d = json.load(f)
    return Episode(series, episode, d[series]['episode '+str(episode)])

def clean(string):
    return ' '.join(string.split())

def table_of_lines(series, episode):
    e = ep_details(series, episode)
    lines = []
    for i in range(len(e.scenes)):
        for line_tuple in scene_split(e.scenes[i]):
            character = clean(line_tuple[0])[:-1]
            if len(character) >= 5:
                if character[-5:] == ' [OC]':
                    character = character[:-5]                
            lines.append(pd.DataFrame([[series, e.title, e.number, i+1,
                                        clean(e.scenes[i][0]), character, clean(line_tuple[1])]],
                                        columns = ['series', 'ep_name', 'ep_number', 'scene_number',
                                                 'scene_loc', 'character', 'line']))
    return pd.concat(lines)

def list_characters(series, episode):
    t = table_of_lines(series, episode)
    return t.character.value_counts()

def make_big_line_table(filename):
    # filename: all_scripts_raw.json, wherever you have it
    with open(filename) as f:
        d = json.load(f)
    shows = []
    for (show,number) in [('TOS',79), ('TAS',21), ('DS9',172), ('TNG',175), ('VOY',159), ('ENT',96)]:
        episodes = []
        for ep_num in range(number+1):
            e = Episode(show, ep_num, d[show]['episode '+str(ep_num)])
            lines = []
            for i in range(len(e.scenes)):
                line_number = 0
                for line_tuple in scene_split(e.scenes[i]):
                    character = clean(line_tuple[0])[:-1]
                    if '[' in character and ']' in character:
                        character = character[:character.find('[')]+character[character.find(']')+1:]
                    lines.append(pd.DataFrame([[show, e.title, e.number, i+1, clean(e.scenes[i][0]).title(),
                                                line_number, clean(character), clean(line_tuple[1])]],
                                                columns = ['series', 'ep_name', 'ep_number', 'scene_number',
                                                           'scene_loc', 'line_number','character', 'line']))
                    line_number += 1
            episodes.append(pd.concat(lines))
            if ep_num % 10 == 9:
                print(str(ep_num+1)+' episodes of '+str(show)+' complete')
        shows.append(pd.concat(episodes))
        print(str(show)+' complete')
    return pd.concat(shows).set_index(['series','ep_number'])




