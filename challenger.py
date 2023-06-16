import time
import subprocess
import simplejson as json
import os
import sys
import requests
import sv_ttk

from pynput.keyboard import Key, Controller
from base64 import b64encode
from tkinter import *
from tkinter import ttk
from modules import leaguefunctions


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

root = Tk()
root.title("Challenger")
root.geometry("750x500")
iconPath = resource_path("challenger.ico")
root.iconbitmap(iconPath)

# FUNCTIONS

def render_accounts():
    if os.path.exists("accounts.json"):
        with open('accounts.json', 'r') as f:
            data = json.load(f)

            for account in data:
                # Render username and password side by side
                Label(second_frame, text=account['username']).grid(row=data.index(account)+10, column=0)

                if len(account) > 3:
                    Label(second_frame, text=account['nickname']).grid(row=data.index(account)+10, column=1)
                    Label(second_frame, text=account['level']).grid(row=data.index(account)+10, column=2)
                    Label(second_frame, text=account['rank']).grid(row=data.index(account)+10, column=3)
                    Label(second_frame, text=account['lp']).grid(row=data.index(account)+10, column=4)
                    Label(second_frame, text=account['wins']).grid(row=data.index(account)+10, column=5)
                    Label(second_frame, text=account['losses']).grid(row=data.index(account)+10, column=6)
                    Label(second_frame, text=account['winrate']).grid(row=data.index(account)+10, column=7)
                    Label(second_frame, text=account['be']).grid(row=data.index(account)+10, column=8)
                    Label(second_frame, text=account['rp']).grid(row=data.index(account)+10, column=9)

                # Add a button to login
                Button(second_frame, text="Login", command=lambda id=account['id']: open_client_and_login(id)).grid(padx = 10, pady = 10, row=data.index(account)+10, column=11)

                # Add a button to edit
                Button(second_frame, text="Edit", command=lambda id=account['id']: edit_window(id)).grid(padx = 10, pady = 10, row=data.index(account)+10, column=12)

                # Fix render bug
                Label(second_frame, text="").grid(row=data.index(account)+12, column=0)


def edit_account(id: int, new_user: str, new_pass: str) -> None:
    
    with open("accounts.json", "r") as accounts_file:
        accounts = json.load(accounts_file)
        for account in accounts:
            if account["id"] == id:
                account["username"] = new_user
                account["password"] = new_pass
    
    with open("accounts.json", "w") as accounts_file:
        json.dump(accounts, accounts_file, indent=4)
    
    # Update the buttons
    render_accounts()

def edit_window(id: int):
    editWindow = Toplevel(root)
    editWindow.title("Edit Account")

    editLabel = Label(editWindow, text="Edit Account", padx= 10, pady=10)
    editLabel.grid(row=0, column=0, columnspan=2)

    editEntryUsernameLabel = Label(editWindow, text="Username:", padx=10, pady=10)
    editEntryUsernameLabel.grid(row=1, column=0)

    editEntryUsername = Entry(editWindow)
    editEntryUsername.grid(row=1, column=1)

    editEntryPasswordLabel = Label(editWindow, text="Password:", padx=10, pady=10)
    editEntryPasswordLabel.grid(row=2, column=0)

    editEntryPassword = Entry(editWindow)
    editEntryPassword.grid(row=2, column=1)
    
    editButton = Button(editWindow, text="Confirm", command=lambda: edit_account(id, editEntryUsername.get(), editEntryPassword.get()))
    editButton.grid(row=3, column=0)

    cancelButton = Button(editWindow, text="Cancel")
    cancelButton.grid(row=3, column=1)

def open_client_and_login(id):
    print(f"Opening client for account ID: {id}")
    with open("accounts.json", "r") as accounts_file:
        accounts = json.load(accounts_file)
        for account in accounts:
            if account["id"] == id:
                username = account["username"]
                password = account["password"]
                subprocess.Popen(f"C:\Riot Games\Riot Client\RiotClientServices.exe --launch-product=league_of_legends --launch-patchline=live --allow_multiple_clients")
                time.sleep(5)
                keyboard = Controller()
                keyboard.type(username)
                keyboard.press(Key.tab)
                keyboard.release(Key.tab)
                keyboard.type(password)
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)

    is_signed_in = leaguefunctions.is_signed_in()

    if is_signed_in == 200:
        update_json_data(id)  

    
