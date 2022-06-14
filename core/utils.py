import queue
import threading
import cv2
import re

faceCascades = cv2.CascadeClassifier("core/haarcascade_frontalface_default.xml")

def has_face(imgPath):
    try:
        image = cv2.imread(imgPath)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        faces = faceCascades.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(30, 30),
        )
        if len(faces) > 0:
            return True
    
    except Exception:
        pass
    
    return False


class Context(object):
    regexes = {
        "mixed": {
            # "url_raw": re.compile(r"\S*https?:\/\/\S*", re.I | re.M),
            "url_onion": re.compile(r"\S*\.onion\S*", re.I | re.M),
            "ipv4": re.compile(r"\S*(?:[0-9]{1,3}\.){3}[0-9]{1,3}\S*", re.I | re.M),
            "username": re.compile(r"\S*@[a-zA-Z0-9]+\S*", re.I | re.M),
        },
        "social": {
            "angellist_company": re.compile(r"(?:https?:)?\/\/angel\.co\/company\/(?P<company>[A-z0-9_-]+)(?:\/(?P<company_subpage>[A-z0-9-]+))?", re.M | re.I),
            "angellist_job": re.compile(r"(?:https?:)?\/\/angel\.co\/company\/(?P<company>[A-z0-9_-]+)\/jobs\/(?P<job_permalink>(?P<job_id>[0-9]+)-(?P<job_slug>[A-z0-9-]+))", re.M | re.I),
            "angellist_user": re.compile(r"(?:https?:)?\/\/angel\.co\/(?P<type>u|p)\/(?P<user>[A-z0-9_-]+)", re.M | re.I),
            "crunchbase_company": re.compile(r"(?:https?:)?\/\/crunchbase\.com\/organization\/(?P<organization>[A-z0-9_-]+)", re.M | re.I),
            "crunchbase_person": re.compile(r"(?:https?:)?\/\/crunchbase\.com\/person\/(?P<person>[A-z0-9_-]+)", re.M | re.I),
            "crunchbase_email": re.compile(r"(?:mailto:)?(?P<email>[A-z0-9_.+-]+@[A-z0-9_.-]+\.[A-z]+)", re.M | re.I),
            "facebook_profile": re.compile(r"(?:https?:)?\/\/(?:www\.)?(?:facebook|fb)\.com\/(?P<profile>(?![A-z]+\.php)(?!marketplace|gaming|watch|me|messages|help|search|groups)[A-z0-9_\-\.]+)\/?", re.M | re.I),
            "facebook_profile_byid": re.compile(r"(?:https?:)?\/\/(?:www\.)facebook.com/(?:profile.php\?id=)?(?P<id>[0-9]+)", re.M | re.I),
            "github_repo": re.compile(r"(?:https?:)?\/\/(?:www\.)?github\.com\/(?P<login>[A-z0-9_-]+)\/(?P<repo>[A-z0-9_-]+)\/?", re.M | re.I),
            "github_user": re.compile(r"(?:https?:)?\/\/(?:www\.)?github\.com\/(?P<login>[A-z0-9_-]+)\/?", re.M | re.I),
            "googleplus_user": re.compile(r"(?:https?:)?\/\/plus\.google\.com\/(?P<id>[0-9]{21})", re.M | re.I),
            "googleplus_username": re.compile(r"(?:https?:)?\/\/plus\.google\.com\/\+(?P<username>[A-z0-9+]+)", re.M | re.I),
            "hackernews_item": re.compile(r"(?:https?:)?\/\/news\.ycombinator\.com\/item\?id=(?P<item>[0-9]+)", re.M | re.I),
            "hackernews_user": re.compile(r"(?:https?:)?\/\/news\.ycombinator\.com\/user\?id=(?P<user>[A-z0-9_-]+)", re.M | re.I),
            "instagram_profile": re.compile(r"(?:https?:)?\/\/(?:www\.)?(?:instagram\.com|instagr\.am)\/(?P<username>[A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)", re.M | re.I),
            "linkedin_company": re.compile(r"(?:https?:)?\/\/(?:[\w]+\.)?linkedin\.com\/(?P<company_type>(company)|(school))\/(?P<company_permalink>[A-z0-9-À-ÿ\.]+)\/?", re.M | re.I),
            "linkedin_post": re.compile(r"(?:https?:)?\/\/(?:[\w]+\.)?linkedin\.com\/feed\/update\/urn:li:activity:(?P<activity_id>[0-9]+)\/?", re.M | re.I),
            "linkedin_profile": re.compile(r"(?:https?:)?\/\/(?:[\w]+\.)?linkedin\.com\/in\/(?P<permalink>[\w\-\_À-ÿ%]+)\/?", re.M | re.I),
            "linkedin_profilepub": re.compile(r"(?:https?:)?\/\/(?:[\w]+\.)?linkedin\.com\/pub\/(?P<permalink_pub>[A-z0-9_-]+)(?:\/[A-z0-9]+){3}\/?", re.M | re.I),
            "medium_post_v1": re.compile(r"(?:https?:)?\/\/medium\.com\/(?:(?:@(?P<username>[A-z0-9]+))|(?P<publication>[a-z-]+))\/(?P<slug>[a-z0-9\-]+)-(?P<post_id>[A-z0-9]+)(?:\?.*)?", re.M | re.I),
            "medium_post_v2": re.compile(r"(?:https?:)?\/\/(?P<publication>(?!www)[a-z-]+)\.medium\.com\/(?P<slug>[a-z0-9\-]+)-(?P<post_id>[A-z0-9]+)(?:\?.*)?", re.M | re.I),
            "medium_user": re.compile(r"(?:https?:)?\/\/medium\.com\/@(?P<username>[A-z0-9]+)(?:\?.*)?", re.M | re.I),
            "medium_user_byid": re.compile(r"(?:https?:)?\/\/medium\.com\/u\/(?P<user_id>[A-z0-9]+)(?:\?.*)", re.M | re.I),
            "phone_number": re.compile(r"(?:tel|phone|mobile):(?P<number>\+?[0-9. -]+)", re.M | re.I),
            "reddit_user": re.compile(r"(?:https?:)?\/\/(?:[a-z]+\.)?reddit\.com\/(?:u(?:ser)?)\/(?P<username>[A-z0-9\-\_]*)\/?", re.M | re.I),
            "skype_profile": re.compile(r"(?:(?:callto|skype):)(?P<username>[a-z][a-z0-9\.,\-_]{5,31})(?:\?(?:add|call|chat|sendfile|userinfo))?", re.M | re.I),
            "snapshat_profile": re.compile(r"(?:https?:)?\/\/(?:www\.)?snapchat\.com\/add\/(?P<username>[A-z0-9\.\_\-]+)\/?", re.M | re.I),
            "stackexchange_user": re.compile(r"(?:https?:)?\/\/(?:www\.)?stackexchange\.com\/users\/(?P<id>[0-9]+)\/(?P<username>[A-z0-9-_.]+)\/?", re.M | re.I),
            "stackexchange_network_user": re.compile(r"(?:https?:)?\/\/(?:(?P<community>[a-z]+(?!www))\.)?stackexchange\.com\/users\/(?P<id>[0-9]+)\/(?P<username>[A-z0-9-_.]+)\/?", re.M | re.I),
            "stackoverflow_question": re.compile(r"(?:https?:)?\/\/(?:www\.)?stackoverflow\.com\/questions\/(?P<id>[0-9]+)\/(?P<title>[A-z0-9-_.]+)\/?", re.M | re.I),
            "stackoverflow_user": re.compile(r"(?:https?:)?\/\/(?:www\.)?stackoverflow\.com\/users\/(?P<id>[0-9]+)\/(?P<username>[A-z0-9-_.]+)\/?", re.M | re.I),
            "telegram_profile": re.compile(r"(?:https?:)?\/\/(?:t(?:elegram)?\.me|telegram\.org)\/(?P<username>[a-z0-9\_]{5,32})\/?", re.M | re.I),
            "twitter_status": re.compile(r"(?:https?:)?\/\/(?:[A-z]+\.)?twitter\.com\/@?(?P<username>[A-z0-9_]+)\/status\/(?P<tweet_id>[0-9]+)\/?", re.M | re.I),
            "twitter_user": re.compile(r"(?:https?:)?\/\/(?:[A-z]+\.)?twitter\.com\/@?(?!home|share|privacy|tos)(?P<username>[A-z0-9_]+)\/?", re.M | re.I),
            "vimeo_user": re.compile(r"(?:https?:)?\/\/vimeo\.com\/user(?P<id>[0-9]+)", re.M | re.I),
            "vimeo_video": re.compile(r"(?:https?:)?\/\/(?:(?:www)?vimeo\.com|player.vimeo.com\/video)\/(?P<id>[0-9]+)", re.M | re.I),
            "xing_profile": re.compile(r"(?:https?:)?\/\/(?:www\.)?xing.com\/profile\/(?P<slug>[A-z0-9-\_]+)", re.M | re.I),
            "youtube_channel": re.compile(r"(?:https?:)?\/\/(?:[A-z]+\.)?youtube.com\/channel\/(?P<id>[A-z0-9-\_]+)\/?", re.M | re.I),
            "youtube_user": re.compile(r"(?:https?:)?\/\/(?:[A-z]+\.)?youtube.com\/user\/(?P<username>[A-z0-9]+)\/?", re.M | re.I),
            "youtube_video": re.compile(r"(?:https?:)?\/\/(?:(?:www\.)?youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)(?P<id>[A-z0-9\-\_]+)", re.M | re.I),
        },
        "downloads": {
            "mega_nz": re.compile(r"\S*mega\.nz\S*", re.I | re.M),
            "google_drive": re.compile(r"\S*drive\.google\S*", re.I | re.M),
            "torrent": re.compile(r"\S*\.torrent\S*", re.I | re.M),
            "sendspace": re.compile(r"\S*\sendspace\S*", re.I | re.M),
            "drive_protonmail": re.compile(r"\S*drive\.protonmail\S*", re.I | re.M),
            "ufile": re.compile(r"\S*ufile\S*", re.I | re.M),
            "mediafire": re.compile(r"\S*mediafire\S*", re.I | re.M),
            "4shared": re.compile(r"\S*4shared\S*", re.I | re.M),
            "anonfile": re.compile(r"\S*anonfile\S*", re.I | re.M),
            "anonymfiles": re.compile(r"\S*anonymfiles\S*", re.I | re.M),
            "gofile": re.compile(r"\S*gofile\S*", re.I | re.M),
            "sql_gg": re.compile(r"\S*sql\.gg\S*", re.I | re.M),
            "fayloobmennik_cloud": re.compile(r"\S*fayloobmennik\.cloud\S*", re.I | re.M),
            "zeroBin_net": re.compile(r"\S*zeroBin\.net\S*", re.I | re.M),
            "0bin": re.compile(r"\S*0bin\S*", re.I | re.M),
            "gplinks": re.compile(r"\S*gplinks\S*", re.I | re.M),
            "disk_yandex_ru": re.compile(r"\S*disk\.yandex\.ru\S*", re.I | re.M),
            "dropmefiles": re.compile(r"\S*dropmefiles\S*", re.I | re.M),
            "goload": re.compile(r"\S*goload\S*", re.I | re.M),
            "klgrth": re.compile(r"\S*pst\.klgrth\.io/\S*", re.I | re.M),
        },
        "pastes": {
            "ghostbin": re.compile(r"\S*ghostbin\S*", re.I | re.M),
            "pastebin": re.compile(r"\S*pastebin\S*", re.I | re.M),
            "pastes": re.compile(r"\S*pastes\S*", re.I | re.M),
            "slexypaste": re.compile(r"\S*slexypaste\S*", re.I | re.M),
        }
    }

    @classmethod
    def find(cls, text):
        matchs = []
        for typ in cls.regexes:
            for key, value in cls.regexes[typ].items():
                match = value.findall(text)
                if match:
                    matchs.append({key: match})

        return matchs


