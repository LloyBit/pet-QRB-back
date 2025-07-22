import subprocess

s1 = subprocess.Popen(["python", "backend/app/main.py"])
s2 = subprocess.Popen(["python", "frontend/bot/bot.py"])


s1.wait()
s2.wait()
