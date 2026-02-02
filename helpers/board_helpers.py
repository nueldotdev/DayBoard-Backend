from functions.db_actions import DBActions





# Function to help with getting boards data. 
# This includes structuring the returned data to contain, lists, cards, etc, within the board detail.
def get_full_boards_data(id: any):
  db = DBActions(use_admin=True)
  data = {
    "message": "Request Successful"
  }
  all_boards = db.get_many('boards', 'creator_id', id)
  
  if not all_boards.data or len(all_boards.data) == 0:
    data['message'] = "No boards found"
    return data

  for board in all_boards.data:
    board.pop('creator_id')
    lists_within_board = db.get_many('lists', 'board_id', board['id'])
    board['lists'] = lists_within_board.data if lists_within_board and lists_within_board.data else []
    
    for list in lists_within_board.data:
      cards_within_list = db.get_many('cards', 'list_id', list['id'])
      list['cards'] = cards_within_list.data if cards_within_list and cards_within_list.data else []
  
  data['boards'] = all_boards.data
  
  return data


async def get_board_data(board_slug: str):
  db = DBActions(use_admin=True)
  data = {
    "message": "Request Successful"
  }
  
  board = db.get_by_field('boards', 'slug', board_slug)
  
  if not board.data or len(board.data) == 0:
    data['message'] = "No boards found"
    return data
  
  lists_within_board = db.get_many('lists', 'board_id', board['id'])
  board['lists'] = lists_within_board.data if lists_within_board and lists_within_board.data else []
  
  for list in lists_within_board.data:
    cards_within_list = db.get_many('cards', 'list_id', list['id'])
    list['cards'] = cards_within_list.data if cards_within_list and cards_within_list.data else []
  
  data['board'] = board.data
  
  return data