# Fetch comments from r/coronavirus

I have written a simple python script that exports an Excel file of all the comments that match our criteria. Our criteria include: The post most has more than one upvote at the time of scrapping, and we will take the 15 most upvoted comments of that post. I am using two Reddit APIs: Praw and Pushshift. Praw is used to get the comments of a post and Pushshift is used to gather the posts. The reason why Pushshift is not used to gather the comments is because Pushshift database is not updated in real time as a tradeoff for faster response time. As a result, most comments will have the same score. With Praw I was able to accurately get the top comments we wanted. We plan on running this script to gather data from February to Mid-April.  

 
