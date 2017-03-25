# AI Gaming Texas Hold'em Poker Python Template

To use this template:
1. Clone this repository
2. Install the requirements with ```pip install -r requirements.txt```
3. Edit bot_id and bot_password in ```example.py```.
3. Run ```example.py``` with ```python example.py```.

## Explanation

Line 30 constructs a ``TexasHoldemClient``` with your id and password for the bot and a callback function.
The callback gets called at every step with the new game_state and a reference to the client whenever it's your move.
Use the contents of game_state to decide what to do. You can either call ```client.bet(bet_size)``` to bet or
```client.fold()``` to fold.

The constructor also takes extra keyword arguments for:

* max_wait_time (default 500)
* game_style_id (default 9)
* dont_play_same_user (default False)
* dont_play_same_bot (default False)
* opponent_id (default None)

Once constructed call client.offer() to offer a game and wait for another bot to connect.

Set the loglevel to DEBUG in line 10 to see more output.

