import hashlib
import os
import downloader


def getMd5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def removeFile(file):
    os.remove(file)


def download(url, file_name):
    path = os.path.join(os.getcwd(), 'tmp', file_name)
    download = downloader.Download(url, path)
    download.download()
    return path
