import argparse
from sys import exit, argv
from socket import socket
from pickle import load, dump
from PyQt6.QtWidgets import QApplication, QLineEdit, QPushButton, QListWidget, QMainWindow, QWidget, QLabel, QGridLayout, QErrorMessage
from dialog import FW_FONT, FixedWidthMessageDialog

# initializes window
class MyWindow(QMainWindow):
    """
    class for GUI window that is created when client is run
    """
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port

        # Create a central widget and set it as the main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QGridLayout()
        central_widget.setLayout(self.layout)

        # Create QLineEdit widgets
        all_labels = ("Label", "Classifier", "Agent", "Date")
        self.l = QLabel("Label")
        self.label = QLineEdit()
        self.c = QLabel("Classifier")
        self.classifier = QLineEdit()
        self.a = QLabel("Agent")
        self.agent = QLineEdit()
        self.d = QLabel("Date")
        self.date = QLineEdit()
        # specify which columns
        self.layout.addWidget(self.l)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.c)
        self.layout.addWidget(self.classifier)
        self.layout.addWidget(self.a)
        self.layout.addWidget(self.agent)
        self.layout.addWidget(self.d)
        self.layout.addWidget(self.date)

        self.submit_button = QPushButton('Submit')
        self.layout.addWidget(self.submit_button)

        self.submit_button.clicked.connect(self.handle_submit_or_enter)

        # Connect the returnPressed signal to a custom slot
        self.label.returnPressed.connect(self.handle_submit_or_enter)
        self.classifier.returnPressed.connect(self.handle_submit_or_enter)
        self.agent.returnPressed.connect(self.handle_submit_or_enter)
        self.date.returnPressed.connect(self.handle_submit_or_enter)

        # Create a variable to store the table info
        self.table_info = QListWidget()
        self.table_info.setFont(FW_FONT)
        self.table_info.itemClicked.connect(self.handle_object_click)
        self.layout.addWidget(self.table_info)

    def handle_submit_or_enter(self):
        """
        This method will be called when the Enter key is pressed or submit button is pressed
        """
        try:
            with socket() as sock:
                try:
                    int_port = int(self.port)
                except sock.error as e:
                    exit(1)

                try:
                    sock.connect((self.host, int_port))

                except Exception as e:
                    # Handle the connection error gracefully
                    error_message = QErrorMessage()
                    print(error_message)
                    print("continue executing")
                    return

                filters_list = [self.label.text(), self.classifier.text(),
                                self.agent.text(), self.date.text()]
                flo_out = sock.makefile(mode = 'wb')
                dump(filters_list, flo_out) # put in the filters to server
                flo_out.flush()

                flo_in = sock.makefile(mode = 'rb')
                # print("unpickling data from server")
                results = load(flo_in) # getting data back from server
                # display results from query in GUI
                # print(results)
                self.update_gui_with_results(results)

        except Exception as e:
            print(f"Error: {e}")
            results = None

    def update_gui_with_results(self, results):
        """"""
        print(results)
        self.table_info.clear()  # Clear the previous results
        self.table_info.addItems(str(results).split('\n'))

    def handle_object_click(self):
        # Define your callback function
        row = self.table_info.currentItem()
        # print(f"Item (entire row) selected: {row.text()}")
        # print(type(row.text()))
        print(row.text())
        if row is None:
            return
        with socket() as sock:
            try:
                int_port = int(self.port)
            except ValueError:
                exit(1)

            sock.connect((self.host, int_port))
            object_id = row.text().split()
            # print(object_id)
            object_id = object_id[0]
            # print(object_id)
            flo_out = sock.makefile(mode = 'wb')
            dump([object_id], flo_out) # put in the filters to server
            flo_out.flush()
            flo_in = sock.makefile(mode = 'rb')
            # return results
            results = load(flo_in) # getting data back from server
            print(results)
            # display results from query in GUI
            info = FixedWidthMessageDialog("Object Details", results, parent=self)
            info.exec()

def run_argparse():
    parser = argparse.ArgumentParser(prog='lux.py', allow_abbrev=False,
                                         description='Client for the YUAG application')
    parser.add_argument('host', help='the host on which the server is running')
    parser.add_argument('port', help='the port at which the server is listening')
    args = parser.parse_args()
    return args

def help_arg():
    print("usage: lux.py [-h] host port")
    print()
    print("Client for the YUAG application")
    print()
    print("positional arguments:")
    print("  host        The host on which the server is running")
    print("  port        The port at which the server is listening")
    print()
    print("optional arguments:")
    print("  -h, --help  show this help message and exit")
    exit(0)

def main():
    """
    creates gui and communicates with server

    """
    # Check for the -h or --help argument
    if len(argv) == 2 and (argv[1] == '-h' or argv[1] == '--help'):
        help_arg()

    # Checks for incorrect arguments
    if len(argv) != 3:
        print('Usage: python %s host port' % argv[0])
        exit(1)

    # Check's for non-integer argument port
    try:
        int(argv[2])
    except ValueError:
        exit(1)

    filters = run_argparse()
    app = QApplication(argv)
    screen_size = app.primaryScreen().availableGeometry()
    window = MyWindow(filters.host, filters.port)
    window.resize(screen_size.width()//2, screen_size.height()//2)
    window.setWindowTitle('Lux') # names window
    window.show()
    exit(app.exec())

if __name__ == '__main__':
    main()