class Worker(threading.Thread):

    def __init__(self):
        super().__init__()

        self.daemon = True
        self.running = False
        self._stop_event = threading.Event()
        self._worker_queue = None

    def run(self):

        while not self.stopped():

            if not self._worker_queue.empty():
                self.running = True

                func, args, kwargs = self._worker_queue.get()

                if (args or kwargs):
                    func(*args, **kwargs)

                else:
                    func()

                self.running = False
                self._worker_queue.task_done()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def receive_signal(self, *args, **kwargs):
        exit(1)


class ThreadsManager(object):

    def __init__(self, max_threads=10) -> None:
        super().__init__()
        self._lock_of_locks = threading.RLock()
        
        self._workers = []
        self._rlocks = dict()
        self._locks = dict()
        self._max_workers = max_threads
        self._worker_queue = queue.Queue()

    def new(self, func, *args, **kwargs) -> None:
        self._create_new_worker()

        while (self._worker_queue.qsize() > self._max_workers):
            pass

        self._worker_queue.put((func, args, kwargs,),)

    def Rlock(self, name) -> threading.RLock:
        with self._lock_of_locks:
            if not name in self._rlocks:
                self._rlocks[name] = threading.RLock()
            return self._rlocks[name]

    def lock(self, name) -> threading.Lock:
        with self._lock_of_locks:
            if not name in self._locks:
                self._locks[name] = threading.Lock()
            return self._locks[name]
    
    def join(self):
        while not self._worker_queue.empty():
            pass

        for worker in self._workers:
            if not worker.running:
                worker.stop()
                worker.join()

        self._worker_queue.join()

    def kill(self):
        for worker in self._workers:
            worker.stop()

    def _create_new_worker(self):
        if len(self._workers) < self._max_workers:
            worker = Worker()
            worker._worker_queue = self._worker_queue
            worker.start()
            self._workers.append(worker)

