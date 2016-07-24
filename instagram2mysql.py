#!/usr/bin/python3

import configparser
import datetime
import os
import pymysql
import requests
import urllib.request

def read_config():
    config = configparser.ConfigParser()
    config.readfp(open("/etc/travel-tracker.ini"))
    return config

def connect_database():
    config = read_config()

    db = pymysql.connect(config.get("Mysql", "host"),
                         config.get("Mysql", "user"),
                         config.get("Mysql", "password"),
                         config.get("Mysql", "database"))
    return db

def instagram_request(url):
    url += "?access_token="+access_token()
    return requests.get(url).json()

def access_token():
    access_token = read_config().get("General", "InstagramAccessToken")
    return access_token

def add_leading_zeros(number):
    return "{0:02d}".format(number)

def download_photo(url, created_time):
    dt = datetime.datetime.fromtimestamp(created_time)
    year = add_leading_zeros(dt.year)
    month = add_leading_zeros(dt.month)
    day = add_leading_zeros(dt.day)
    hour = add_leading_zeros(dt.hour)
    minute = add_leading_zeros(dt.minute)
    second = add_leading_zeros(dt.second)

    file_name = "IMG_{}{}{}_{}{}{}.jpg".format(year,month,day,hour,minute,second)

    config = read_config()
    images_directory = config.get("Directories", "output") + "/images/"

    if not os.path.exists(images_directory):
        os.makedirs(images_directory)

    file_path = images_directory + file_name
    print("download_photo:",url,file_path)
    downloader = urllib.request.urlretrieve(url, file_path)
    return file_path

def insert_data(instagram_id, link, file_path, text, latitude, longitude, created_time):
    db = connect_database()

    db.cursor().execute("insert into instagram_photos (instagram_id, link, file_path, text, latitude, longitude, created_time) values (%s, %s, %s, %s, %s, %s, from_unixtime(%s))", (instagram_id, link, file_path, text, latitude, longitude, created_time))

    db.commit()

def instagram_id_exists(instagram_id):
    db = connect_database()
    cursor = db.cursor()

    cursor.execute("select count(*) from instagram_photos where instagram_id=%s",(instagram_id))

    result = cursor.fetchall()[0][0]

    return result>0

def import_photos():
    json = instagram_request("https://api.instagram.com/v1/users/self/media/recent/")
    for photo in json['data']:
        if photo['location'] is not None:
            latitude = photo['location']['latitude']
            longitude = photo['location']['longitude']

        else:
            latitude = None
            longitude = None

        created_time = photo['created_time']
        link = photo['link']
        image_url = photo['images']['standard_resolution']['url']

        if photo['caption'] is not None:
            text = photo['caption']['text']
        else:
            text = None

        instagram_id = photo['id']
        created_time = photo['created_time']

        print("latitude:",latitude)
        print("longitude:",longitude)
        print("created_time:",created_time)
        print("link:",link)
        print("image_url:",image_url)
        print("text:",text)
        print("instagram_id:",instagram_id)

        inserted = instagram_id_exists(instagram_id)

        if not inserted:
            file_path = download_photo(image_url, int(created_time))
            insert_data(instagram_id, link, file_path, text, latitude, longitude, created_time)

if __name__ == "__main__":
    import_photos()
