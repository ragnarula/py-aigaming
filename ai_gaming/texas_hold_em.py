import requests
import logging
import json
import gevent
import gevent.pool
import signal


class TexasHoldemGameState:
    def __init__(self, data):
        for key in data:
            setattr(self, key, data[key])


class TexasHoldemClient:
    offer_url = "https://beta.aigaming.com/Api/OfferGame"
    cancel_url = "https://beta.aigaming.com/Api/CancelGameOffer"
    poll_url = "https://beta.aigaming.com/Api/PollForGameState"
    move_url = "https://beta.aigaming.com/Api/MakeMove"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    def __init__(self, bot_id, bot_password, on_move, **kwargs):
        self.pool = gevent.pool.Pool()
        self.cancelled = False
        self.logger = logging.getLogger(__name__ + '.TexasHoldemClient')
        self.on_move = on_move
        self.game_config = {}
        self.game_state = {}
        self.player_key = ""
        self.balance = 0
        self.game_config['BotId'] = bot_id
        self.game_config['BotPassword'] = bot_password
        self.game_config['MaximumWaitTime'] = kwargs.get('max_wait_time', 500)
        self.game_config['GameStyleId'] = kwargs.get('game_style_id', 9)
        self.game_config['DontPlayAgainstSameUser'] = kwargs.get('dont_play_same_user', False)
        self.game_config['DontPlayAgainstSameBot'] = kwargs.get('dont_play_same_bot', False)

        if kwargs.get('OpponentId', None) is not None:
            self.game_config['OpponentId'] = kwargs.get('opponent_id', None)

        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signal, frame):
        self.cancelled = True
        self.cancel()

    def copy_response(self, json_response):

        self.logger.debug("Copying response state")
        self.logger.debug(json_response)
        self.game_state = json_response.get('GameState', self.game_state)
        self.player_key = json_response.get('PlayerKey', self.player_key)
        self.balance = json_response.get('Balance', self.balance)

    def check_valid_response(self, response, handler):

        if response.status_code == requests.codes.ok:

            json_response = response.json()
            result = json_response['Result']
            self.logger.debug("Result: {}".format(result))
            self.copy_response(json_response)

            handler(result)
        else:
            self.logger.debug("Got non OK response: {}".format(response.status_code))
            self.logger.debug(response.text)

    def get_response_handler(self, response, response_handler):

        def handler():
            self.check_valid_response(response, response_handler)

        return handler

    def offer(self):
        if self.cancelled:
            return

        self.logger.debug("Offering")
        self.logger.debug(self.game_config)

        result = requests.post(self.offer_url,
                               data=json.dumps(self.game_config),
                               headers=self.headers)

        self.pool.spawn(self.get_response_handler(result, self.on_response))
        self.pool.join()

    def poll(self):

        data = json.dumps({
            'BotId': self.game_config['BotId'],
            'BotPassword': self.game_config['BotPassword'],
            'PlayerKey': self.player_key,
            'MaximumWaitTime': self.game_config['MaximumWaitTime']
        })

        self.logger.debug("Polling")
        self.logger.debug(data)
        gevent.sleep(0.5)

        if self.cancelled:
            return

        result = requests.post(self.poll_url,
                               data=data,
                               headers=self.headers)

        self.pool.spawn(self.get_response_handler(result, self.on_response))

    def cancel(self):

        data = json.dumps({
            'BotId': self.game_config['BotId'],
            'BotPassword': self.game_config['BotPassword'],
            'PlayerKey': self.player_key
        })

        self.logger.debug("Cancelling")
        self.logger.debug(data)

        result = requests.post(self.cancel_url,
                               data=data,
                               headers=self.headers)

        self.pool.spawn(self.get_response_handler(result, self.on_cancel_response))

    def bet(self, bet_size):
        if self.cancelled:
            return
        move_type = {
            'BetSize': bet_size
        }

        data = json.dumps({
            'BotId': self.game_config['BotId'],
            'BotPassword': self.game_config['BotPassword'],
            'PlayerKey': self.player_key,
            'Move': move_type
        })

        self.logger.debug("Betting")
        self.logger.debug(json.dumps(data))

        result = requests.post(self.move_url,
                               data=data,
                               headers=self.headers)

        self.pool.spawn(self.get_response_handler(result, self.on_response))

    def fold(self):
        if self.cancelled:
            return
        move_type = {
            'Fold': False,
        }

        data = json.dumps({
            'BotId': self.game_config['BotId'],
            'BotPassword': self.game_config['BotPassword'],
            'PlayerKey': self.player_key,
            'MoveType': move_type
        })

        self.logger.debug("Folding")
        self.logger.debug(data)

        result = requests.post(self.move_url,
                               data=data,
                               headers=self.headers)

        self.pool.spawn(self.get_response_handler(result, self.on_response))

    def on_response(self, result):

        if result == "SUCCESS":
            self.play()

        elif result == "WAITING_FOR_GAME":
            self.logger.info("Waiting for an opponent")
            self.poll()

        elif result == "NOT_YOUR_MOVE":
            self.logger.error("Not your turn to make a move")
            self.poll()

        elif result == 'INVALID_MOVE':
            self.logger.error("Invalid move requested")
            self.play()

        else:
            self.logger.debug("Unhandled response: {}".format(result))
            self.logger.debug(self.game_state)

    def on_cancel_response(self, result):

        if result == "SUCCESS":
            self.logger.info("Game successfully cancelled")

        elif result == "GAME_ALREADY_STARTED":
            self.play()

        else:
            self.logger.debug("Unhandled cancel response: {}".format(result))
            self.logger.debug(self.game_state)

    def play(self):

        if self.game_state['GameStatus'] == 'RUNNING':

            if self.game_state['IsMover']:
                self.on_move(TexasHoldemGameState(self.game_state), self)

            else:
                self.poll()

        else:
            self.logger.info("Game no longer running")
            self.logger.info(self.game_state['GameStatus'])
