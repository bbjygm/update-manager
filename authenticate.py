# https://www.vitoshacademy.com/hashing-passwords-in-python/

import hashlib
import binascii
import os
import json

users_path = 'users.json'


def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt,
                                  1000000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def store_account(form):
    users = {}
    with open(users_path, 'r+') as file:
        users = json.loads(file.read())

    error = reject_create(form, users)
    if error:
        return error

    users[form['username']] = {
        'username': form['username'],
        'hash': hash_password(form['password']),
        'email': form['email'],
        'player_url': form['player'],
        'updates_url': form['updates']
    }

    with open(users_path, 'w+') as file:
        file.write(json.dumps(users))

    return False


def get_hash(username):
    users = {}
    with open(users_path, 'r+') as file:
        users = json.loads(file.read())

    if username in users and 'hash' in users[username]:
        return users[username]['hash']
    else:
        return False


def verify_password(provided_password, stored_password):
    # Verify a stored password against one provided by user
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'),
                                  salt.encode('ascii'), 1000000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


def false_verify():
    # Should take about the same time as verify_password, used to equalize login and failed login times
    binascii.hexlify(
        hashlib.pbkdf2_hmac('sha512', 'incorrect password'.encode('utf-8'),
                            'sodium chloride'.encode('ascii'),
                            1000000)).decode('ascii')
    return False


def verify_login(username, password):
    stored_password = get_hash(username)
    if stored_password:
        return verify_password(password, stored_password)
    else:
        return false_verify()


def reject_create(form, users):
    if form['username'] in users:
        return 'Username already exists'

    if form['password'] != form['confirm']:
        return 'Password confirmation does not match'

    return False
