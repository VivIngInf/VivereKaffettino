from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///database.sqlite", isolation_level="READ UNCOMMITTED", echo=True)

"""with engine.connect() as connection:
    result = connection.execute()"""