from spaceandtime import SpaceAndTime, SXTTable

# Log into Space and Time network
sxt = SpaceAndTime('./.env_admin')
sxt.authenticate()


# CREATE TABLE: SXTDEMO.Verifiable_TicTacToe
#   This holds deck before the game starts, so it can't be altered
#   as players join.
tbl_game = SXTTable('SXTDEMO.Verifiable_TicTacToe',
                    from_file = './.env_admin',
                    access_type = sxt.TABLE_ACCESS.PUBLIC_READ, 
                    SpaceAndTime_parent=sxt)
tbl_game.immutable = False
tbl_game.create_ddl = """
Create Table {table_name} 
( Game_ID      varchar
, Turn_No      integer
, Player_Name  varchar
, Player_Mark  varchar
, Row_ID       integer
, Col_ID       integer
, Game_State   varchar
, primary key(Game_ID, Turn_No)
) {with}
"""

if tbl_game.exists: tbl_game.drop()
tbl_game.create()

