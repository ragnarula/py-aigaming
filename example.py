import ai_gaming.texas_hold_em as tx
import logging
logging.basicConfig(level=logging.DEBUG)


def on_move(game_state, game_control):
    game_control.bet(game_state.BigBlind)


def main():
    bot_id = "rag4"
    bot_password = "123123"

    game = tx.TexasHoldemClient(bot_id, bot_password, on_move)
    game.offer()


if __name__ == "__main__":
    main()
