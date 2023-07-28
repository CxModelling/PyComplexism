import json

__author__ = 'TimeWz667'
__all__ = ['load_txt', 'save_txt', 'load_json', 'save_json']


def load_txt(path):
    """
    Load txt file given path
    :param path: path of a txt file
    :return: string of the txt file
    """
    with open(path, 'r') as f:
        return str(f.read())


def save_txt(txt, path):
    """
    Write txt file to given path
    :param txt: text to be writen
    :param path: path of a txt file
    :return: string of the txt file
    """
    with open(path, 'w') as f:
        f.write(txt)


def load_json(path):
    """
    Load json file given path
    :param path: path of a json file
    :return: json of the json file
    """
    with open(path, 'r') as f:
        return json.load(f)


def save_json(js, path):
    """
    Save a dictionary into a json file
    :param js: json-formatted object
    :param path: file path
    """
    with open(path, 'w') as f:
        json.dump(js, f)