def update_json_data(id):

    # Get the summoner name
    summoner_name, summoner_level = leaguefunctions.get_summoner_data()
    summoner_rank, summoner_lp, summoner_wins, summoner_losses, summoner_winrate = leaguefunctions.get_ranked_info()
    summoner_be, summoner_rp = leaguefunctions.get_currencies()

    if os.path.exists("accounts.json"):
        with open("accounts.json", "r") as accounts_file:
            accounts = json.load(accounts_file)
            for account in accounts:
                if account["id"] == id:
                    account["nickname"] = summoner_name
                    account["level"] = summoner_level
                    account["rank"] = summoner_rank
                    account["lp"] = summoner_lp
                    account["wins"] = summoner_wins
                    account["losses"] = summoner_losses
                    account["winrate"] = summoner_winrate
                    account["rp"] = summoner_rp
                    account["be"] = summoner_be
                    
        with open("accounts.json", "w") as accounts_file:
            json.dump(accounts, accounts_file, indent=4)

    render_accounts()


def add_account():
    username = username_entry.get()
    password = password_entry.get()

    account = {
        "id": 0, 
        "username": username,
        "password": password,
    }

    if username == "" or password == "":
        return
    
    # Autoincrement id
    account["id"] = highest_id() + 1

    if os.path.exists("accounts.json"):
        with open("accounts.json", "r") as accounts_file:
            accounts = json.load(accounts_file)
            accounts.append(account)
        with open("accounts.json", "w") as accounts_file:
            json.dump(accounts, accounts_file, indent=4)
    else:
        with open("accounts.json", "w") as accounts_file:
            json.dump([account], accounts_file, indent=4)
    
    # Clear the text inputs
    username_entry.delete(0, END)
    password_entry.delete(0, END)

    #Render the new account
    render_accounts()

def highest_id():
    if os.path.exists("accounts.json"):
        with open("accounts.json", "r") as accounts_file:
            accounts = json.load(accounts_file)
            highest_id = 0
            for account in accounts:
                if account["id"] > highest_id:
                    highest_id = account["id"]
            return highest_id
    else:
        with open("accounts.json", "w") as accounts_file:
            json.dump([], accounts_file)
            accounts_file.close()
            return 0


# Creating the main frame

main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=1)

# Creating a canvas

my_canvas = Canvas(main_frame)
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# Adding the scrollbar

my_scrollbar_y = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)

# Configuring the canvas

my_canvas.configure(yscrollcommand=my_scrollbar_y.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion = my_canvas.bbox("all")))

# Creating another frame inside the canvas

second_frame = Frame(my_canvas)

# Adding that new frame to a window in the canvas

my_canvas.create_window((0,0), window=second_frame, anchor="nw")

# Adding the scrollbar to the right side of the window

my_scrollbar_y.pack(side=RIGHT, fill=Y)

# Adding labels and entries to add new accounts

Label(second_frame, text="Username").grid(row=0, column=0, padx=10, pady=10)
Label(second_frame, text="Password").grid(row=1, column=0, padx=10, pady=10)

username_entry = Entry(second_frame)
password_entry = Entry(second_frame, show="*")

username_entry.grid(row=0, column=1)
password_entry.grid(row=1, column=1)

Button(second_frame, text="Add account", command=add_account).grid(padx=10, pady=10, row=2, column=0, columnspan=2)

Label(second_frame, text="Username").grid(row=9, column=0, padx=5)
Label(second_frame, text="Nickname").grid(row=9, column=1, padx=5)
Label(second_frame, text="Level").grid(row=9, column=2, padx=5)
Label(second_frame, text="Division").grid(row=9, column=3, padx=5)
Label(second_frame, text="LP").grid(row=9, column=4, padx=5)
Label(second_frame, text="Wins").grid(row=9, column=5, padx=5)
Label(second_frame, text="Losses").grid(row=9, column=6, padx=5)
Label(second_frame, text="Winrate").grid(row=9, column=7, padx=5)
Label(second_frame, text="BE").grid(row=9, column=8, padx=5)
Label(second_frame, text="RP").grid(row=9, column=9, padx=5)

sv_ttk.set_theme("dark")

render_accounts()

root.mainloop()
