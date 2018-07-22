import json
import tweepy
import re
import pandas as pd
import arcpy
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection

gis = GIS(arcpy.GetParameterAsText(1), arcpy.GetParameterAsText(2), arcpy.GetParameterAsText(3))

hashtag = arcpy.GetParameterAsText(0)
twitterHashtag = "#" + hashtag
dictionaryName = hashtag + "_dictionary"

dictionary_available = gis.content.is_service_name_available(service_name= dictionaryName, service_type = 'featureService')
print("...signed in to gis")

# authenticate twitter api
auth = tweepy.OAuthHandler("Consumer Key", "Consumer Secret")
auth.set_access_token("Access Token", "Access Token Secret")
api = tweepy.API(auth)
print("...authenticated to twitter")

col_names = ['word', "count"]
dictionary  = pd.DataFrame(columns = col_names)
## get tweets and build dictionary
for tweet in tweepy.Cursor(api.search, q=twitterHashtag, rpp=100).items(100):
    tweetText = tweet.text
    tweetText = re.sub('RT.*?:', '', tweetText)
    tweetText = re.sub('http.*', '', tweetText)
    words = tweetText.split(" ")
    
    for word in words:
        word = word.strip()
        if not word:
            continue
        if (dictionary['word'] == word).any():
            indexToUpdate = dictionary[(dictionary['word'] == word)].index.tolist()[0]
            oldValue = dictionary.iloc[indexToUpdate]['count']
            dictionary.iloc[indexToUpdate]['count'] = oldValue + 1
        else:
            dictionary.loc[len(dictionary)] = [word, 1]
print("...created dictionary")

csv_path = dictionaryName + ".csv"
dictionary = dictionary.sort_values(by=['count'], ascending=False)
dictionary.to_csv(csv_path)
print("...dictionary writter to csv")

print(dictionary)
csv_properties={'title': dictionaryName,
                'description':'Dictionary for twitter hashtag',
                'tags':'twitter'}
csv_item = gis.content.add(item_properties=csv_properties, data=csv_path)









