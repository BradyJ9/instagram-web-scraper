from os import write
from time import sleep
from datetime import datetime
from selenium import webdriver
from random import randrange
import sys
import _thread
import pymongo

###UNFINISHED###

GAA_USERNAME = ""
GAA_PASSWORD = ""
USER_HANDLE_TO_INSPECT = ""

DATABASE_NAME = ""
COLLECTION_NAME = ""

def init_mongo_client():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")

def run_stats(db_client):
    db_client[COLLECTION_NAME][DATABASE_NAME]

def main():
    mongo_client = init_mongo_client()

    run_stats(mongo_client)

main()