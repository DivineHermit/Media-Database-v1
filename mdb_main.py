import sys
import logging
from logging.handlers import RotatingFileHandler
from PyQt5 import QtWidgets
from mdb_handler import MDBHandler  # The Database Handler
from mdb_ui_main_window import Ui_MainWindow  # Main GUI Window
from mdb_ui_edit_genres import Ui_edit_genres_window  # Edit Genres Window
from mdb_ui_edit_media_types import Ui_edit_media_types_window  # Edit Media Types Window
from mdb_ui_entries_converter import Ui_Converter  # Convert Entries Window

# ----- Logging Configuration -----
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_formatter = logging.Formatter("%(asctime)s|%(name)s|%(levelname)s\n%(message)s\n")

log_handler = RotatingFileHandler("MDB log.log", maxBytes=10000, backupCount=1)
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(log_formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)

logger.addHandler(log_handler)
logger.addHandler(stream_handler)

__module_version__ = __version__ = "1.00"
__author__ = "Dominic Lee"


# noinspection PyBroadException
class MDB(QtWidgets.QMainWindow):
    """"""
    def __init__(self, database="Media-Database.db"):
        """
        Initialize the UI.
        :param database: Name of the database (defaults to 'Media-Database.db')
        """
        super(MDB, self).__init__()
        # ----- Connect to the database handler -----
        self.database = MDBHandler(database)
        self.database.create_tables()
        # ----- Create UI -----
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.load_media_types_and_genres()
        self.load_media_list()
        self.display_entry_count()
        # ----- Link Sub Windows -----
        self.edit_genres = MDBEditGenres(parent=self)
        self.edit_media_types = MDBEditMediaTypes(parent=self)
        self.entries_converter = MDBEntriesConverter(parent=self)
        # ----- Variables -----
        self.current_entry = None
        self.search_option = None
        # ----- Finally -----
        self.create_connections()

    # ---------- Database Methods ----------
    def add_entry(self):
        """
        Add the data from the UI input boxes to the database.
        Performs a check based on the title to see if an entry already exists
        and asks the user if they want to add the data anyway.
        """
        if self.ui.le_title.text() == "":
            QtWidgets.QMessageBox.critical(
                self,
                "No Title",
                "Minimum required information for an entry is a Title.",
                QtWidgets.QMessageBox.Ok)
        else:
            # If the entry doesn't exist just add it to the database.
            if not self.database.check_if_entry_exists("media", "title", self.ui.le_title.text()):
                self.database.add_entry(
                    title=self.ui.le_title.text(),
                    description=self.ui.te_description.toPlainText(),
                    age_rating=self.ui.le_age_rating.text(),
                    genre=self.ui.cb_genre.currentText(),
                    season=self.ui.sb_season.value(),
                    disc_count=self.ui.sb_disc_count.value(),
                    media_type=self.ui.cb_media_type.currentText(),
                    play_time=self.ui.sb_play_time.value(),
                    notes=self.ui.te_notes.toPlainText())
                self.clear_ui()
            else:
                # If an entry with the same title exists display message box.
                QtWidgets.QMessageBox.critical(
                    self, "Entry already exists!",
                    f"An entry with the title:\n{self.ui.le_title.text()}\nalready exists.\n",
                    QtWidgets.QMessageBox.Ok)

    def delete_entry(self):
        """Delete the currently selected entry from the database."""
        delete = QtWidgets.QMessageBox.question(
            self, "Delete entry?", f"Do you really want to delete '{self.current_entry[1]}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if delete == QtWidgets.QMessageBox.Yes:
            self.database.delete_entry(self.current_entry[0])
            self.clear_ui()

    def search(self):
        """Search the database and display the results in the media list."""
        try:
            # self.clear_ui()
            self.ui.lst_media_list.clear()
            logger.debug(
                f"MDB.search: query={self.ui.le_search_bar.text()} / column={self.search_option}")
            for result in self.database.search(
                    query=self.ui.le_search_bar.text(),
                    column=self.search_option):
                logger.debug(f"MDB.search: result={result[1]}")
                self.ui.lst_media_list.addItem(result[1])

        except Exception:
            logger.exception("Error in MDB.search")

    def update_entry(self):
        """
        Update the currently selected entry with
        the current contents of the UI input boxes.
        """
        try:
            self.database.update_entry(
                table="media",
                rowid=self.current_entry[0],
                title=self.ui.le_title.text(),
                description=self.ui.te_description.toPlainText(),
                age_rating=self.ui.le_age_rating.text(),
                genre=self.ui.cb_genre.currentText(),
                season=self.ui.sb_season.value(),
                disc_count=self.ui.sb_disc_count.value(),
                media_type=self.ui.cb_media_type.currentText(),
                play_time=self.ui.sb_play_time.value(),
                notes=self.ui.te_notes.toPlainText())
            self.clear_ui()
        except Exception:
            logger.exception("Error in MDB.update_entry")

    # ---------- UI Methods ----------
    def about(self):
        """
        Triggers a message box with basic app info.
        """
        QtWidgets.QMessageBox.information(
            self,
            f"About Media Database v{__version__}",
            f"Media Database v{__version__}\nCreated by {__author__}\n\n"
            f"Using PyQt5 for the gui and SQLite3 for the database.\n"
            f"Code available on GitHub for personal/educational purposes.\n\n"
            f"Have fun.\n",
            QtWidgets.QMessageBox.Ok)

    def clear_ui(self):
        """Clear the entry boxes/reset their values and reload the media list."""
        # ----- Variables -----
        self.current_entry = None
        # ----- Search Bar -----
        self.ui.le_search_bar.clear()
        self.ui.rb_all.setChecked(True)
        # ----- Media List -----
        self.ui.lst_media_list.clear()
        # ----- The Input Boxes -----
        self.ui.le_title.clear()
        self.ui.te_description.clear()
        self.ui.le_age_rating.clear()
        self.ui.cb_genre.setCurrentIndex(0)
        self.ui.sb_season.setValue(0)
        self.ui.sb_disc_count.setValue(1)
        self.ui.cb_media_type.setCurrentIndex(0)
        self.ui.sb_play_time.setValue(0)
        self.ui.te_notes.clear()
        # ----- The Entry Count -----
        self.ui.lbl_status.clear()
        # ----- Types and Genres Lists
        self.ui.cb_media_list_filter.clear()
        self.ui.cb_media_type.clear()
        self.ui.cb_genre.clear()
        self.load_media_types_and_genres()
        self.ui.cb_media_list_filter.setCurrentIndex(0)
        # ----- Other Bits -----
        self.ui.le_title.setFocus()
        self.display_entry_count()
        self.load_media_list()

    def closeEvent(self, event=None):
        """Overrides close event with custom quit message box."""
        choice = QtWidgets.QMessageBox.question(self, "Quit?", "Quit the program?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            self.database.close()   # Close connection to the cursor & database.
            event.accept()          # Quite the program.
        else:
            event.ignore()          # Don't quit the program.

    def create_connections(self):
        """
        Links PyQt signals with their corresponding method.
        """
        # ---------- Menu Connections ----------
        # File menu:
        self.ui.actionClear_UI.triggered.connect(self.clear_ui)
        self.ui.actionQuit.triggered.connect(self.close)
        # Data menu:
        self.ui.actionAdd_Entry.triggered.connect(self.add_entry)
        self.ui.actionDelete_Entry.triggered.connect(self.delete_entry)
        self.ui.actionUpdate_Entry.triggered.connect(self.update_entry)
        self.ui.actionEdit_Genres.triggered.connect(self.show_edit_genres)
        self.ui.actionConvert_Genres.triggered.connect(
            lambda: self.show_entries_converter(self.ui.actionConvert_Genres))
        self.ui.actionEdit_Media_Types.triggered.connect(self.show_edit_media_types)
        self.ui.actionConvert_Types.triggered.connect(
            lambda: self.show_entries_converter(self.ui.actionConvert_Types))
        # Help menu:
        self.ui.actionAbout.triggered.connect(self.about)
        # ---------- UI Element Connections ----------
        # Search Buttons:
        self.ui.btn_search.clicked.connect(self.search)
        self.ui.rb_all.toggled.connect(
            lambda: self.set_search_option(self.ui.rb_all))
        self.ui.rb_title.toggled.connect(
            lambda: self.set_search_option(self.ui.rb_title))
        self.ui.rb_description.toggled.connect(
            lambda: self.set_search_option(self.ui.rb_description))
        self.ui.rb_genre.toggled.connect(
            lambda: self.set_search_option(self.ui.rb_genre))
        self.ui.rb_notes.toggled.connect(
            lambda: self.set_search_option(self.ui.rb_notes))
        # Other UI Elements:
        self.ui.cb_media_list_filter.currentIndexChanged.connect(self.load_media_list)
        self.ui.lst_media_list.currentItemChanged.connect(self.display_info)

    def display_entry_count(self):
        """Sets the text in lbl_status."""
        try:
            self.ui.lbl_status.setText(self.database.count_entries())
        except Exception:
            logger.exception("Error in MDB.display_entry_count")

    def display_info(self):
        """Load the gui with info on the selected item from the media list."""
        # Get the currently selected items data from the database.
        if self.ui.lst_media_list.currentItem() is not None:
            logger.debug(f"MDB.display_info\n"
                         f"Current list item: {self.ui.lst_media_list.currentItem().text()}\n"
                         f"Current Entry is: {self.current_entry}")
            self.current_entry = self.database.select_one_entry(
                table="media",
                column="title",
                value=self.ui.lst_media_list.currentItem().text())
            logger.debug(f"MDB.display_info\n"
                         f"Set Current Entry to: "
                         f"{self.current_entry}/type:{type(self.current_entry)}")

            # Now display the information on the UI.
            self.ui.le_title.setText(self.current_entry[1])
            self.ui.te_description.setPlainText(self.current_entry[2])
            self.ui.le_age_rating.setText(self.current_entry[3])
            self.ui.cb_genre.setCurrentText(self.current_entry[4])
            self.ui.sb_season.setValue(self.current_entry[5])
            self.ui.sb_disc_count.setValue(self.current_entry[6])
            self.ui.cb_media_type.setCurrentText(self.current_entry[7])
            self.ui.sb_play_time.setValue(self.current_entry[8])
            self.ui.te_notes.setPlainText(self.current_entry[9])

    def load_media_types_and_genres(self):
        """
        Adds items to the GUIs combo boxes.
        The filter list only displays media types that are already used by entries
         in the database while the media types and genres are loaded from their
         own tables ready to be applied to new entries.
        """
        # A default option
        self.ui.cb_media_list_filter.addItem("Select Media Type")
        self.ui.cb_genre.addItem("Select Genre")
        self.ui.cb_media_type.addItem("Select Media Type")
        # e, t & g are tuples (db rows) and we need the first/only item in them.
        for e in self.database.return_distinct_entries(table="media", column="media_type"):
            # Add media type from media entries to the filter list.
            self.ui.cb_media_list_filter.addItem(e[0])
        for t in self.database.return_all_entries(table="media_types", column="type"):
            # Add media type to the types list.
            self.ui.cb_media_type.addItem(t[0])
        for g in self.database.return_all_entries(table="genres", column="genre"):
            # Add genre to the genre info list.
            self.ui.cb_genre.addItem(g[0])

    def load_media_list(self):
        """
        Populates the media list with the titles from the database
        or just the selected media type.
        """
        # Clear the list to avoid duplicate listings.
        self.ui.lst_media_list.clear()

        # Then repopulate the media list.
        if self.ui.cb_media_list_filter.currentIndex() != 0:
            logger.debug(f"Current Filter: {self.ui.cb_media_list_filter.currentText()}")
            # ----- Filtered Titles -----
            for title in self.database.filter_entries(
                    table="media",
                    column="media_type",
                    value=self.ui.cb_media_list_filter.currentText()):
                logger.debug(f"Adding '{title[1]}' to media list.")
                self.ui.lst_media_list.addItem(title[1])
        else:
            # ----- All Titles -----
            for title in self.database.return_all_entries():
                self.ui.lst_media_list.addItem(title[0])
        self.ui.lst_media_list.sortItems()

    def set_search_option(self, option):
        """"""
        # logger.debug(f"MDB.set_search_option: {option.text()}/value={self.search_option[option]}")
        values = {self.ui.rb_all: None,
                  self.ui.rb_title: "title",
                  self.ui.rb_description: "description",
                  self.ui.rb_genre: "genre",
                  self.ui.rb_notes: "notes"}
        self.search_option = values[option]
        logger.debug(f"MDB.search_option set to: {self.search_option}")

    def show_edit_genres(self):
        """Makes the Edit Genres window visible."""
        self.edit_genres.show()

    def show_edit_media_types(self):
        """Makes the Edit Media Types window visible."""
        self.edit_media_types.show()

    def show_entries_converter(self, sender):
        """
        Makes the Entries Converter window visible.
        The Entries Converter allows you to change all entries
        from one genre/media type to another.
        """
        self.entries_converter.clear_ui()
        if sender == self.ui.actionConvert_Genres:
            for old in self.database.return_distinct_entries(table="media", column="genre"):
                self.entries_converter.ui.cb_old_values.addItem(old[0])

            for new in self.database.return_distinct_entries(table="genres", column="genre"):
                self.entries_converter.ui.cb_new_values.addItem(new[0])

            self.entries_converter.column = "genre"

        if sender == self.ui.actionConvert_Types:
            for old in self.database.return_distinct_entries(table="media", column="media_type"):
                self.entries_converter.ui.cb_old_values.addItem(old[0])

            for new in self.database.return_distinct_entries(table="media_types", column="type"):
                self.entries_converter.ui.cb_new_values.addItem(new[0])

            self.entries_converter.column = "media_type"

        self.entries_converter.show()


# noinspection PyBroadException
class MDBEditGenres(QtWidgets.QMainWindow):
    """"""
    def __init__(self, database="Media-Database.db", parent=None):
        """Initialize the Edit Genres sub-window."""
        super(MDBEditGenres, self).__init__(parent)
        # ----- Connect to Database -----
        self.database = MDBHandler(database)
        # ----- Create UI -----
        self.ui = Ui_edit_genres_window()
        self.ui.setupUi(self)
        self.load_genres()
        self.clear_ui()
        self.ui.le_genre_name.setFocus()
        # ----- Signal Connections -----
        self.create_connections()
        # ----- Variables -----
        self.current_genre = None

    # ----- UI Methods -----
    def clear_ui(self):
        """Clear all the widgets and reload the genres list."""
        self.ui.lst_genres.clear()
        self.ui.le_genre_name.clear()
        self.ui.le_genre_name.setFocus()
        self.ui.te_genre_description.clear()
        self.ui.te_genre_examples.clear()

        self.load_genres()
        self.ui.lst_genres.clearSelection()
        self.current_genre = None
        self.ui.le_genre_name.setFocus()

    def closeEvent(self, event=None):
        """Override the close event and just hide the window."""
        self.hide()

    def create_connections(self):
        """Links PyQt signals with their corresponding method."""
        # self.ui.central_widget.keyPressEvent.connect()
        self.ui.lst_genres.currentItemChanged.connect(self.display_genre_info)
        self.ui.btn_add_genre.clicked.connect(self.add_genre)
        self.ui.btn_delete_genre.clicked.connect(self.delete_genre)
        self.ui.btn_update_genre.clicked.connect(self.update_genre)
        self.ui.btn_done.clicked.connect(self.closeEvent)
        self.ui.btn_clear.clicked.connect(self.clear_ui)

    def display_genre_info(self):
        """Load the gui with info on the selected item from the genre list."""
        if self.ui.lst_genres.currentItem() is not None:
            logger.debug(f"MDB.display_genre_info Current genre was: {self.current_genre}")
            self.current_genre = self.database.select_one_entry(
                table="genres",
                column="genre",
                value=self.ui.lst_genres.currentItem().text())
            logger.debug(f"MDB.display_genre_info Current genre set to: {self.current_genre}")

            self.ui.le_genre_name.setText(self.current_genre[1])
            self.ui.te_genre_description.setPlainText(self.current_genre[2])
            self.ui.te_genre_examples.setPlainText(self.current_genre[3])

    def load_genres(self):
        """Populate the listbox with all the genres in the database."""
        try:
            # Clear the list box to avoid duplicate listings
            self.ui.lst_genres.clear()
            # Now populate the list box with all the genres in the database
            for genre in self.database.return_all_entries(
                    table="genres", column="genre"):
                self.ui.lst_genres.addItem(genre[0])
        except Exception:
            logger.exception("Error in MDBEditGenres.load_genres")

    # ----- Database Methods -----
    def add_genre(self):
        """Add a genre to the database with data from the UI."""
        try:
            self.database.add_genre(
                genre=self.ui.le_genre_name.text(),
                description=self.ui.te_genre_description.toPlainText(),
                examples=self.ui.te_genre_examples.toPlainText())
            self.clear_ui()
            self.load_genres()
        except Exception:
            logger.exception("Error in MDBEditGenres.add_genres")

    def delete_genre(self):
        """
        Delete a genre from the database, the database handler
        will remove the genre from all entries too.
        """
        try:
            self.database.delete_genre(entry=self.current_genre)
            self.clear_ui()
        except Exception:
            logger.exception("Error in MDBEditGenres.delete_genres")

    def update_genre(self):
        """Update selected genres information with info from the UI."""
        try:
            if self.current_genre is None or self.ui.le_genre_name.text() == "":
                QtWidgets.QMessageBox.warning(
                    self,
                    "Update Error!",
                    "Unable to update.\nEither nothing is selected or the name box is empty.",
                    QtWidgets.QMessageBox.Ok)
            else:
                self.database.update_genre(
                    rowid=self.current_genre[0],
                    genre=self.ui.le_genre_name.text(),
                    description=self.ui.te_genre_description.toPlainText(),
                    examples=self.ui.te_genre_examples.toPlainText())
                self.clear_ui()
                self.load_media_types()
        except Exception:
            logger.exception("Error in MDBEditGenres.update_genre")


# noinspection PyBroadException
class MDBEditMediaTypes(QtWidgets.QMainWindow):
    """"""
    def __init__(self, database="Media-Database.db", parent=None):
        """Initialize the Edit Media Types sub-window."""
        super(MDBEditMediaTypes, self).__init__(parent)
        # ----- Connect to Database -----
        self.database = MDBHandler(database)
        # ----- Create UI -----
        self.ui = Ui_edit_media_types_window()
        self.ui.setupUi(self)
        self.load_media_types()
        self.clear_ui()
        self.ui.le_type_name.setFocus()
        # ----- Signal Connections -----
        self.create_connections()
        # ----- Variables -----
        self.current_media_type = None

    # ----- UI Methods -----
    def clear_ui(self):
        """Clear all the widgets and reload the media types list."""
        self.ui.lst_media_types.clear()
        self.ui.le_type_name.clear()
        self.ui.le_type_name.setFocus()
        self.load_media_types()
        self.current_media_type = None

    def closeEvent(self, event=None):
        """Override the close event and just hide the window."""
        self.hide()

    def create_connections(self):
        """Links PyQt signals with their corresponding method."""
        self.ui.lst_media_types.currentItemChanged.connect(self.display_type_info)
        self.ui.btn_add_type.clicked.connect(self.add_media_type)
        self.ui.btn_delete_type.clicked.connect(self.delete_media_type)
        self.ui.btn_update_type.clicked.connect(self.update_media_type)
        self.ui.btn_clear.clicked.connect(self.clear_ui)
        self.ui.btn_done.clicked.connect(self.closeEvent)

    def display_type_info(self):
        """
        Load the gui with info on the selected item from
        the media types list.
        """
        if self.ui.lst_media_types.currentItem() is not None:
            logger.debug(f"MDBEditMediaTypes.display_type_info "
                         f"Current type was: {self.current_media_type}")
            self.current_media_type = self.database.select_one_entry(
                table="media_types",
                column="type",
                value=self.ui.lst_media_types.currentItem().text())
            logger.debug(f"MDBEditMediaTypes.display_type_info "
                         f"Current type set to: {self.current_media_type}")
            self.ui.le_type_name.setText(self.current_media_type[1])

    def load_media_types(self):
        """
        Populate the listbox with all the media types
        in the database.
        """
        try:
            # Clear the list box to avoid duplicate listings
            self.ui.lst_media_types.clear()
            # Now populate the list box with all the genres in the database
            for genre in self.database.return_all_entries(
                    table="media_types", column="type"):
                self.ui.lst_media_types.addItem(genre[0])
        except Exception:
            logger.exception("Error in MDBEditGenres.load_media_types")

    # ----- Database Methods -----
    def add_media_type(self):
        """Add a media type to the database with data from the UI."""
        try:
            self.database.add_media_type(media_type=self.ui.le_type_name.text())
            self.clear_ui()
            self.load_media_types()
        except Exception:
            logger.exception("Error in MDBEditMediaTypes.add_media_type")

    def delete_media_type(self):
        """
        Delete a media type from the database,
        the database handler will remove the media type
        from all entries too.
        """
        try:
            if self.current_media_type is None:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Nothing selected",
                    "Unable to deleted as nothing is selected.",
                    QtWidgets.QMessageBox.Ok)
            else:
                self.database.delete_media_type(entry=self.current_media_type)
                self.clear_ui()
                self.load_media_types()
        except Exception:
            logger.exception("Error in MDBEditMediaTypes.delete_media_type")

    def update_media_type(self):
        """Update selected media type information with info from the UI."""
        try:
            if self.current_media_type is None or self.ui.le_type_name.text() == "":
                QtWidgets.QMessageBox.warning(
                    self,
                    "Nothing selected",
                    "Unable to update.\nEither nothing is selected or the name box is empty.",
                    QtWidgets.QMessageBox.Ok)
            else:
                self.database.update_media_type(
                    rowid=self.current_media_type[0],
                    media_type=self.ui.le_type_name.text())
                self.clear_ui()
                self.load_media_types()
        except Exception:
            logger.exception("Error in MDBEditMediaTypes.update_media_types")


# noinspection PyBroadException
class MDBEntriesConverter(QtWidgets.QMainWindow):
    """"""
    def __init__(self, database="Media-Database.db", parent=None):
        """Initialize the Entries Converter sub-window."""
        super(MDBEntriesConverter, self).__init__(parent)
        self.ui = Ui_Converter()
        self.ui.setupUi(self)
        self.create_connections()
        self.database = MDBHandler(database)
        self.column = None

    def clear_ui(self):
        """Clear all the widgets."""
        self.ui.cb_old_values.clear()
        self.ui.cb_new_values.clear()

    def closeEvent(self, event=None):
        """
        Override the close event to clear the widgets
        and hide the window.
        """
        self.clear_ui()
        self.hide()

    def convert_entries(self):
        """
        Display a message box to confirm the change and then
        pass the values from the combo boxes to the database handler
        to convert the selected entries.
        """
        try:
            choice = QtWidgets.QMessageBox.information(
                self,
                f"Convert all entries with {self.ui.cb_old_values.currentText()}",
                f"All entries of '{self.ui.cb_old_values.currentText()}' "
                f"will be swapped to '{self.ui.cb_new_values.currentText()}'.\n\nConfirm?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                logger.debug(f"Attempting to convert "
                             f"'{self.ui.cb_old_values.currentText()}' to "
                             f"'{self.ui.cb_new_values.currentText()}'")
                self.database.convert_entries(
                    column=self.column,
                    old_value=self.ui.cb_old_values.currentText(),
                    new_value=self.ui.cb_new_values.currentText())
                self.closeEvent()
        except Exception:
            logger.exception("Error in MDBEntriesConverter.convert_entries")

    def create_connections(self):
        """Links PyQt signals with their corresponding method."""
        self.ui.btn_ok.clicked.connect(self.convert_entries)
        self.ui.btn_cancel.clicked.connect(self.closeEvent)


def main():
    """Setup and display the application when run."""
    app = QtWidgets.QApplication(sys.argv)
    window = MDB()
    window.show()
    sys.exit(app.exec_())


def exception_hook(cls, exception, traceback):
    """Used to display traceback for errors with Qt."""
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    sys.excepthook = exception_hook
    main()
