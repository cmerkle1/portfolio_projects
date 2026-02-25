import socket
import time
import sys
import os

# usage: python wait_for_db.py <host> <port> <command_to_run...>

if len(sys.argv) < 3:
    print("Error: you must provide host and port")
    sys.exit(1)

host = sys.argv[1]
port = int(sys.argv[2])
# The rest of the arguments are the command we want to run after DB is up
cmd = sys.argv[3:]

print(f"Checking database connection at {host}:{port}...")

while True:
    try:
        # Try to open a connection
        with socket.create_connection((host, port), timeout=1):
            print("Database is up! Starting the web server...")
            break
    except (OSError, ConnectionRefusedError):
        print("Database unavailable, sleeping 1s...")
        time.sleep(1)

# Execute the original command (manage.py runserver)
if cmd:
    os.execvp(cmd[0], cmd)