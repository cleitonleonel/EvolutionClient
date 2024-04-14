import time
import json
import queue
from constants import games
from core.http.api import EvolutionAPI


if __name__ == '__main__':
    # Register account in https://novasortebet.com
    evolution = EvolutionAPI("usuario", "senha")
    # games_avaiable = evolution.get_all_games_id()
    # print(games_avaiable)
    evolution.trace_ws = False
    evolution.all_results = False
    for index, game in enumerate(games):
        print(f"{index}: {game['name']}")
    game_selected = input("Insira o número correspondente ao game que deseja obter dados: ")
    print(f"Game selecionado: {games[int(game_selected)].get('name')}" if game_selected else exit())
    evolution.game_id = games[int(game_selected)].get('id')
    evolution.auth()
    if not evolution.is_connected:
        evolution.reconnect()
    evolution.start_websocket()
    response_queue = queue.Queue()
    while True:
        """if evolution.ws_response is not None:
            print(evolution.ws_response)"""
        if not response_queue.empty() and evolution.ws_response != response_queue.queue[-1]:
            response_queue.put(evolution.ws_response)
        elif response_queue.empty():
            response_queue.put(evolution.ws_response)
        if evolution.websocket_closed:
            evolution.reconnect()
            evolution.start_websocket()
        try:
            result = response_queue.get(block=False)
            if result:
                print(result)
        except queue.Empty:
            pass
        time.sleep(3)
