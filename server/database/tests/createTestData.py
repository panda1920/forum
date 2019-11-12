import json
from pathlib import Path
from time import time

FILENAME = Path(__file__).resolve().parents[0] / 'testdata.json'
USERS = [
    'Anonymous',
    'Bobby',
    'Charlie',
    'Daniel',
    'Eugene',
    'Frederick',
    'Geralt',
    'Henry',
    'Ian',
    'Johnson',
]
EMAIL_DOMAIN = '@myforumwebapp.com'
POSTCOUNT_PER_USER = 5

def createUsers():
    users = []
    now = time()
    for idx, username in enumerate(USERS):
        users.append({
            'userId': str(idx),
            'displayName': username,
            'userName': username.lower() + EMAIL_DOMAIN,
            'createdAt': now
        })
    

    return users

def createPosts(users):
    posts = []
    now = time()

    for userCount, user in enumerate(users):
        for n in range(POSTCOUNT_PER_USER):
            posts.append({
                'postId': str(userCount * POSTCOUNT_PER_USER + n),
                'userId': user['userId'],
                'post': f'{user["displayName"]}\'s post {n}',
                'createdAt': now
            })

    return posts

FILENAME.unlink()
FILENAME.touch()

users = createUsers()
posts = createPosts(users)

with FILENAME.open('w', encoding='utf-8') as f:
    json.dump({
        'users': users,
        'posts': posts
    }, f)