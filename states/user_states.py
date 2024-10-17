from aiogram.dispatcher.filters.state import StatesGroup, State

class CardState(StatesGroup):
    waiting_for_card = State()
    
class OrderHistoryStates(StatesGroup):
    viewing_order = State()
    
    
class SupportStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_new_question = State()
    
    
class ReviewStates(StatesGroup):
    rating = State()
    text = State()
    
    
class ReviewOrderStates(StatesGroup):
    rating = State()
    text = State()