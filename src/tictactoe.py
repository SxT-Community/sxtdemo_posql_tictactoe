import uuid
from faker import Faker
from pprint import pprint
from spaceandtime import SXTTable, SXTUser
fkr = Faker()

judge = SXTUser('.env_admin')
judge.authenticate()
results = SXTTable('SXTDEMO.Verifiable_TicTacToe', '.env_admin', default_user=judge)
results.add_biscuit('game biscuit',  results.PERMISSION.SELECT, results.PERMISSION.INSERT)

success, data = results.select(
    f"Select count(*) as Games_Played from {results.table_name} where Game_State = 'started'")
if success: print(f'\n{"-"*25}\nGames played to date: {data[0]["GAMES_PLAYED"]}\n')



def is_winner(selected_squares:list)->bool:
    """Evaluates the tictactoe squares selected, returning True if a winner
    """
    if len(selected_squares) < 3: return False 
    for test in range(1,4):
        if [r[0] for r in squares].count(test) == 3: return True
        if [c[0] for c in squares].count(test) == 3: return True
    if (2,2) in selected_squares: #diagonal
        if (1,1) in selected_squares and (3,3) in selected_squares: return True
        if (3,1) in selected_squares and (1,3) in selected_squares: return True
    return False 

def printx(msg:str=''):
    print(msg)
    input('')

games_to_play = 2
gameid = ''


for game_number in range(1, games_to_play+1):
    
    # reset game values for a new game:
    turn = 0
    game_state = 'started'
    gameid = f'{game_number:09}-{str(uuid.uuid4())}'
    squares = [(x,y) for x in list(range(1,4)) for y in list(range(1,4))] # row, col

    # assign players:
    playerX = SXTUser('../.env_user'); playerX.name = fkr.name(); playerX.squares_selected = []
    playerO = SXTUser('../.env_user'); playerO.name = fkr.name(); playerO.squares_selected = []

    # Play the game and see who wins!
    while squares != []:        
        for player in [playerX, playerO]:
            turn +=1
            
            square_selected = fkr.random.choice(squares)
            player.squares_selected.append(square_selected)
            squares.remove(square_selected)
            winner = is_winner(player.squares_selected)

            # record current state of the game:
            if   turn == 1:     game_state = 'started'
            elif winner:        game_state = 'winner' 
            elif squares == []: game_state = 'tie'
            else: game_state = 'wip'

            data = [{'Game_ID': gameid,
                     'Turn_No': turn,
                     'Player_Name': player.name,
                     'Player_Mark': 'X' if player == playerX else 'O',
                     'Row_ID':square_selected[0],
                     'Col_ID':square_selected[1],
                     'Game_State': game_state
                      }]
            
            results.insert.with_list_of_dicts(data)
            if game_state in['winner','tie']:  break #end of game
        if game_state in['winner','tie']:  break #end of game


    success, data = judge.execute_query(f"""
        Select Turn_No, Player_Name, Player_Mark, Game_State
        ,'row'||Row_ID ||', col'||Col_ID as Square
        from {results.table_name}
        where Game_ID =  '{gameid}'
        order by Turn_No""")
    if success: 
        for row in data: 
            print(f"turn {row['TURN_NO']} ({row['PLAYER_MARK']}) took {row['SQUARE']} -- {row['GAME_STATE'].ljust(8)} for {row['PLAYER_NAME']}")
        printx('')




# Report Results:
summary_sql = """
Select /*! USE COLS */
Mark, State, Freq 
,(Freq*1.0000) / sum(freq) over() as Freq_Pct
from 
  (
  Select case when Game_State = 'winner' then Player_Mark else '-' end Mark 
  ,Game_State as State
  ,count(*) as Freq 
  from SXTDEMO.Verifiable_TicTacToe
  where Game_State in ('winner','tie')
  group by Mark,Game_State
)
order by 1 desc
"""
success, data = judge.execute_query(summary_sql) 
if success:
    print(f"\n{'-'*25}\nALL-GAMES SUMMARY:")
for row in data:
    print(f"  {row['Mark']} = {row['State']} {row['Freq']} times ({row['Freq_Pct']:.2%})")



# -------------------------------------- 
# -------------------------------------- 
# ----- VERIFY THE GAME WAS FAIR  ------
# -------------------------------------- 
# -------------------------------------- 

#  - SXT Verifcation API (do we have a name?)
#    https://docs.spaceandtime.io/reference/execute-sql-tamperproof

#  - Github Verifier Repo (Open Source)
#    TBD 

#  - Horizen Network / AlignLayer Network
#    TBD

#  - On-Chain
#    TBD