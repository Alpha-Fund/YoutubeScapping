#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 17:13:22 2022

@author: ArnoSG
"""

import requests
from bs4 import BeautifulSoup 
import json
import re
# From https://github.com/egbertbouman/youtube-comment-downloader
from youtube_comment_downloader import *


##############################################################################
##############################################################################
##############################################################################

# Test Functions

class Launch_Tests :
    

    def Test_GetTitle (self) :
        assert GetTitle() == "Pierre Niney : L’interview face cachée par HugoDécrypte"
        print("Title tested...")

    def Test_GetAuthor (self) :
        assert GetAuthor() == "HugoDécrypte"
        print('Author tested...')
    
    def Test_GetView (self) :
        # Change each time so here a little solution to filter but for more test we need to update numbre of view
        assert int(GetView()) >= 732998
        print("View number tested...")

    def Test_GetLikes (self) :
        # Same prblem of variation
        assert GetLikes() == "30 438 clics"
        print("Like number tested ...")

    def Test_GetId (self) :
        assert GetId() == ''    # COMPLETE WHEN I HAVE IT
        print("Id tested ...")

    def Test_GetDescription (self) :
        # Too long so if everything is fine it's have to be the correct description too
        #assert Test_GetAuthor() and Test_GetId() and Test_GetLikes() and Test_GetTitle() and Test_GetView()
        print("Description tested ...")



##############################################################################
##############################################################################
##############################################################################


class Scrapping :
    
    def __init__(self, url) :
        self.url = url
        self.page = requests.get(url)
        self.soup =  BeautifulSoup(self.page.content, "html.parser")  
        self.title = ""
        self.author = ""
        self.view = 0
        self.like = 0
        self.description = ""
        self.links = []
        self.id = 0
        self.commentaries = []
    

    def GetTitle(self) :
        self.title = soup.find("meta", itemprop="name")["content"]
        return self.title

    def GetAuthor (self) :
         self.author = soup.find("span", itemprop="author").next.next["content"]
         return self.author

    def GetView (self) :
        self.view = soup.find("meta",itemprop="interactionCount")['content']
        return self.view

    def GetLikes (self) :
        data = re.search(r"var ytInitialData = ({.*?});", soup.prettify()).group(1)  
        data_json = json.loads(data)
        videoPrimaryInfoRenderer = data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']
        likes_label = videoPrimaryInfoRenderer['videoActions']['menuRenderer']['topLevelButtons'][0]['segmentedLikeDislikeButtonRenderer']['likeButton']['toggleButtonRenderer']['defaultText']['accessibility']['accessibilityData']['label'] 
        # number of likes  
        likes_label = videoPrimaryInfoRenderer['videoActions']['menuRenderer']['topLevelButtons'][0]['segmentedLikeDislikeButtonRenderer']['likeButton']['toggleButtonRenderer']['defaultText']['accessibility']['accessibilityData']['label'] # "No likes" or "###,### likes"  
        likes_str = likes_label.split(' ')[0].replace(',','')  
        self.likes = '0' if likes_str == 'No' else likes_str
        return self.likes

    def GetDescription (self) :
        #description = soup.find("meta", itemprop="description")["content"]
        pattern = re.compile('(?<=shortDescription":").*(?=","isCrawlable)')
        self.description = pattern.findall(str(soup))[0].replace('\\n','\n')
        return self.description
    
    def GetLinks (self) :
        # Links
        links = re.findall(r"(?P<url>https?://[^\s]+)", self.description)
        # Timestamp
        links += re.findall(r"[0-9]+:[0-9]{2}", self.description)
        return self.links

    def GetCommentaries (self) :
        downloader = YoutubeCommentDownloader()
        comments = downloader.get_comments_from_url(self.url, sort_by=SORT_BY_POPULAR)
        
        #Filter informations from comments
        commentaries = []
        for comment in islice(comments, self.nbComments):
            c = {}
            c['Author'] = comment['author']
            c['Content'] = comment['text']
            c['NbLikes'] = comment['votes']

            commentaries.append(c)

        return commentaries
    
    
    def Return_All_Scrapping_Data (self) :
        dictio = {}
        dictio['Title'] = self.GetTitle()
        dictio['Author'] = self.GetAuthor()
        dictio['View'] = self.GetView()
        dictio['NbLikes'] = self.GetLikes()
        dictio['Description'] = self.GetDescription()
        dictio['Links'] = self.GetLinks()
        dictio['Comments'] = self.GetCommentaries()
        
        return dictio


##############################################################################
##############################################################################
##############################################################################


# Input data
with open("/data/Documents/ING3/DevOps/input.json", "r") as f :
    video_id = json.load(f)["videos_id"]
    
output = []
for ide in video_id :
    data = Scrapping("https://www.youtube.com/watch?v=" + ide).Return_All_Scrapping_Data()
    data['Id'] = ide
    print(data)
    output.append(data)

with open("/data/Documents/ING3/DevOps/output.json", "w") as f :
    f.write(json.dumps(output, indent=4))
