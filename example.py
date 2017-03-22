import ai_gaming.texas_hold_em as tx
import logging
logging.basicConfig(level=logging.DEBUG)


def on_move(game_state, context):
    print (game_state)


def main():
    bot_id = "ragnarula-5"
    bot_password = 123123

    game = tx.TexasHoldemClient(bot_id, bot_password, on_move)
    game.offer()


if __name__ == "__main__":
    main()
