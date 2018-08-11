from tempfile import mkstemp
from shutil import move
from os import fdopen
from subprocess import call
import os


def replace_in_file(file_path, pattern, subst, replace="../config/.save_database.py"):
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    move(file_path, replace)
    move(abs_path, file_path)


if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    replace_in_file("../config/database.py", "URI_USED = URI_SQLITE", "URI_USED = URI_TESTING")
    call(["python",
          "-m",
          "unittest",
          "account.py",
          "circle.py",
          "circle_logic.py",
          "conversation.py",
          "conversation_logic.py",
          "device.py",
          "device_message.py",
          "device_message_logic.py",
          "media.py",
          "media_logic.py",
          "message.py",
          "message_logic.py",
          "payment.py",
          "socketio_auth.py",
          "socketio_message.py",
          "socketio_notif.py",
          "socketio_rooms.py",
          "-v"
          ])
    replace_in_file("../config/database.py", "URI_USED = URI_TESTING", "URI_USED = URI_SQLITE")