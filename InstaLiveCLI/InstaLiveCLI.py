import argparse
import hashlib
import hmac
import json
import os
import time
import urllib
import uuid
import tempfile
from PIL import Image

import requests

from .http import ClientCookieJar
from .util import to_json, from_json
import urllib.request as compat_urllib_request

# Turn off InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class InstaLiveCLI:
    previewWidth: int = 1080
    previewHeight: int = 1920
    broadcastMessage: str = ""
    sendNotification: bool = True
    share_to_story: bool = False
    last_comment_ts: int = 1
    is_running: bool = False
    username: str = None
    password: str = None
    username_id: str = None
    rank_token: str = None
    token: str = None
    uuid: str = None
    LastJson: dict = None
    LastResponse = None
    s = requests.Session()
    isLoggedIn: bool = False
    broadcast_id: int = None
    stream_key: str = None
    stream_server: str = None

    cookie_jar = None

    save_settings: bool = False

    is_cli = False

    two_factor_required = False
    two_factor_last_number = None
    two_factor_identifier = None
    last_csrf_token = None
    DEVICE_SETS = {
        "app_version": "136.0.0.34.124",
        "android_version": "28",
        "android_release": "9.0",
        "dpi": "640dpi",
        "resolution": "1440x2560",
        "manufacturer": "samsung",
        "device": "SM-G965F",
        "model": "star2qltecs",
        "cpu": "samsungexynos9810",
        "version_code": "208061712",
    }

    API_URL = 'https://i.instagram.com/api/v1/'

    USER_AGENT = 'Instagram {app_version} Android ({android_version}/{android_release}; {dpi}; {resolution}; ' \
                 '{manufacturer}; {model}; armani; {cpu}; en_US)'.format(**DEVICE_SETS)
    IG_SIG_KEY = '4f8732eb9ba7d1c8e8897a75d6474d4eb3f5279137431b2aafb71fafe2abe178'
    SIG_KEY_VERSION = '4'

    def __init__(self, username='', password='', settings='', auth='', saved=False):
        """Initiate InstaLiveCLI

        Args:
            username (str, optional): Username of your Instagram. Defaults to ''.
            password (str, optional): Password of your Instagram. Defaults to ''.
            settings (str, optional): filename of your settings. Defaults to ''.
            auth (dict, optional): loading dictionary of your settings. Defaults to ''.
        """
        if bool(username) == False and bool(password) == False and bool(auth) == False and bool(settings) == False:
            parser = argparse.ArgumentParser(add_help=True)
            parser.add_argument("-u", "--username", type=str, help="username", required=True)
            parser.add_argument("-p", "--password", type=str, help="password", required=True)
            parser.add_argument("-proxy", type=str, help="Proxy format - user:password@ip:port", default=None)
            parser.add_argument("-s", "--save", help="save settings to auth.json",action='store_true')
            
            args = parser.parse_args()

            username = args.username
            password = args.password

            self.is_cli = True
        else:
            self.is_cli = False

        if settings:
            self.import_settings(settings)
        

        if saved:
            self.save_settings = True

        m = hashlib.md5()
        m.update(username.encode('utf-8') + password.encode('utf-8'))
        self.device_id = self.generate_device_id(m.hexdigest())

        self.set_user(username=username, password=password)

        # Handle Cookies
        cookie_string = None
        cookie_jar = ClientCookieJar(cookie_string=cookie_string)
        self.cookie_jar = cookie_jar

        if auth:
            self.load_settings(auth)

    @property
    def settings(self):
        """Helper property that extracts the settings that you should cache
        in addition to username and password.

        Returns:
            dict: all the settings and cookies
        """

        # check logged in
        try:
            if self.two_factor_required != True:
                status = self.get_broadcast_status()
            else:
                status = None
        except:
            status = None

        return {
            'uuid': self.uuid,
            'username': self.username,
            'device_id': self.device_id,
            'cookie': self.cookie_jar.dump(self.s.cookies),
            'isLoggedIn': self.isLoggedIn, # !todo: check expiration date cookies
            'last_csrf_token': self.last_csrf_token,
            'data_stream': {
                'broadcast_id':self.broadcast_id,
                'stream_server': self.stream_server,
                'stream_key': self.stream_key,
                'status':  status
            },
            'two_step_verification': {
                "two_factor_required": self.two_factor_required,
                "two_factor_last_number": self.two_factor_last_number,
                "two_factor_identifier": self.two_factor_identifier
            },
            'created_ts': int(time.time())
        }
    
    def get_broadcast_status(self):
        """Returning current broadcast info status if exists

        Returns:
            str: broadcast status
        """
        if self.send_request("live/{}/info/".format(self.broadcast_id)):
            return self.LastJson['broadcast_status']
        return None
    
    def export_settings(self, filename):
        """Exporting all the settings to json file

        Args:
            filename (str): filename, for example: "settings.json"
        """
        with open(filename, 'w') as outfile:
            json.dump(self.settings, outfile, default=to_json)

    def import_settings(self, filename):
        """Import and load settings from json file

        Args:
            filename (str): filename, for example: "settings.json"

        Returns:
            dict: settings configuration
        """
        with open(filename) as file_data:
            cached_auth = json.load(file_data, object_hook=from_json)
        
        self.load_settings(cached_auth)
        return cached_auth

    def load_settings(self, cached_auth):
        """load all the settings from python dictionary

        Args:
            cached_auth (dict): settings configuration
        """
        
        
        self.load_cookies(cached_auth['cookie'])
        self.uuid = cached_auth['uuid']
        self.device_id = cached_auth['device_id']
        self.isLoggedIn = cached_auth['isLoggedIn']

        # streaming data
        self.broadcast_id = cached_auth['data_stream']['broadcast_id']
        self.stream_key = cached_auth['data_stream']['stream_key']
        self.stream_server = cached_auth['data_stream']['stream_server']
        
        self.two_factor_required = cached_auth['two_step_verification']['two_factor_required']
        self.two_factor_last_number = cached_auth['two_step_verification']['two_factor_last_number']
        self.two_factor_identifier = cached_auth['two_step_verification']['two_factor_identifier']

        self.last_csrf_token = cached_auth['last_csrf_token']
        self.username = cached_auth['username']
    def load_cookies(self, cookie_string):
        """Loads cookie from Cookiestring to Cookie jar and then import it to session's cookiejar

        Args:
            cookie_string (str): cookies string
        """
        cookie_jar = ClientCookieJar(cookie_string=cookie_string)
        self.s.cookies = cookie_jar._cookies

    def set_user(self, username, password):
        """Set user to class variable instance

        Args:
            username (str): Username of your Instagram
            password (str): Password of your Instagram
        """
        self.username = username
        self.password = password
        self.uuid = self.generate_UUID(True)

    def generate_UUID(self, t: bool = True, seed=None):
        """generating UUID

        Args:
            t (bool, optional): if you want return raw uuid. Defaults to True.
            seed (str, optional): seed string. Defaults to None.

        Returns:
            str: UUID1 string
        """
        if seed:
            m = hashlib.md5()
            m.update(seed.encode('utf-8'))
            new_uuid = uuid.UUID(m.hexdigest())

            return str(new_uuid)
        else:
            generated_uuid = str(uuid.uuid1()) # change from uuid 4 to 1 for better use cases
            if t:
                return generated_uuid
            else:
                return generated_uuid.replace('-', '')

    def generate_device_id(self, seed):
        """generate unique device id from seed

        Args:
            seed (str): seed string

        Returns:
            str: unique formatted device id
        """
        volatile_seed = "12345"
        m = hashlib.md5()
        m.update(seed.encode('utf-8') + volatile_seed.encode('utf-8'))
        return 'android-' + m.hexdigest()[:16]

    def set_code_challenge_required(self, path, code):
        """setting code challenge 

        Args:
            path (str): path api
            code (str): code challenge
        """
        data = {'security_code': code,
                '_uuid': self.uuid,
                'guid': self.uuid,
                'device_id': self.device_id,
                '_uid': self.username_id,
                '_csrftoken': self.LastResponse.cookies['csrftoken']}

        self.send_request(path, self.generate_signature(json.dumps(data)), True)

    def get_code_challenge_required(self, path, choice=0):
        """send code challenge choice
        choices: 0 - SMS, 1 - EMAIL
        Args:
            path (str): api path
            choice (int, optional): choice challenge . Defaults to 0.

        """
        data = {'choice': choice,
                '_uuid': self.uuid,
                'guid': self.uuid,
                'device_id': self.device_id,
                '_uid': self.username_id,
                '_csrftoken': self.LastResponse.cookies['csrftoken']}

        self.send_request(path, self.generate_signature(json.dumps(data)), True)

    def login(self, force=False):
        """Login to api

            becareful if you want to use force, it might rate limit, even worst banned you if you send too many times.

        Args:
            force (bool, optional): forcing to send login requests. Defaults to False.

        Returns:
            bool: if logged in
        """
        if not self.isLoggedIn or force:
            if self.send_request(endpoint='si/fetch_headers/?challenge_type=signup&guid=' + self.generate_UUID(False),
                                 login=True):

                data = {'phone_id': self.generate_UUID(True),
                        '_csrftoken': self.LastResponse.cookies['csrftoken'],
                        'username': self.username,
                        'guid': self.uuid,
                        'device_id': self.device_id,
                        'password': self.password,
                        'login_attempt_count': '0'}

                if self.send_request('accounts/login/', post=self.generate_signature(json.dumps(data)), login=True):
                    if "two_factor_required" not in self.LastJson:
                        self.isLoggedIn = True
                        self.username_id = self.LastJson["logged_in_user"]["pk"]
                        self.rank_token = "%s_%s" % (self.username_id, self.uuid)
                        self.token = self.LastResponse.cookies["csrftoken"]
                        return True
                    else:
                        if self.is_cli:
                            self.two_factor()
                            self.isLoggedIn = True
                            self.username_id = self.LastJson["logged_in_user"]["pk"]
                            self.rank_token = "%s_%s" % (self.username_id, self.uuid)
                            self.token = self.LastResponse.cookies["csrftoken"]
                            return True
                            
                        self.two_factor_required = True
                        self.two_factor_last_number = self.LastJson['two_factor_info']['obfuscated_phone_number']
                        self.two_factor_identifier = self.LastJson['two_factor_info']['two_factor_identifier']
                        self.last_csrf_token = self.LastResponse.cookies['csrftoken']
                        return False
        return False

    def two_factor(self, code=''):
        """sending verification if there's two factor neeeded

        Returns:
            bool: if two factor passed
        """
        # verification_method': 0 works for sms and TOTP. why? ¯\_ಠ_ಠ_/¯
        if code == '':
            verification_code = input('Enter verification code: ')
        else:
            verification_code = code

        data = {
            'verification_method': 0,
            'verification_code': verification_code,
            'trust_this_device': 0,
            'two_factor_identifier': self.two_factor_identifier,
            '_csrftoken': self.last_csrf_token,
            'username': self.username,
            'device_id': self.device_id,
            'guid': self.uuid,
        }

        if self.send_request('accounts/two_factor_login/', self.generate_signature(json.dumps(data)), login=True):
            return True
        else:
            return False

    def send_request(self, endpoint, post=None, login=False, headers: dict = {}):
        """Sending requests to instagram API

        Args:
            endpoint (str): API endpoint instagram
            post (dict, optional): data for post to api. Defaults to None.
            login (bool, optional): [description]. Defaults to False.

        Raises:
            Exception: Failing send requests

        Returns:
            bool: if requests is success
        """
        verify = False  # don't show request warning

        # if not self.isLoggedIn and not login:
        #     raise Exception("Not logged in!\n")

        if not len(headers) > 0:
            headers = {
                'Connection': 'close',
                'Accept': '*/*',
                'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Cookie2': '$Version=1',
                'Accept-Language': 'en-US',
                'User-Agent': self.USER_AGENT
            }

        self.s.headers.update(headers)

        while True:
            try:
                if post is not None:
                    self.LastResponse = self.s.post(self.API_URL + endpoint, data=post, verify=verify)
                else:
                    self.LastResponse = self.s.get(self.API_URL + endpoint, verify=verify)

                self.LastJson = json.loads(self.LastResponse.text)

                break
            except Exception as e:
                print('* Except on SendRequest (wait 60 sec and resend): {}'.format(str(e)))
                time.sleep(60)

        if self.LastResponse.status_code == 200:
            return True
        elif 'two_factor_required' in self.LastJson and self.LastResponse.status_code == 400:
            # even the status code isn't 200 return True if the 2FA is required
            if self.LastJson['two_factor_required']:
                print("Two factor required")
                return True
        elif 'message' in self.LastJson and self.LastResponse.status_code == 400:
            if self.LastJson['message'] == 'challenge_required':
                path = self.LastJson['challenge']['api_path'][1:]
                choice = int(input('Choose a challenge mode (0 - SMS, 1 - Email): '))
                self.get_code_challenge_required(path, choice)
                code = input('Enter the code: ')
                self.set_code_challenge_required(path, code)
        else:
            error_message = " - "
            if "message" in self.LastJson:
                error_message = self.LastJson['message']
            print('* ERROR({}): {}'.format(self.LastResponse.status_code, error_message))
            print(self.LastResponse)
            return False

    def set_proxy(self, proxy=None):
        """Set proxy to session

        Args:
            proxy (string, optional): user:password@ip:port. Defaults to None.
        """
        if proxy is not None:
            proxies = {'http': 'http://' + proxy, 'https': 'http://' + proxy}
            self.s.proxies.update(proxies)

    def generate_signature(self, data, skip_quote=False):

        if not skip_quote:
            try:
                parsed_data = urllib.parse.quote(data)
            except AttributeError:
                parsed_data = urllib.quote(data)
        else:
            parsed_data = data
        return 'ig_sig_key_version=' + self.SIG_KEY_VERSION + '&signed_body=' + hmac.new(
            self.IG_SIG_KEY.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest() + '.' + parsed_data

    def start(self):
        """Starting CLI APP
        """
        print("Let's do it!")
        if self.isLoggedIn or self.login():
            print("You'r logged in")
            
            if self.save_settings:
                self.export_settings('auth.json')                
                print('Settings exported to auth.json!')

            if self.create_broadcast():
                print("Broadcast ID: {}")
                print("* Broadcast ID: {}".format(self.broadcast_id))
                print("* Server URL: {}".format(self.stream_server))
                print("* Server Key: {}".format(self.stream_key))

                print("Press Enter after your setting your streaming software.")
                if self.start_broadcast():
                    self.is_running = True

                    while self.is_running:
                        cmd = input('command> ')

                        if cmd == "stop":
                            self.stop()

                        elif cmd == "mute comments":
                            self.mute_comments()

                        elif cmd == "unmute comments":
                            self.unmute_comment()

                        elif cmd == 'info':
                            self.live_info()

                        elif cmd == 'viewers':
                            users, ids = self.get_viewer_list()
                            print(users)

                        elif cmd == 'comments':
                            self.get_comments()

                        elif cmd[:4] == 'chat':
                            to_send = cmd[5:]
                            if to_send:
                                self.send_comment(to_send)
                            else:
                                print('usage: chat <text to chat>')

                        elif cmd == 'wave':
                            users, ids = self.get_viewer_list()
                            for i in range(len(users)):
                                print(f'{i + 1}. {users[i]}')
                            print('Type number according to user e.g 1.')
                            while True:
                                cmd = input('number> ')

                                if cmd == 'back':
                                    break
                                try:
                                    user_id = int(cmd) - 1
                                    self.wave(ids[user_id])
                                    break
                                except:
                                    print('Please type number e.g 1')

                        else:
                            print(
                                'Available commands:\n\t '
                                '"stop"\n\t '
                                '"mute comments"\n\t '
                                '"unmute comments"\n\t '
                                '"info"\n\t '
                                '"viewers"\n\t '
                                '"comments"\n\t '
                                '"chat"\n\t '
                                '"wave"\n\t')

    def get_viewer_list(self):
        """Get all of viewers from broadcast

        Returns:
            list: Returns two list user, and ids
        """
        if self.send_request("live/{}/get_viewer_list/".format(self.broadcast_id)):
            users = []
            ids = []
            for user in self.LastJson['users']:
                users.append(f"{user['username']}")
                ids.append(f"{user['pk']}")

            return users, ids

    def wave(self, user_id):
        """Waving to specific user_id

        Args:
            user_id (str): id of user you want to wave

        Returns:
            bool: if user waved
        """
        data = json.dumps(
            {'_uid': self.username_id, '_uuid': self.uuid, '_csrftoken': self.token, 'viewer_id': user_id})

        if self.send_request('live/{}/wave/'.format(self.broadcast_id), post=self.generate_signature(data)):
            return True
        return False

    def live_info(self):
        """Printing broadcast information to the console

            Broadcast ID, Server URL, Stream Key, Viewer Count, Status Broadcast.
        """
        if self.send_request("live/{}/info/".format(self.broadcast_id)):
            viewer_count = self.LastJson['viewer_count']

            print("[*]Broadcast ID: {}".format(self.broadcast_id))
            print("[*]Server URL: {}".format(self.stream_server))
            print("[*]Stream Key: {}".format(self.stream_key))
            print("[*]Viewer Count: {}".format(viewer_count))
            print("[*]Status: {}".format(self.LastJson['broadcast_status']))

    def mute_comments(self):
        """Mute current broadcast comments

        Returns:
            bool: if current comment muted
        """
        data = json.dumps({'_uuid': self.uuid, '_uid': self.username_id, '_csrftoken': self.token})
        if self.send_request(endpoint='live/{}/mute_comment/'.format(self.broadcast_id),
                             post=self.generate_signature(data)):
            print("Comments muted")
            return True

        return False

    def unmute_comment(self):
        """Unmute current broadcast comments

        Returns:
            bool: if current comment unmuted
        """
        data = json.dumps({'_uuid': self.uuid, '_uid': self.username_id, '_csrftoken': self.token})
        if self.send_request(endpoint='live/{}/unmute_comment/'.format(self.broadcast_id),
                             post=self.generate_signature(data)):
            print("Comments un-muted")
            return True

        return False

    def send_comment(self, msg):
        """Sending comment to broadcast

        Args:
            msg (str): message to send

        Returns:
            bool: if comment sent
        """
        data = json.dumps({
            'idempotence_token': self.generate_UUID(True),
            'comment_text': msg,
            'live_or_vod': 1,
            'offset_to_video_start': 0
        })

        if self.send_request("live/{}/comment/".format(self.broadcast_id), post=self.generate_signature(data)):
            if self.LastJson['status'] == 'ok':
                return True

    def create_broadcast(self):
        """Creating broadcast live

            broadcast_id, stream_server, stream_key will be saved on Class Variable.


        Returns:
            bool: if broadcast created
        """
        data = json.dumps({'_uuid': self.uuid,
                           '_uid': self.username_id,
                           'preview_height': self.previewHeight,
                           'preview_width': self.previewWidth,
                           'broadcast_message': self.broadcastMessage,
                           'broadcast_type': 'RTMP',
                           'internal_only': 0,
                           '_csrftoken': self.token})

        if self.send_request(endpoint='live/create/', post=self.generate_signature(data)):
            last_json = self.LastJson
            self.broadcast_id = last_json['broadcast_id']

            upload_url = last_json['upload_url'].split(str(self.broadcast_id))

            self.stream_server = upload_url[0]
            self.stream_key = "{}{}".format(str(self.broadcast_id), upload_url[1])

            return True

        else:

            return False

    def start_broadcast(self):
        """Starting current broadcast

        Returns:
            bool: If broadcast is started
        """
        data = json.dumps({'_uuid': self.uuid,
                           '_uid': self.username_id,
                           'should_send_notifications': 1,
                           '_csrftoken': self.token})

        if self.send_request(endpoint='live/' + str(self.broadcast_id) + '/start/', post=self.generate_signature(data)):
            return True
        else:
            return False

    def end_broadcast(self):
        """Stopping current broadcast from API 

        Returns:
            bool: if broadcast is stopped
        """
        data = json.dumps({'_uuid': self.uuid, '_uid': self.username_id, '_csrftoken': self.token})
        if self.send_request(endpoint='live/' + str(self.broadcast_id) + '/end_broadcast/',
                             post=self.generate_signature(data)):
            return True
        return False

    def get_post_live_thumbnails(self):
        if self.send_request(endpoint="live/{}/get_post_live_thumbnails/".format(self.broadcast_id)):
            return self.LastJson.get("thumbnails")[int(len(self.LastJson.get("thumbnails")) / 2)]

    def upload_live_thumbnails(self):
        im1 = Image.open(requests.get(self.get_post_live_thumbnails(), stream=True).raw)
        size = 1080, 1920
        im1 = im1.resize(size, Image.ANTIALIAS)
        upload_id = str(int(time.time() * 1000))
        link = os.path.join(tempfile.gettempdir(), "{}.jpg".format(upload_id))
        im1.save(link, "JPEG", quality=100)

        upload_idforurl = "{}_0_{}".format(upload_id, str(hash(os.path.basename(link))))

        rupload_params = {
            "retry_context": '{"num_step_auto_retry":0,"num_reupload":0,"num_step_manual_retry":0}',
            "media_type": "1",
            "xsharing_user_ids": "[]",
            "upload_id": upload_id,
            "image_compression": json.dumps(
                {"lib_name": "moz", "lib_version": "3.1.m", "quality": "80"}
            ),
        }

        h = {
            "Accept-Encoding": "gzip",
            "X-Instagram-Rupload-Params": json.dumps(rupload_params),
            "X-Entity-Type": "image/jpeg",
            "Offset": "0",
            "X-Entity-Name": upload_idforurl,
            "X-Entity-Length": str(os.path.getsize(link)),
            "Content-Type": "application/octet-stream",
            "Content-Length": str(os.path.getsize(link)),
            "Accept-Encoding": "gzip",
        }

        data = open(link, 'rb').read()

        if self.send_request(endpoint="../../rupload_igphoto/{}".format(upload_idforurl), post=data, headers=h):
            if self.LastJson.get('status') == 'ok':
                return self.LastJson.get('upload_id')

    def add_post_live_to_igtv(self, description, title):
        data = json.dumps(
            {
                "_csrftoken": self.token,
                "_uuid": self.uuid,
                "broadcast_id": self.broadcast_id,
                "cover_upload_id": self.upload_live_thumbnails(),
                "description": description,
                "title": title,
                "igtv_share_preview_to_feed": 1,
            }
        )
        if self.send_request(endpoint='live/add_post_live_to_igtv/', post=self.generate_signature(data)):
            print('Live Posted to Story!')
            return True
        return False

    def delete_post_live(self):
        """Deleting video after broadcast is stopped

        Returns:
            bool: If video successfully deleted
        """
        data = json.dumps({'_uuid': self.uuid, '_uid': self.username_id, '_csrftoken': self.token})
        if self.send_request(endpoint='live/{}/delete_post_live/'.format(self.broadcast_id),
                             post=self.generate_signature(data)):
            return True
        return False

    def stop(self):
        self.end_broadcast()
        print('Save Live replay to IGTV ? <y/n>')
        save = input('command> ')
        if save == 'y':
            title = input("Title: ")
            description = input("Description: ")
            print("Please wait...")
            self.add_post_live_to_igtv(description, title)
        else:
            self.delete_post_live()
        print('Exiting...')
        self.is_running = False
        print('Bye bye')

    def get_comments(self):
        """Getting all comments on live broadcast

        Returns:
            dict: list of comments
        """
        if self.send_request("live/{}/get_comment/".format(self.broadcast_id)):
            if 'comments' in self.LastJson:
                for comment in self.LastJson['comments']:
                    print(f"{comment['user']['username']} has posted a new comment: {comment['text']}")
                return self.LastJson['comments']
            else:
                print("There is no comments.")
                return False
