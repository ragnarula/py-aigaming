import requests
import logging


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
        'content-type': 'application/json',
        'accept': 'application/json'
    }

    def __init__(self, bot_id, bot_password, on_move, **kwargs):

        self.logger = logging.getLogger(__name__ + '.TexasHoldEmClient')
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

    def offer(self):

        self.logger.debug("Sending game offer")
        self.logger.debug(self.game_config)

        requests.post(self.offer_url,
                      data=self.game_config,
                      headers=self.headers,
                      hooks={'response': self.on_response})

    def on_response(self, response, *args, **kwargs):

        self.logger.debug("Got response")

        json_response = response.json()

        if 'Result' in json_response:

            result = json_response['Result']

            if result is "SUCCESS":

                self.logger.debug("Response successful")
                self.game_state = json_response.GameState
                self.player_key = json_response.PlayerKey
                self.balance = json_response.Balance

                if self.game_state['GameStatus'] is 'RUNNING':

                    self.on_move(TexasHoldemGameState(self.game_state), self)

                else:

                    self.logger.info("Game no longer runnung")
                    self.logger.info(self.game_state['GameStatus'])

            elif result is "WAITING_FOR_GAME":

                self.poll()

            elif result is "GAME_HAS_ENDED":

                self.logger.info("Game Has Ended")

            else:

                self.logger.error("Unhandled response")
                self.logger.debug(response.text)

        else:

            self.logger.error("No result in response")
            self.logger.debug(response.text)

    def poll(self):

        data = {
            'BotId': self.game_config['BotId'],
            'BotPassword': self.game_config['BotPassword'],
            'PlayerKey': self.player_key,
            'MaximumWaitTime': self.game_config['MaxWaitTime']
        }

        requests.post(self.cancel_url,
                      data=data,
                      headers=self.headers,
                      hooks={'response': self.on_response})

    def cancel(self):

        data = {
            'BotId': self.game_config['BotId'],
            'BotPassword': self.game_config['BotPassword'],
            'PlayerKey': self.player_key
        }

        requests.post(self.cancel_url,
                      data=data,
                      headers=self.headers,
                      hooks={'response': self.on_cancel_response})

    def on_cancel_response(self, response, *args, **kwargs):

        self.logger.debug("Got cancellation response")

        json_response = response.json()

        if 'Result' in json_response:

            result = json_response['Result']

            if result is "SUCCESS":

                self.logger.info("Game cancelled")

            elif result is "GAME_ALREADY_RUNNING":

                self.logger.error("Game already started")

            else:

                self.logger.error("Unhandled response")
                self.logger.debug(response.text)

        else:

            self.logger.error("No result in response")
            self.logger.debug(response.text)

    def bet(self, bet_size):

        move_type = {
            'Fold': False,
            'BetSize': bet_size
        }

        data = {
            'BotId': self.game_config['BotId'],
            'BotPassword': self.game_config['BotPassword'],
            'PlayerKey': self.player_key,
            'MoveType': move_type
        }

        requests.post(self.move_url,
                      data=data,
                      headers=self.headers,
                      hooks={'response': self.on_response})

    def fold(self):
        move_type = {
            'Fold': False,
            'BetSize': 0
        }

        data = {
            'BotId': self.game_config['BotId'],
            'BotPassword': self.game_config['BotPassword'],
            'PlayerKey': self.player_key,
            'MoveType': move_type
        }

        requests.post(self.move_url,
                      data=data,
                      headers=self.headers,
                      hooks={'response': self.on_response})
