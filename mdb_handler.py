#! python3
# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
import sqlite3

# ----- Logging Configuration -----
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_formatter = logging.Formatter("%(asctime)s|%(name)s|%(levelname)s\n%(message)s\n")

log_handler = RotatingFileHandler("MDBH Log.log", maxBytes=10000, backupCount=1)
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(log_formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)

logger.addHandler(log_handler)
logger.addHandler(stream_handler)


# noinspection PyBroadException
class MDBHandler:
    """
    Media Database Handler.
    Designed to allow you or a GUI app to add, delete, update and
    search entries in a sqlite3 database.
    """
    def __init__(self, database):
        """Connect to/create the database file and create a cursor."""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.file_name = database

    # ----- Media Table -----
    def add_entry(self, title, description="", age_rating="", genre="",
                  season=0, disc_count=1, media_type="", play_time=0, notes=""):
        """
        Add an entry to the database, minimum information needed is a Title.
        """
        logger.debug(f"MDBHandler.add_entry Adding:\ntitle={title}\n"
                     f"description={description}\nage_rating={age_rating}\n"
                     f"genre={genre}\nseason={season}\ndisc_count={disc_count}\n"
                     f"media_type={media_type}\nplay_time={play_time}\n"
                     f"notes={notes}")
        try:
            with self.connection:
                self.cursor.execute(
                    f"INSERT INTO media VALUES (NULL, :title, :description, :age_rating,"
                    f":genre, :season, :disc_count, :media_type, :play_time, :notes)",
                    {"title": title, "description": description, "age_rating": age_rating,
                     "genre": genre, "season": season, "disc_count": disc_count,
                     "media_type": media_type, "play_time": play_time, "notes": notes})
                self.connection.commit()
        except Exception:
            logger.exception("Error in MCDHandler.add_entry")

    def delete_entry(self, entry):
        """Delete the media entry with 'rowid'."""
        logger.debug(f"MDBHandler.delete_entry\nDELETING: {entry[1]}")
        try:
            with self.connection:
                self.cursor.execute(
                    "DELETE FROM media WHERE rowid=(:rowid)", {"rowid": entry[0]})
        except Exception:
            logger.exception("Error in MDBHandler.delete_entry")

    def update_entry(self, table, rowid, title, description, age_rating,
                     genre, season, disc_count, media_type, play_time, notes):
        """
        Update the entry  with 'rowid' in 'table' with new information,
        usually supplied via gui.
        :param table: Table name.
        :param rowid: The integer primary key id.
        :param title: varchar
        :param description: varchar
        :param age_rating: varchar (not an integer due to 'U' and 'PG' classifications.
        :param genre: varchar
        :param season: integer
        :param disc_count: integer
        :param media_type: varchar
        :param play_time: integer
        :param notes: varchar
        """
        logger.debug(f"MDBHandler.update_entry\nUpdating:\ntable={table}\n"
                     f"rowid={rowid}\ntitle={title}\ndescription={description}\n"
                     f"age_rating={age_rating}\ngenre={genre}\nseason={season}\n"
                     f"disc_count={age_rating}\nmedia_type={media_type}\n"
                     f"play_time={play_time}\nnotes={notes}")
        try:
            with self.connection:
                self.cursor.execute(
                    f"""UPDATE {table}
                    SET title=(:title),
                    description=(:description),
                    age_rating=(:age_rating),
                    genre=(:genre),
                    season=(:season),
                    disc_count=(:disc_count),
                    media_type=(:media_type),
                    play_time=(:play_time),
                    notes=(:notes)
                    WHERE id=(:rowid)""",
                    # Data to pass in:
                    {"rowid": rowid,
                     "title": title,
                     "description": description,
                     "age_rating": age_rating,
                     "genre": genre,
                     "season": season,
                     "disc_count": disc_count,
                     "media_type": media_type,
                     "play_time": play_time,
                     "notes": notes})
                self.connection.commit()
        except Exception:
            logger.exception("Error in MDBHandler.update_entry")

    # ----- Genres Table -----
    def add_genre(self, genre, description="", examples=""):
        """"""
        logger.debug(f"MDBHandler.add_genre\nTrying to insert:\n"
                     f"genre={genre}\ndescription={description}\nexamples={examples}")
        try:
            with self.connection:
                self.cursor.execute(
                    f"INSERT INTO genres VALUES (NULL, :genre, :description, :examples)",
                    {"genre": genre, "description": description, "examples": examples})
                self.connection.commit()
        except Exception:
            logger.exception("Error in MDBHandler.add_genre")

    def delete_genre(self, entry):
        """Removes a genre from the 'genres' table and from all entries with that genre."""
        try:
            with self.connection:
                self.convert_entries(column="genre",
                                     old_value=entry[1],
                                     new_value="-DELETED GENRE-")
                logger.debug(f"MDBHandler.delete_genre\n"
                             f"Swapped '{entry[1]}' to '-DELETED GENRE-'")
                self.cursor.execute("DELETE FROM genres WHERE rowid=:rowid",
                                    {"rowid": entry[0]})
                logger.debug(f"MDBHandler.delete_genre\nDELETED GENRE: {entry}")
                self.connection.commit()
        except Exception:
            logger.exception("Error in MDBHandler.delete_genre")

    def update_genre(self, rowid, genre, description, examples):
        """"""
        logger.debug(f"MDBHandler.update_genre\nUpdating:\nrowid={rowid}\n"
                     f"genre={genre}\ndescription={description}\n"
                     f"examples={examples}")
        try:
            with self.connection:
                self.cursor.execute(
                    """UPDATE genres
                    SET genre=(:genre),
                    description=(:description),
                    examples=(:examples)
                    WHERE rowid=(:rowid)""",
                    {"genre": genre,
                     "description": description,
                     "examples": examples,
                     "rowid": rowid})
                self.connection.commit()
        except Exception:
            logger.exception("Error in MDBHandler.update_genre")

    # ----- Media Types Table -----
    def add_media_type(self, media_type):
        """"""
        logger.debug(f"MDBHandler.add_media_type\nmedia_type={media_type}")
        try:
            with self.connection:
                self.cursor.execute(
                    "INSERT INTO media_types VALUES (NULL, :type)",
                    {"type": media_type})
                self.connection.commit()
        except Exception:
            logger.exception("Error in MDBHandler.add_media_type")

    def delete_media_type(self, entry):
        """"""
        try:
            with self.connection:
                self.convert_entries(column="media_type",
                                     old_value=entry[1],
                                     new_value="-DELETED MEDIA TYPE-")
                logger.debug(f"MDBHandler.delete_media_type\n"
                             f"Swapped '{entry[1]}' to '-DELETED MEDIA TYPE-'")
                self.cursor.execute("DELETE FROM media_types WHERE rowid=:rowid",
                                    {"rowid": entry[0]})
                logger.debug(f"MDBHandler.delete_media_type\nDELETED TYPE: {entry[0]}")
                self.connection.commit()
        except Exception:
            logger.exception("Error in MDBHandler.delete_media_types")

    def update_media_type(self, rowid, media_type):
        """"""
        try:
            with self.connection:
                self.cursor.execute(
                    """UPDATE media_types
                    SET type=(:media_type)
                    WHERE rowid=(:rowid)""",
                    {"media_type": media_type,
                     "rowid": rowid})
                self.connection.commit()
        except Exception:
            logger.exception("Error in MDBHandler.update_media_type")

    # ----- Search Function(s) -----
    def return_all_entries(self, table="media", column="title", count=1000):
        """
        Creates a generator to return all entries in a table so they can be iterated over.

        :param table:   Name of the table from which to return entries (defaults to 'media').

        :param column:  Name of the column with the data to return
                        (defaults to 'title' or use '*' for complete rows).

        :param count:   Acts as a buffer for large data sets, currently defaults to 1000.

        :return:        Yields one row from the results at a time for iteration.
        """
        try:
            with self.connection:
                self.cursor.execute(f"""SELECT {column} FROM {table} ORDER BY {column}""")
                while True:
                    results = self.cursor.fetchmany(count)
                    if not results:
                        break
                    for row in results:
                        yield row
        except Exception:
            logging.exception("Error in MDBHandler.return_all_entries")

    def return_distinct_entries(self, table, column, count=1000):
        """"""
        try:
            with self.connection:
                self.cursor.execute(f"""SELECT DISTINCT {column} FROM {table} ORDER BY {column}""")
                while True:
                    results = self.cursor.fetchmany(count)
                    if not results:
                        break
                    for row in results:
                        yield row
        except Exception:
            logger.exception("Error in MDBHandler.return_distinct_entries")

    def filter_entries(self, table="media", column="title", value="", count=1000):
        """
        Create a generator with entries with the given parameters.

        :param table:   Table name to search.
        :param column:  The column to search.
        :param value:   And what to search for.
        :param count:   Acts as a buffer for large data sets, currently defaults to 1000.
        :return:        A generator with the results inside.
        """
        try:
            logger.debug(f"MDBHandler.filter_entries\n"
                         f"ran with:\n"
                         f"table={table}/{type(table)}\n"
                         f"column={column}/{type(column)}\n"
                         f"value={value}/{type(value)}s")
            with self.connection:
                self.cursor.execute(
                    f"""SELECT * FROM {table} WHERE {column}=('{value}') ORDER BY {column}""")
                while True:
                    results = self.cursor.fetchmany(count)
                    if not results:
                        break
                    for row in results:
                        yield row
        except Exception:
            logger.exception("Error in MDBHandler.filter_entries")

    def search(self, query, column=None, count=1000):
        """
        Search for 'query' in the media table, columns title, description, genre, notes.

        If column is not specified checks all columns, even returns partials.

        :param query:   What you are searching for e.g. 'Marvel', 'PS4', '90210'.
        :param column:  Which column to look in (Optional).
        :param count:   Acts as a buffer for larger databases (default: 1000).
        :return:        Returns a generator containing rows from the database,
                        that have a match to 'query'.
        """
        try:
            with self.connection:
                if column is None:
                    self.cursor.execute(
                        f"""SELECT * FROM media WHERE
                        title LIKE (:query) OR
                        description LIKE (:query) OR
                        genre LIKE (:query) OR
                        notes LIKE (:query)""",
                        {"query": f"%{query}%"})
                    while True:
                        results = self.cursor.fetchmany(count)
                        if not results:
                            break
                        for row in results:
                            yield row
                else:
                    self.cursor.execute(
                        f"SELECT * FROM media WHERE {column} LIKE (:query)",
                        {"query": f"%{query}%"})
                    while True:
                        results = self.cursor.fetchmany(count)
                        if not results:
                            break
                        for row in results:
                            yield row
        except Exception:
            logger.exception("Error in MDBHandler.search")

    def select_one_entry(self, table="media", column="title", value=""):
        """

        :param table:
        :param column:
        :param value:
        :return:
        """
        try:
            with self.connection:
                self.cursor.execute(f"""SELECT * FROM {table} WHERE {column}=(:value)""",
                                    {"value": value})
                entry = self.cursor.fetchone()
                logger.debug(f"MDBHandler.select_one_entry\n"
                             f"Table = {table}\nColumn = {column}\nValue = {value}\n"
                             f"Result = {entry}")
                return entry
        except Exception:
            logger.exception("Error in MDBHandler.select_one_entry")

    # ----- Other Functions -----
    def check_if_entry_exists(self, table, column, entry):
        """
        Check to see if an entry already exists.
        :param table:   The table to look in.
        :param column:  The column to check.
        :param entry:   And what to check for.
        :return:        True if something is found else False.
        """
        try:
            with self.connection:
                self.cursor.execute(
                    f"SELECT * FROM {table} WHERE {column}=(:entry)",
                    {"entry": entry})
                if self.cursor.fetchall():
                    logger.debug(
                        f"MCDHandler.check_if_entry_exists returned True\n"
                        f"Table: {table} - Column: {column} - Entry: {entry}")
                    return True
                return False
        except Exception:
            logger.exception("Error in MCDHandler.check_if_entry_exists")

    def close(self):
        """Close the cursor and database connections."""
        try:
            self.cursor.close()
            self.connection.close()
        except Exception:
            logger.exception("Error in MDBHandler.close")

    def convert_entries(self, column, old_value, new_value):
        """Update entries with 'old_value' in 'column' and update to 'new_value'

        :param column:
        :param old_value:
        :param new_value:
        """
        try:
            with self.connection:
                self.cursor.execute(
                    f"UPDATE media SET {column}=:new_value WHERE {column}=:old_value",
                    {"new_value": new_value, "old_value": old_value})
                self.connection.commit()
        except Exception:
            logger.exception("Error in MDBHandler.convert_entries")

    def count_entries(self):
        """
        Counts the media tables entries by media type.

        :return: A string of media types the amount of entries with that type.
                 e.g. Audio CD: 3, DVD - Movie: 5, etc.
        """
        try:
            with self.connection:
                self.cursor.execute("SELECT COUNT(*) FROM media")
                total = self.cursor.fetchone()
                output = f"Total Media Count: {total[0]} entries\n"
                for media_type in self.return_distinct_entries(
                        table="media",
                        column="media_type"):
                    self.cursor.execute(
                        f"SELECT COUNT(*) FROM media WHERE media_type=:type",
                        {"type": media_type[0]})
                    count = self.cursor.fetchone()
                    output += f"{media_type[0]}: {count[0]}, "
            logger.debug(f"MDBHandler.count_entries returned:\n{output}")
            return output.rstrip(", ")
        except Exception:
            logger.exception("Error in MDBHandler.count_entries")

    def create_tables(self):
        """
        Create the base tables of the media database:

        genres: Table columns consists of:
                id(int), genre(varchar), description(varchar) and examples(varchar).
        media:  Table columns consists of:
                id(int), title(varchar), description(varchar), age_rating(varchar),
                genre(varchar), cast(varchar), season(int), disc_count(int),
                media_type(varchar) and play_time(int).
        media_types: Table columns consists of:
                id(int) and type(varchar).
        """
        try:
            with self.connection:
                # The media_types table:
                self.cursor.execute(
                    f"""CREATE TABLE IF NOT EXISTS media_types (
                    id INTEGER PRIMARY KEY NOT NULL,
                    type VARCHAR)""")

                # The genres table:
                self.cursor.execute(
                    f"""CREATE TABLE IF NOT EXISTS genres (
                    id INTEGER PRIMARY KEY,
                    genre VARCHAR,
                    description VARCHAR,
                    examples VARCHAR)""")

                # The main media table:
                self.cursor.execute(
                    f"""CREATE TABLE IF NOT EXISTS media (
                    id INTEGER PRIMARY KEY, 
                    title VARCHAR NOT NULL,
                    description VARCHAR,
                    age_rating VARCHAR,
                    genre VARCHAR,
                    season INTEGER,
                    disc_count INTEGER,
                    media_type VARCHAR,
                    play_time INTEGER,
                    notes VARCHAR)""")
                self.connection.commit()
        except Exception:
            logger.exception("Error in MDBHandler.create_tables")

    def __str__(self):
        """"""
        return f"Database: {self.file_name}\nContaining:\n{self.count_entries()}."


def main():
    """"""
    app = MDBHandler("Media-Database.db")
    app.create_tables()
    print(app)


if __name__ == "__main__":
    main()
