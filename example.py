"""
Import the texas hold em package and logging for output
"""
import ai_gaming.texas_hold_em as tx
import logging

"""
Set the log level to debug to get all of the output
"""
logging.basicConfig(level=logging.INFO)


def on_move(game_state, client):
    """
    Put your bot code in this function. The game_state parameter gives you the current game state at every move. 
    It contains useful information like BigBlind amount, current bet etc..
    Look at http://help.aigaming.com/rest-api-manual in the GameStateType section for a complete list of what it holds
    The 'client' parameter is a reference to the TexasHoldemClient, it allows you to client.bet(int betsize),
    client.fold() or client.cancel(). To call, bet the same size as the game_state.OpponentRoundBetTotal or minBet.
    """
    min_bet = game_state.OpponentRoundBetTotal - game_state.PlayerRoundBetTotal
    max_bet = min_bet + game_state.OpponentStack
    client.bet(min_bet)


def main():
    bot_id = ""
    bot_password = ""

    client = tx.TexasHoldemClient(bot_id, bot_password, on_move)
    client.offer()


if __name__ == "__main__":
    main()
