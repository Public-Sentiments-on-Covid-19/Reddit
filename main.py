import json
import os
import csv
import requests
import praw
import sys
import praw.models
import datetime as dt

# setup pushshift API (Input time HERE)
month_after = int(sys.argv[1])
day_after = int(sys.argv[2])
month_before = int(sys.argv[3])
day_before = int(sys.argv[4])

after = int(dt.datetime(2020,month_after,day_after).timestamp())
before = int(dt.datetime(2020,month_before, day_before).timestamp())
score = 1
numberOfComments = 20
subname = "coronavirus"
subCount = 0
subStats = {}

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
def getPushshiftData(after, before, sub, score):
    url = 'https://api.pushshift.io/reddit/search/submission/?&size=1000&score=>'+str(score)+'&after='+str(after)+'&before='+str(before)+'&subreddit='+str(sub)
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
    submission.comment_sort = 'best'
    submission.comment_limit = numberOfComments
    submission.comments.replace_more(limit=0)
    comments = submission.comments.list()
    for top_level_comment in comments:
        comment_id = top_level_comment.id
        comment_text = top_level_comment.body
        comment_score = top_level_comment.score
        # print(comment_id)
        # print(comment_text)
        if (comment_score < 1):
            continue
        comment_text_updated = comment_text.replace('\r', '').replace('\n', '')
        subData.append((title,created,permalink, comment_id, comment_text_updated))
        subStats[comment_id] = subData
        subData = list()

#Add to Excel file as output
def updateSubs_file():
    upload_count = 0
    file ="data/" + str(month_after) + "-" + str(day_after) +".csv"
    with open(file, 'w', newline='', encoding='utf-8') as file:
        a = csv.writer(file, delimiter=',')
        headers = ["Title","Publish Date","Permalink","Comment ID","Comment"]
        a.writerow(headers)
        for sub in subStats:
            a.writerow(subStats[sub][0])
            upload_count+=1

def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))

data = getPushshiftData(after, before, subname, score)
while len(data) > 0:
    for submission in data:
        collectSubData(submission)
        subCount+=1
    after = data[-1]['created_utc']
    data = getPushshiftData(after, before, subname, score)
print(str(len(subStats)) + " submissions have added to list")

updateSubs_file()
notify("Done", "Finished " + str(len(subStats)))
