from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
# client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.reila

from datetime import datetime


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/getDiary', methods=['GET'])
def getDiary():
    return render_template('diary_index.html')


@app.route('/getMovie', methods=['GET'])
def getMovie():
    return render_template('movie_index.html')


@app.route('/diary', methods=['GET'])
def show_diary():
    diaries = list(db.diary.find({}, {'_id': False}))
    return jsonify({'all_diary': diaries})


@app.route('/diary', methods=['POST'])
def save_diary():
    date_receive = request.form['date_give']
    desc_receive = request.form['desc_give']

    file = request.files["file_give"]

    extension = file.filename.split('.')[-1]

    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    filename = f'file created: {mytime}'

    save_to = f'static/{filename}.{extension}'
    file.save(save_to)

    doc = {
        'date': date_receive,
        'desc': desc_receive,
        'file': f'{filename}.{extension}',
        'uploaded': today.strftime('%Y.%m.%d')
    }

    db.diary.insert_one(doc)
    return jsonify({'msg': 'saved'})


@app.route('/memo', methods=['GET'])
def movie_listing():
    movies = list(db.movies.find({}, {'_id': False}))
    return jsonify({'all_movies': movies})


@app.route('/memo', methods=['POST'])
def movie_saving():
    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    title = soup.select_one('meta[property="og:title"]')['content']
    image = soup.select_one('meta[property="og:image"]')['content']
    desc = soup.select_one('meta[property="og:description"]')['content']

    doc = {
        'title': title,
        'image': image,
        'desc': desc,
        'url': url_receive,
        'comment': comment_receive
    }

    db.movies.insert_one(doc)

    return jsonify({'msg': 'Saved!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
