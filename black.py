import argparse
import hashlib
import json
import os
import shutil
import webbrowser
from datetime import datetime
from io import StringIO
from pathlib import Path
from urllib.parse import urljoin, urlparse

import html2text
import requests
from flask import Flask, render_template
from flask_socketio import SocketIO
from lxml import etree

from core.utils import Context, ThreadsManager, has_face



class DATA:
    datas = []
    faces = []
    images = []


def to_md5(string):
    return hashlib.md5(str(string).encode("utf-8")).hexdigest()


def dl(url, filename):
    try:

        if not Path(filename).exists():
            with requests.get(url, stream=True, timeout=5) as r:
                r.raise_for_status()

                with open(filename, "wb") as fp:
                    for chunk in r.iter_content(chunk_size=8192):
                        fp.write(chunk)

    except Exception:
        pass


def nu(urls, website, url, _path):
    n_url = urljoin(website, url)
    h = to_md5(n_url)
    path = urlparse(n_url).path
    ext = os.path.splitext(path)[1]

    with TM.Rlock("add"):
        if n_url not in urls.values():
            if "jpg" in n_url or "jpeg" in n_url or "png" in n_url or not ext:
                DATA.images.append(
                    {"id": _path, "imgPath": f"{archive}/{h}{ext}"})

            urls[h] = n_url
            TM.new(dl, n_url, f"{archive}/{h}{ext}")

    return f"{h}{ext}"


def req(check, username):
    urls = dict()
    url = check["check_uri"].format(account=username)

    try:
        res = requests.get(url, timeout=5)
        text = html2text.HTML2Text().handle(res.text)

        found = True
        if str(res.status_code) != str(check.get("account_existence_code")):
            found = False

        if check.get("account_existence_string") not in res.text:
            found = False

        if found:
            filename = str(to_md5(url)) + ".html"
            _path = archive + "/" + filename

            if not Path(_path).exists():
                tree = etree.parse(StringIO(res.text), etree.HTMLParser())
                for node in tree.xpath("//*[@src]"):
                    node.set("src", nu(urls, url, node.get("src"), _path))

                for node in tree.xpath("//*[@srcset]"):
                    node.set("srcset", nu(urls, url, node.get(
                        "srcset").split(" ")[0], _path))

                for node in tree.xpath("//*[@href]"):
                    node.set("href", nu(urls, url, node.get("href"), _path))

                data = etree.tostring(tree, pretty_print=False, encoding="utf-8", method="html")  # noqa

                with open(_path, "wb") as fp:
                    fp.write(data)

            d = {
                "archive": {"id": _path, "url": url},
                "ana": {"id": _path, "url": url, "matchs": Context.find(text)},
            }

            with TM.Rlock("append"):
                print("[+]", url)
                DATA.datas.append(d)

    except Exception:
        pass


app = Flask(__name__)
io = SocketIO(app, async_mode="threading")


@app.route("/")
def home():
    return render_template("index.html")


@io.on("connect")
def connect(msg):
    jsonData = json.load(open("static/data.json"))
    io.emit("getQuery", jsonData, json=True)


TM = ThreadsManager(1000)

parser = argparse.ArgumentParser()
parser.add_argument("-u", dest="username", required=True, help="username of target")
parser.add_argument("-d", dest="datetime", help="select snapshot by datetime")
parser.add_argument("-l", dest="lst", action="store_true", help="list snapshots of target")
args = parser.parse_args()

username = args.username
today = args.datetime

userDB = json.loads(requests.get(
    "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/master/web_accounts_list.json").text)

if today:
    today = today.replace("/", "_")
else:
    today = datetime.now().strftime("%d_%m_%Y")

archive = f"static/archive/{username}/{today}"

if args.lst:
    try:
        for dt in Path(f"static/archive/{username}").glob("*"):
            print("-", dt.name)
    except Exception:
        print("[Err] User not found!")
else:
    if Path(archive).exists():
        shutil.copyfile(f"{archive}/data.json", "static/data.json")

    else:
        p = Path(archive)
        p.mkdir(parents=True, exist_ok=True)

        for check in userDB["sites"]:
            TM.new(req, check, username)

        TM.join()

        for imgObj in DATA.images:
            if has_face(imgObj["imgPath"]):
                DATA.faces.append(imgObj)

        with open(f"{archive}/data.json", "w") as fp:
            json.dump(
                {
                    "recon": DATA.datas,
                    "faces": DATA.faces
                }, fp
            )

        shutil.copyfile(f"{archive}/data.json", "static/data.json")

    
    # io.run(app, debug=True)
    webbrowser.open("http://localhost:5000")
    io.run(app)

