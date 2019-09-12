import urllib.request
import time, csv, sys, boto3, uuid, hashlib
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

dynamodb = boto3.client('dynamodb')

def put_to_dynamodb(args):
    """given the list of string arguments, put one item to dynamodb table"""
    dynamodb.put_item( \
    TableName='whats_new_routes', \
    Item={'uuid':{'S':args[0]}, 'name':{'S':args[1]},'grade':{'S':args[2]}, 'stars':{'S':args[3]}, 'ts':{'S':args[4]}, 'ttl':{'N':args[5]} })

def generate_uuid(args):
    """given a list of strings, return an md5 hash. This will be the primary key in dynamodb table"""
    uuid = ""
    for arg in args:
        uuid += "".join(arg.lower().split())
    return hashlib.md5(uuid.encode()).hexdigest()

def to_minutes(num, unit):
    """given a number and time unit, return time in minutes (int)"""
    if unit == 'hours' or unit == 'hour':
        return num*60
    elif unit == 'mins' or unit == 'min' or unit == 'minute':
        return num
    elif unit == 'days' or unit == 'day':
        return num*1440
    else:
        sys.exit("unexpected error in to_minutes: num=" +str(num)+ " unit="+unit)

response = urllib.request.urlopen('https://www.mountainproject.com/whats-new?type=routes&locationId=0&days=1')
soup = BeautifulSoup(response, features="html.parser")
rows = soup.findAll("tr", {"class": "route-row"})

names = []

# our class selector gives us duplicates
# so we must skip those with continue, also skip if they have an empty time
for route in rows:

    # get time of route creation
    time_ago          = route.findAll("span", {"class":"text-nowrap"})
    if len(time_ago) != 0:
        time_ago = time_ago[1].get_text().strip()
        if time_ago.split()[0] != "moments":
            minutes_ago = to_minutes(int(time_ago.split()[0]), time_ago.split()[1])
        else:
            # case when "moments ago"
            minutes_ago   = 1
    else:
        continue

    #
    # get route name
    #
    route_name        = route.strong.string
    if route_name not in names:
        names.append(route_name)
    else:
        continue
    
    #
    # get grade of route and number of stars
    #
    grade = route.findAll('span', {"class": "rateYDS"})[0].string
    stars = str(len( route.findAll("span", {"class":"scoreStars"})[0].findAll("img") ))
  
    #
    # create a timestamp by subtracting "created time ago" from today() 
    #
    created_timestamp = str(int((datetime.today() - timedelta(minutes=minutes_ago)).timestamp()))
 
    #
    # dynamodb time-to-live, set timestamp when record will expire
    #
    ttl = str( int((datetime.today() + timedelta(days=2)).timestamp()) ) 
   
    print (route_name, grade, stars, created_timestamp) 
    
    parsed_row = [route_name, grade, stars, created_timestamp, ttl]
    primary_key = generate_uuid(parsed_row[:-2])

    put_to_dynamodb( [primary_key] + parsed_row )

