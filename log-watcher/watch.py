import os
import re
import smtplib
import subprocess
import time
from email.mime.text import MIMEText

SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]
EMAIL_TO = os.environ.get("EMAIL_TO", SMTP_USER)
LOG_FILE = os.environ.get("LOG_FILE", "/data/logs/latest.log")

JOIN_PATTERN = re.compile(r"\[Server thread/INFO\].*?: (.+) joined the game")


def send_email(player: str):
    msg = MIMEText(f"{player} joined the Minecraft server.")
    msg["Subject"] = f"Minecraft: {player} joined"
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_TO

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print(f"Email sent: {player} joined", flush=True)


def watch():
    # Wait for the log file to exist
    while not os.path.exists(LOG_FILE):
        print(f"Waiting for {LOG_FILE}...", flush=True)
        time.sleep(5)

    print(f"Watching {LOG_FILE}", flush=True)

    # Use tail -F to follow the log file even through rotations
    proc = subprocess.Popen(
        ["tail", "-n", "0", "-F", LOG_FILE],
        stdout=subprocess.PIPE,
        text=True,
    )

    for line in proc.stdout:
        match = JOIN_PATTERN.search(line)
        if match:
            player = match.group(1)
            try:
                send_email(player)
            except Exception as e:
                print(f"Failed to send email: {e}", flush=True)


if __name__ == "__main__":
    watch()
