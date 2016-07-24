#!/usr/bin/python3

import astral
import configparser
import os
import pymysql
import pystache
import time

DEBUG=False

os.environ['TZ'] = "Europe/London"
time.tzset()

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

def populate_last_image(informations):
    db = connect_database()

    cursor = db.cursor()

    cursor.execute("select link, latitude, longitude, created_time, file_path, text from instagram_photos order by created_time desc limit 1")
    result = cursor.fetchall()[0]

    informations['last_photo_path'] = result[4]
    informations['last_latitude'] = result[1]
    informations['last_longitude'] = result[2]
    informations['last_text'] = result[5]
    informations['picture_date'] = result[3]

def generate_informations():
    informations = {}
    populate_last_image(informations)

    informations['google_maps_key'] = read_config().get("General", "GoogleMapKey")

    return informations

def generate_output(info):
    template_file = open("index.tmpl", "r")
    output = pystache.render(template_file.read(), informations)

    config = read_config()
    directory = config.get("Directories", "output") + "/"

    output_file = open(directory + "index.html", "w")
    output_file.write(output)
    output_file.close()

if __name__ == "__main__":
    informations = generate_informations()
    generate_output(informations)
