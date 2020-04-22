import json
import os
import csv
import requests
import praw
import sys
import praw.models
import datetime as dt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# setup pushshift API (Input time HERE)
month = int(sys.argv[1])
day = int(sys.argv[2])
month_2 = int(sys.argv[3])
day_2 = int(sys.argv[4])

numberOfComments = 20
subname = "coronavirus"
analyzer = SentimentIntensityAnalyzer()

# setup praw API
keys = {}
with open("pwd.json","r") as f:
    keys = json.loads(f.read())
client = keys['client']
secret = keys['secret']
username = keys['username']
userpwd = keys['userpwd']
reddit = praw.Reddit(client_id=client, client_secret=secret, password=userpwd, username=username, user_agent='fetch_script')

# Get Posts from Pushshift API
def getPushshiftData(after, before, sub):
    url = 'https://api.pushshift.io/reddit/search/submission/?&size=1000&after='+str(after)+'&before='+str(before)+'&subreddit='+str(sub)
    r = requests.get(url)
    data = json.loads(r.text)
    return data['data']

# Get comments from post
def collectSubData(subm):
    subData = list()
    sub_id = subm['id']
    title = subm['title']
    created = dt.datetime.fromtimestamp(subm['created_utc'])
    permalink = subm['permalink']

    #praw stuff
    submission = reddit.submission(id=sub_id)
    if (submission.score >= 20):
        count = 0
        title_vs = analyzer.polarity_scores(submission.title)['compound']
        submission.comment_sort = 'best'
        submission.comments.replace_more(limit=0)
        comments = submission.comments.list()
        nc = numberOfComments
        if (len(comments) <= numberOfComments):
            nc = len(comments)
        while count < nc:
            top_level_comment = comments[count]
            comment_id = top_level_comment.id
            comment_text = top_level_comment.body
            comment_score = top_level_comment.score
            if (comment_score < 1):
                count = count+1
                continue
            comment_text_updated = comment_text.replace('\r', '').replace('\n', '')
            comment_vs = analyzer.polarity_scores(comment_text_updated)['compound']
            subData.append((comment_id,comment_vs,title_vs,comment_text_updated,title,created,permalink))
            subStats[comment_id] = subData
            subData = list()
            count = count+1

#Add to Excel file as output
def updateSubs_file():
    upload_count = 0
    file ="data/" + str(month) + "-" + str(day) +".csv"
    with open(file, 'w', newline='', encoding='utf-8') as file:
        a = csv.writer(file, delimiter=',')
        headers = ["Comment ID","Comment_VS","Title_VS", "Comment","Title","Publish Date","Permalink"]
        a.writerow(headers)
        for sub in subStats:
            a.writerow(subStats[sub][0])
            upload_count+=1

def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))

after = int(dt.datetime(2020,month,day).timestamp())
before = int(dt.datetime(2020,month_2, day_2).timestamp())
subCount = 0
subStats = {}

data = getPushshiftData(after, before, subname)
while len(data) > 0:
    for submission in data:
        collectSubData(submission)
        subCount+=1
    after = data[-1]['created_utc']
    data = getPushshiftData(after, before, subname)
print(str(len(subStats)) + " submissions have added to list")

updateSubs_file()
notify("Done", "Finished " + str(month) + " " + str(day) + " " + str(len(subStats)))
