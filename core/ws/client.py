import time
import json
import random
import websocket
from threading import Timer
from datetime import datetime


def send_ping(ws):
    caracteres = "abcdefghijklmnopqrstuvwxyz1234567890"
    _id = "".join([random.choice(caracteres) for _ in range(10)])
    interval = int(random.choice([5, 10, 15]))
    timestamp = int(time.time() * 1000)
    ping_msg = str({
        "id": _id,
        "type": "metrics.ping",
        "args": {"t": timestamp}
    })
    try:
        ws.send(json.dumps(ping_msg))
        Timer(interval, send_ping, args=(ws,)).start()
    except:
        pass


class WebSocketClient(object):

    def __init__(self, api):
        self.api = api
        self.wss = websocket.WebSocketApp(
            self.api.wss_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open,
            on_ping=self.on_ping,
            on_pong=self.on_pong,
            header=self.api.headers
        )
        websocket.enableTrace(self.api.trace_ws)

    def on_open(self, ws):
        print("Starting Websocket...")
        caracteres = "abcdefghijklmnopqrstuvwxyz1234567890"
        _id = "".join([random.choice(caracteres) for _ in range(10)])
        message = {"id": _id, "type": "lobby.initLobby", "args": {"version": 2}}
        self.wss.send(json.dumps(message))
        send_ping(ws)
        self.api.websocket_closed = False

    def on_message(self, ws, message):
        data = json.loads(message)
        if "lobby.historyUpdated" in message:
            game_data = data["args"].get(self.api.table_id)
            if game_data:
                self.api.ws_response = game_data["results"]
                msg_video = str({
                    "log": {
                        "type": "CLIENT_GAME_RESULT",
                        "value": {
                            "isPlayerWins": 'false',
                            "result": data["args"].get(self.api.table_id),
                            "winAmount": 0,
                            "winningChips": {},
                            "payouts": {},
                            "balance": 10000.00,
                            "balanceId": "combined",
                            "latency": 206,
                            "currency": "BRL",
                            "layout": "ImmersiveV2",
                            "browser": "CHROME 112.0.0.0",
                            "userAgent": self.api["headers"]["user_agent"],
                            "gameTime": datetime.now().strftime("%H:%M:%S"),
                            "gameType": "topdice",
                            "channel": "PCMac",
                            "orientation": "landscape",
                            "gameDimensions": {
                                "width": 1045.328125,
                                "height": 588
                            },
                            "gameId": self.api.table_id
                        }
                    }
                })
                self.wss.send(json.dumps(msg_video))
        elif "roulette.recentResults" in message:
            self.api.ws_response = data["args"].get("recentResults")
        elif "connection.kickout" in message:
            self.api.websocket_closed = True

    def on_error(self, ws, error):
        pass

    def on_close(self, ws, close_status_code, close_msg):
        self.api.websocket_closed = True

    def on_ping(self, ws, message):
        print("PING: ", message)

    def on_pong(self, ws, message):
        print("PONG")
