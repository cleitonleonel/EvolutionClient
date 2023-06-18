import time
import json
from constants import players
from core.http.api import EvolutionAPI


if __name__ == '__main__':
    # Register account in https://game.novasortebet.com
    bba = EvolutionAPI("email", "password")
    bba.trace_ws = False
    for index, player in players.items():
        print(f"{index}: {player}")
    player_selected = int(input("Insira o número correspondente ao game que deseja obter dados: "))
    print(f"Game selecionado: {players.get(player_selected)}" if player_selected else exit())
    bba.game_id = players.get(player_selected)
    if not bba.is_connected:
        bba.reconnect()
    bba.start_websocket()
    while True:
        if bba.ws_response is not None:
            # print(json.dumps(bba.ws_response, indent=4))
            print(bba.ws_response[:9])
        if bba.websocket_closed:
            bba.reconnect()
            bba.start_websocket()
        time.sleep(3)
