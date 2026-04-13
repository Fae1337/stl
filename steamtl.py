import tkinter as tk
import win32crypt
import binascii
import zlib
import jwt
import os
import shutil
import time
import subprocess
from tkinter.messagebox import showerror, showwarning, showinfo

def get_clipboard(root):
    cp = root.clipboard_get()
    return cp

class TokenLogin:
    def __init__(self):
        self.pc_name = os.environ['USERNAME']
        self.cfg_path = "C:/Program Files (x86)/Steam/config"
        self.local_path = f"C:/Users/{self.pc_name}/AppData/Local/Steam/local.vdf"
    
    def _decode_token(self, token):
        decoded = jwt.decode(token, options={'verify_signature': False})
        steam_id = str(decoded.get('sub'))
        pseudo_login = f'user_{steam_id[-6:]}'

        encrypted = win32crypt.CryptProtectData(token.encode('utf-8'), None, pseudo_login.encode('utf-8'), None, None, 0)
        hex_token = binascii.hexlify(encrypted).decode('ascii')
        key = hex(zlib.crc32(pseudo_login.encode('utf-8')))[2:] + '1'

        return (
            steam_id,
            pseudo_login,
            hex_token,
            key,
        )

    def _add_profile_title(self, steamid, account_name):
        text = f"""\"users\"
        {{
            "{steamid}"
            {{
                "AccountName"		"{account_name}"
                "PersonaName"		"Dayn"
                "RememberPassword"		"1"
                "WantsOfflineMode"		"0"
                "SkipOfflineModeWarning"		"0"
                "AllowAutoLogin"		"0"
                "MostRecent"		"1"
                "Timestamp"		"{int(time.time())}"
            }}
        }}
        """
        text2 = f"""\"InstallConfigStore\"
        {{
            "Software"
            {{
                "Valve"
                {{
                    "Steam"
                    {{
                        "Accounts"
                        {{
                            "{account_name}"
                            {{
                                "SteamID"		"{steamid}"
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        try:
            with open("C:/Program Files (x86)/Steam/config/loginusers.vdf", "w", encoding="utf-8") as login_user:
                login_user.write(text)
            with open("C:/Program Files (x86)/Steam/config/config.vdf", "w", encoding="utf-8") as config_vdf:
                config_vdf.write(text2)
            return True
        except Exception as e:
            showerror(title="Error", message=e)
            return False
    
    def token_write(self, crc32_key, token):
        text = f"""\"MachineUserConfigStore\"
        {{
            "Software"
            {{
                "Valve"
                {{
                    "Steam"
                    {{
                        "ConnectCache"
                        {{
                            "{crc32_key}"        "{token}"
                        }}
                    }}
                }}
            }}
        }}
        """
        try:
            with open(f"C:/Users/{self.pc_name}/AppData/Local/Steam/local.vdf", "w", encoding="utf-8") as local_vdf:
                local_vdf.write(text)
            return True
        except Exception as e:
            showerror(title="Error", message=e)
            return False
        
    def clear_steam(self):
        try:
            if os.path.exists(self.cfg_path):
                shutil.rmtree(self.cfg_path)

            os.makedirs(self.cfg_path)

            if os.path.exists(self.local_path):
                os.remove(self.local_path)

            subprocess.run('taskkill /f /im steam.exe', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run('taskkill /f /im steamwebhelper.exe', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            return True
        except Exception as e:
            showerror(title="Error", message=e)
            return False


    def SteamMain(self, token):
        if not self.clear_steam():
            return

        if len(token) < 400:
            showerror(title="Error", message="Invalid copied token")
            return
            
        token = token.replace("EyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0", "eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0")
        steam_id, pseudo_login, hex_token, key = self._decode_token(token)

        if not self._add_profile_title(steam_id, pseudo_login):
            return

        if not self.token_write(key, hex_token):
            return

        time.sleep(2)
        steam_exe_path = r"C:\Program Files (x86)\Steam\steam.exe"
        subprocess.Popen(steam_exe_path)

        showinfo(title="Good", message="Account added successfully")

class Gui:
    def __init__(self):
        main = TokenLogin()

        root = tk.Tk()
        root.title("Stl")
        root.geometry("250x70")
        
        root.resizable(False, False)
        root.configure(bg="gray")

        frame = tk.Frame(root, padx=10, pady=20, bg="gray")
        frame.pack(fill="both", expand=True)

        btn_add = tk.Button(frame, text="Add Account", width=14,command=lambda: main.SteamMain(get_clipboard(root)))
        btn_add.pack(side="left", padx=5)

        btn_clear = tk.Button(frame, text="Clear Steam", width=14,command=lambda: main.clear_steam())
        btn_clear.pack(side="left", padx=5)

        root.mainloop()

if __name__ == "__main__":
    app = Gui()