from tempfile import mkstemp
from shutil import move
from os import fdopen
from subprocess import call
import os


def replace_in_file(file_path, pattern, subst, replace="config/.save_database.py"):
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    move(file_path, replace)
    move(abs_path, file_path)


def run_all():
    call(["python",
          "-m",
          "unittest",
          "test/rest_basic/test_account.py",
          "test/rest_basic/test_circle.py",
          "test/rest_basic/test_circle_logic.py",
          "test/rest_basic/test_conversation.py",
          "test/rest_basic/test_conversation_logic.py",
          "test/rest_basic/test_device.py",
          "test/rest_basic/test_device_message_logic.py",
          "test/rest_basic/test_media.py",
          "test/rest_basic/test_media_logic.py",
          "test/rest_basic/test_message.py",
          "test/rest_basic/test_message_logic.py",
          "test/rest_basic/test_payment.py",
          "test/socket_basic/test_authentication.py",
          "test/socket_basic/test_messages.py",
          "test/socket_basic/test_notifications.py",
          "test/socket_basic/test_rooms.py",
          "-v"
          ])


if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    os.chdir("..")
    replace_in_file("config/database.py", "URI_USED = URI_SQLITE", "URI_USED = URI_TESTING")
    run_all()
    replace_in_file("config/database.py", "URI_USED = URI_TESTING", "URI_USED = URI_SQLITE")
