import gzip
import json
import requests

from NwalaTextUtils.textutils import parallelTask
from NwalaTextUtils.textutils import genericErrorInfo

def rehydrate_tweet(twt_id, user_agent=''):

    #grandparent: https://github.com/JustAnotherArchivist/snscrape/issues/996
    #parent: https://github.com/JustAnotherArchivist/snscrape/issues/996#issuecomment-1615937362
    url = "https://cdn.syndication.twimg.com/tweet-result"
    querystring = {"id": twt_id,"lang":"en"}

    payload = ""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0" if user_agent == '' else user_agent,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://platform.twitter.com",
        "Connection": "keep-alive",
        "Referer": "https://platform.twitter.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers"
    }

    try:
        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
        return json.loads(response.text)
    except:
        genericErrorInfo()

    return {}

def paral_rehydrate_tweets(tweet_ids):

    jobs_lst = []
    len_tweet_ids = len(tweet_ids)
    for i in range(len_tweet_ids):
        
        t = tweet_ids[i]
        keywords = {'twt_id': t['tid'], 'user_agent': ''}
        jobs_lst.append({
            'func': rehydrate_tweet,
            'args': keywords,
            'misc': t['notes'],
            'print': '' if i % 10 else f'\trehydrate_tweet() {i} of {len_tweet_ids}'
        })

    
    res_lst = parallelTask(jobs_lst, threadCount=5)
    
    tweets = []
    for r in res_lst:
        r['output']['notes'] = r['misc']
        tweets.append(r['output'])

    return tweets

def write_tweets_to_jsonl_file(outfilename, tweets):

    try:
        with gzip.open(outfilename, 'wt') as outfile:
            for t in tweets:
                outfile.write( json.dumps(t, ensure_ascii=False) + '\n' )
    except:
        genericErrorInfo()

    print(f'\nWrote: {outfilename}')

def read_tweets_frm_jsonl_file(infilename):

    try:
        with gzip.open(infilename, 'rb') as infile:
            
            counter = 1
            for tweet in infile:
                tweet = json.loads(tweet.decode())
                
                print(f'reading tweets: {counter}')
                counter += 1
    except:
        genericErrorInfo()


def dumpJsonToFile(outfilename, dictToWrite, indentFlag=False, extraParams=None):

    if( extraParams is None ):
        extraParams = {}

    extraParams.setdefault('verbose', True)

    try:
        outfile = open(outfilename, 'w')
        
        if( indentFlag is True ):
            json.dump(dictToWrite, outfile, ensure_ascii=False, indent=4)#by default, ensure_ascii=True, and this will cause  all non-ASCII characters in the output are escaped with \uXXXX sequences, and the result is a str instance consisting of ASCII characters only. Since in python 3 all strings are unicode by default, forcing ascii is unecessary
        else:
            json.dump(dictToWrite, outfile, ensure_ascii=False)

        outfile.close()

        if( extraParams['verbose'] ):
            print('\twriteTextToFile(), wrote:', outfilename)
    except:
        if( extraParams['verbose'] ):
            print('\terror: outfilename:', outfilename)
        genericErrorInfo()
