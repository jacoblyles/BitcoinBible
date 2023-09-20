#!/usr/bin/env python3

import os 
import sys
import csv
import tweepy

import random


VERSES = 31102
NONCE = 9187
URL_LENGTH = 23
HASH_LENGTH = 64
CHAR_LIMIT = 280

BOOK_IDX = 1
CHAPTER_IDX = 2
VERSE_IDX = 3
TEXT_IDX = 4

ABBRS = None


def hex_to_verse(hexstring):
    return (int(hexstring, 16) + NONCE) % VERSES


def load_bible():
    filenym = outfile = os.path.join(get_script_path(), "data/csv/t_kjv.csv")
    with open(filenym) as f:
        reader = csv.reader(f)
        data = list(reader)
        data.pop(0) #headers
        data.pop(30673) #blank verse
    return data


def load_abbr():
    global ABBRS
    if ABBRS:
        return ABBRS
    else:
        filenym = outfile = os.path.join(get_script_path(), "data/csv/key_english.csv")
        with open(filenym) as f:
            reader = csv.reader(f)
            ABBRS = list(reader)
        return ABBRS


def book_name_to_num(name):
    abbr = load_abbr()
    book = filter(lambda t: t[1] == name, abbr)
    return list(book)[0][0]


def book_num_to_name(num):
    abbr = load_abbr()
    book = filter(lambda t: t[0] == num, abbr)
    return list(book)[0][1]


def pp_verse(verse_list):
    book_num = verse_list[BOOK_IDX]
    name = book_num_to_name(book_num)
    book_str = '{book} {chapter}:{verse}'.format(book=name, chapter=verse_list[2], verse=verse_list[3])
    return (book_str, verse_list[4])


def print_to_file(block, verseStr):
    outfile = os.path.join(get_script_path(), "output/output.txt")
    f = open(outfile, "a")
    f.write(block)
    f.write(" ")
    f.write(verseStr)
    f.write("\n")
    f.close()


def format_book(book_str: str):
    print(book_str)
    return "-".join(book_str.split())


def prepare_tweet(block_hash, book, chapter, verse, text):
    # Not using URLS for now
    #url = 'https://www.kingjamesbibleonline.org/{}-{}-{}/'.format(format_book(book), chapter, verse)
    LNBREAK_LEN = 4
    HEADER_LEN = 6
    
    index_str = '{} {}:{}'.format(book, chapter, verse)
    out_text = ""
    if HASH_LENGTH + LNBREAK_LEN + HEADER_LEN + len(index_str) + len(text) > 280:
        text_len = CHAR_LIMIT - HASH_LENGTH - HEADER_LEN - LNBREAK_LEN - 3 - len(index_str)
        truncate_text = text[0:text_len] + "..."
        out_text = '{}\n\n{}\n\n{}'.format(block_hash, index_str, truncate_text)
    else:
        out_text = '{}\n\n{}\n\n{}'.format(block_hash, index_str, text)
    return out_text


def print_to_twitter(text):

    # Authenticate to Twitter
    auth = tweepy.OAuthHandler("CONSUMER_KEY", "CONSUMER_SECRET")
    auth.set_access_token("ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")

    # Create API object
    api = tweepy.API(auth)

    # Create a tweet
    api.update_status(text)


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def verse_name_to_index(name):
    
    def verse_to_index_tuple(verse_str):
        book = " ".join(verse_str.split()[:-1])
        chapter = verse_str.split()[-1:][0].split(":")[0]
        verse = verse_str.split()[-1:][0].split(":")[1]
        book_num = book_name_to_num(book)
        return (book_num, chapter, verse)

    def index_tuple_to_verse_number(tupl):
        bible = load_bible()
        verse = [i for i, v in enumerate(bible) if v[1] == tupl[0] and v[2] == tupl[1] and v[3] == tupl[2]]
        return verse[0]

    tupl = verse_to_index_tuple(name)
    return index_tuple_to_verse_number(tupl)


def find_nonce():
    for i in range(100000000000):        
        genesis_index = (int("000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f", 16) + i) % VERSES
        if genesis_index == 0:
            print(i)
            break


if __name__ == "__main__":
    bible = load_bible()
    block = sys.argv[1]
    verse_num = hex_to_verse(block)
    verse = bible[verse_num]

    tweet = prepare_tweet(block, book_num_to_name(verse[BOOK_IDX]), verse[CHAPTER_IDX], verse[VERSE_IDX], verse[TEXT_IDX])
    print(tweet)
    print(len(tweet))

    # pverse = pp_verse(verse)
    # print(pverse)
    # print_to_file(str(pverse))
    print_to_twitter(tweet)
    

