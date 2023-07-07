import time
import json
from constants import games
from core.http.api import EvolutionAPI


if __name__ == '__main__':
    # Register account in https://game.novasortebet.com
    evolution = EvolutionAPI("user", "pass")
    # evolution.get_all_games_id()
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
    while True:
        if evolution.ws_response is not None:
            # print(json.dumps(evolution.ws_response, indent=4))
            print(evolution.ws_response[:9])
        if evolution.websocket_closed:
            evolution.reconnect()
            evolution.start_websocket()
        time.sleep(3)
