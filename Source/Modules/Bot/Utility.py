from hashlib import sha256
from base64 import urlsafe_b64encode


def safe_hash_name(string1: str, string2: str) -> str:
    return urlsafe_b64encode(sha256(str(string1 + "_" + string2).encode()).digest()).decode('utf-8')[:16]


ACQUIRE_USERNAME_REGISTRATION = "SRwRn962weWpk_8A"
ACQUIRE_AGE_REGISTRATION = "JIOLaLm4rDKlRBbl"
ACQUIRE_USERNAME_RECHARGE = "0M4vBDMcZnKfxed9"
ACQUIRE_AMOUNT_RECHARGE = "lcADSaGdP15eAw2i"
ACQUIRE_USERNAME_VERIFY = "_4xTaIgSUS3oZKIL"
ACQUIRE_CARD_NUMBER = "iVivD-PBK7FWrL2D"
ACQUIRE_USERNAME_ADD_ADMIN = "VbO0w6FbL_Vu1imZ"
ACQUIRE_USERNAME_REMOVE_ADMIN = "GqRI4J9kGURvhy8P"
ACQUIRE_MESSAGE_TO_SEND_ALL = "RWSxXiHZAPNZKuPI"
ACQUIRE_USERNAME_CARD_CHANGE = "IxylYTF4FvHARdOo"
ACQUIRE_CARD_NUMBER_CHANGE = "ym4rhDgd54OMJL-n"
ACQUIRE_NEW_PRODUCT = "InbjTLYzVY2L_fqK"
ACQUIRE_PRICE_PRODUCT = "x2AkueUDv6gYUkuI"
ACQUIRE_USERNAME_UNLIMITED = "8v6uq4n-VxbLNNmj"
ACQUIRE_CARD_UNLIMITED = "DePANQG74P8A39mi"
ACQUIRE_USERNAME_TO_ACTIVATE = "34uQ23-1KA3i8_3y"
ACQUIRE_USERNAME_TO_DEACTIVATE = "rSYP1-x3XfdOCSaD"
ACQUIRE_USERNAME_HISTORY = "dh0dPnn11aPYNZ76"

CONVERSATION_CLASSES = ["ConversationManager", "Registration", "Recharge", "AdminMenu", "VerifyUser", "AddAdmin",
                        "ViewHistory",
                        "RemoveAdmin", "SendMessageAll", "ChangeCard", 'StorageMenu', 'NewProduct', "RemoveProduct",
                        'UnlimitedUser', 'ManageCard', 'ActivateCard', 'DeactivateCard']


GENDER_DICT = {"donna": "a", "uomo": "o", "altro": "ə"}
DB_GENDER_DICT = {"D": "a", "U": "o", "A": "ə", "M": "o", "F": "a"}
