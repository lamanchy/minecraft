import os
import re
import smtplib
import subprocess
import time
from email.mime.text import MIMEText

SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]
EMAIL_TO = [os.environ.get("EMAIL_TO", SMTP_USER), "marketa.tumova28@gmail.com"]
LOG_FILE = os.environ.get("LOG_FILE", "/data/logs/latest.log")

JOIN_PATTERN = re.compile(r"\[Server thread/INFO\].*?: (.+) joined the game")
LEAVE_PATTERN = re.compile(r"\[Server thread/INFO\].*?: (.+) left the game")


def send_email(player: str, joined: bool):
    action = "joined" if joined else "left"
    msg = MIMEText(f"{player} {action} the Minecraft server.")
    msg["Subject"] = f"Minecraft: {player} {action}"
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(EMAIL_TO)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg, to_addrs=EMAIL_TO)

    print(f"Email sent: {player} {action}", flush=True)


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
        join_match = JOIN_PATTERN.search(line)
        leave_match = LEAVE_PATTERN.search(line)
        if join_match:
            player = join_match.group(1)
            try:
                send_email(player, joined=True)
            except Exception as e:
                print(f"Failed to send email: {e}", flush=True)
        elif leave_match:
            player = leave_match.group(1)
            try:
                send_email(player, joined=False)
            except Exception as e:
                print(f"Failed to send email: {e}", flush=True)


if __name__ == "__main__":
    watch()
