from database.db import SessionLocal

class DbHandler:
    def __enter__(self):
        # logger.debug("opening connection to database")
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        # logger.debug("closing connection to database")
        # self.db.commit()
        self.db.close()
