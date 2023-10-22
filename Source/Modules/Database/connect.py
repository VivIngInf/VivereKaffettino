from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///database.sqlite", echo=True)

"""with engine.connect() as connection:
    result = connection.execute()"""