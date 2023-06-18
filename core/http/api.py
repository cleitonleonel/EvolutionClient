import random
import requests
from threading import Thread
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from core.ws.client import WebSocketClient

URL_BASE = 'https://game.novasortebet.com'
URL_CLIENT = 'https://grt-evo.com'
WSS_BASE = "wss://grt-evo.com"
VERSION_API = "0.0.1-professional"

retry_strategy = Retry(
    connect=3,
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504, 104, 403],
    allowed_methods=["HEAD", "POST", "PUT", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)


class Response(object):

    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class Browser(object):

    def __init__(self):
        self.response = None
        self.headers = None
        self.session = requests.Session()

    def set_headers(self, headers=None):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/87.0.4280.88 Safari/537.36"
        }
        if headers:
            for key, value in headers.items():
                self.headers[key] = value

    def get_headers(self):
        return self.headers

    @staticmethod
    def get_timestamp():
        return str(int(datetime.now().timestamp()))

    def send_request(self, method, url, **kwargs):
        try:
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)
            return self.session.request(method, url, **kwargs)
        except requests.exceptions.ConnectionError:
            return Response({"result": False,
                             "object": self.response,
                             "message": "Network Unavailable. Check your connection."
                             }, 104)


class EvolutionAPI(Browser):
    websocket_thread = None
    websocket_client = None
    websocket_closed = None
    ws_response = None
    is_logged = False
    trace_ws = False
    game_id = None
    evo_user_id = None
    evo_session_id = None

    def __init__(self, email=None, password=None):
        super().__init__()
        self.is_connected = False
        self.email = email
        self.password = password
        self.wss_url = None
        self.set_headers()
        self.headers = self.get_headers()
        self.get_response()
        self.auth()

    def get_response(self):
        return self.send_request('GET',
                                 f"{URL_BASE}/cassinoaovivo",
                                 headers=self.headers)

    def auth(self):
        payload = {
            "username": self.email,
            "password": self.password,
            "ajax_serialize": {
                "username": self.email,
                "password": self.password
            },
            "dtCache": self.get_timestamp()
        }
        self.headers["origin"] = URL_BASE
        self.headers["referer"] = f"{URL_BASE}/cassinoaovivo"
        self.response = self.send_request("POST",
                                          f"{URL_BASE}/entrar/login/insert",
                                          json=payload,
                                          headers=self.headers)
        if self.response:
            self.is_connected = True
            data = self.get_game_player()
            self.evo_user_id = data.get("user_id")
            self.evo_session_id = data.get("session_id")
        return self.response

    def get_game_player(self):
        payload = {
            "game": "9c45ebf83907bfae80190294bbfa24a5a42a2523",
            "fornecedor": "slotegrator",
            "mobile": 0,
            "usabonus": 0
        }
        self.response = self.send_request("POST",
                                          f"{URL_BASE}/cassinoaovivo/getgameurl",
                                          data=payload,
                                          headers=self.headers)
        return self.launch_game()

    def launch_game(self):
        self.response = self.send_request("GET",
                                          f"{self.response.json().get('url')}")
        payload = {
            "device": "desktop",
            "wrapped": True,
            "client_version": "6.20230601.72759.25995-e3aa0e2b12"
        }
        return self.send_request("GET",
                                 f"{URL_CLIENT}/setup",
                                 params=payload).json()

    def reconnect(self):
        print("Reconectando...")
        self.auth()

    @property
    def websocket(self):
        return self.websocket_client.wss

    def start_websocket(self):
        self.close()
        self.set_headers()
        caracteres = "abcdefghijklmnopqrstuvwxyz1234567890"
        payload = {
            "messageFormat": "json",
            "device": "Desktop",
            "instance": "".join([random.choice(caracteres) for _ in range(6)]),
            "EVOSESSIONID": self.evo_session_id,
            "client_version": "6.20230530.72609.25899-854ba93305",
        }
        self.wss_url = f'{WSS_BASE}/public/lobby/socket/v2/{self.evo_user_id}?' \
                       f'{"&".join(f"{key}={value}" for key, value in payload.items())}'
        self.websocket_client = WebSocketClient(self)
        self.websocket_thread = Thread(
            target=self.websocket.run_forever,
            kwargs={
                'origin': f'{URL_CLIENT}',
                'host': 'grt-evo.com',
            }
        )
        self.websocket_thread.daemon = True
        self.websocket_thread.start()

    def close(self):
        if self.websocket_client:
            self.websocket.close()
            self.websocket_thread.join()
            self.websocket_thread = None

    def websocket_alive(self):
        return self.websocket_thread.is_alive()
