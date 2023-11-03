from telegram.ext import ConversationHandler

# SELECTING_ACTION, REGISTER, BALANCE, ADD_ADMIN, REMOVE_ADMIN, INFO, STOP = map(chr, range(4))


# State definitions for top level conversation
MAINMENU, SELECTING_ACTION, REGISTER, SHOWING, = map(chr, range(4))

# State definitions for second level conversation
SELECTING_LEVEL, SELECTING_GENDER = map(chr, range(4, 6))

# State definitions for descriptions conversation
SELECTING_FEATURE, TYPING = map(chr, range(6, 8))

# Meta states
STOPPING = map(chr, range(8, 10))

# Shortcut for ConversationHandler.END
END = ConversationHandler.END

# Different constants for this example
(
    SUCA,
    INFO,
    CHILDREN,
    SELF,
    MALE,
    FEMALE,
    AULETTA,
    USERNAME,
    START_OVER,
    FEATURES,
    CURRENT_FEATURE,
    CURRENT_LEVEL,
) = map(chr, range(10, 22))