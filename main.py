import requests
import json
import os
import threading
import queue
import customtkinter
import decor
import time
import csv
import datetime
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog

MAX_THREAD = 5
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")


#thx stack overflow
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

def getRequest(name):
    global done
    url_yield = f'https://api.nasdaq.com/api/quote/{name}/summary?assetclass=stocks'
    url_earnings = f'https://api.nasdaq.com/api/analyst/{name}/earnings-date'
    # start = time.perf_counter()
    response = requests.get(url_yield, headers=headers).json()
    # end = time.perf_counter()
    # run_time = end-start
    # print(f"Ping - {run_time:.4f} secs")
    try:
        curr_yield = response["data"]["summaryData"]["Yield"]["value"]
    except:
        print(f"{name} NOT EXIST!")
        done+=1
        return
    response = requests.get(url_earnings, headers=headers).json()
    split = response["data"]["announcement"].split(":")
    if(split[1] == ' '):
        split = "N/A"
    else:
        split = split[1]
    # print(name, split, curr_yield)
    out_csv.writerow([name, split, curr_yield])
    done += 1

def worker():
    while not q.empty():
        name = q.get()
        getRequest(name)
        print(float(done)/float(total))
        progress_bar.set(float(done)/float(total))
    return

def thread():
    thread_list = []
    for t in range(MAX_THREAD):
        thread = threading.Thread(target=worker)
        thread_list.append(thread)
    
    for thread in thread_list:
        thread.start()
    
    for thread in thread_list:
        thread.join()
    return

def editJson():
    return

@decor.timer
def run_me():
    # global MAX_THREAD
    global q, out_csv, progress_bar, out_button, done, total, out_csv_fp
    q = queue.Queue()
    out_csv_fp = f"{os.path.dirname(os.path.realpath(__file__))}/output/{datetime.date.today()}.csv"
    out_csv_open_file = open(out_csv_fp, "+w")
    out_csv = csv.writer(out_csv_open_file)
    out_csv.writerow(["Code", "Date", "Yield"])
    json_fp = open(f"{os.path.dirname(os.path.realpath(__file__))}/nasdaq.json")
    json_file = json.load(json_fp)
    names = json_file["data"] 
    # MAX_THREAD = names.__len__()
    done = 0
    total = names.__len__()
    for curr_name in names:
        q.put(str(curr_name))
    
    thread()
    out_button.grid(column=0, row=3, padx=10, pady=12, columnspan=3)
    out_path.configure(text=f"{out_csv_fp}")
    out_path.update()
    out_csv_open_file.close()
    return

def script_thread():
    thread = threading.Thread(target=run_me)
    thread.start()

def open_file_menu():
    global root
    global out_path
    # root = tkinter.Tk()
    tempPath = str(out_csv_fp)
    head, tail = os.path.split(str(tempPath))
    file = filedialog.askopenfilename(initialdir=head)
    return os.startfile(file)
    

def scriptGui(root):
    global out_button
    global progress_bar
    global out_path

    page = customtkinter.CTkFrame(root)
    greeting = customtkinter.CTkLabel(page, text="Temp Text", font=("Roboto", 18))
    start_button = customtkinter.CTkButton(page, text="Start", font=("Roboto", 12), command=script_thread)
    progress_bar = customtkinter.CTkProgressBar(page, width=300)
    out_path = customtkinter.CTkLabel(page, text="", font=("Roboto", 12))
    out_button = customtkinter.CTkButton(page, text="Open", font=("Roboto", 12), command=open_file_menu)

    progress_bar.set(0)

    page.grid(column=0, row=0, padx=60, pady=20)
    greeting.grid(column=0, row=0, columnspan=3, padx=10, pady=12)

    start_button.grid(column=0, row=1, padx=10, pady=12, columnspan=3)
    progress_bar.grid(column=0, row=2, padx=10, pady=12, columnspan=2)
    out_path.grid(column=0, row=4, columnspan=3)
    out_button.grid_remove()

def on_quit():
    global root
    msg = CTkMessagebox(title="Quit?", message="Do you wnat to quit the program?", icon="question", option_1="No", option_2="Yes")
    response = msg.get()
    if response == "Yes":
        root.destroy()
    else:
        return

def main():
    global root
    root = customtkinter.CTk()
    root.title("Derek Prog")
    scriptGui(root)
    root.protocol("WM_DELETE_WINDOW", on_quit)
    root.mainloop()

if __name__ == "__main__":
    main()