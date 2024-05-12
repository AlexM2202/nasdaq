import requests
import json
import os
import threading
import queue
import customtkinter
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

def run_me():
    # global MAX_THREAD
    global q, out_csv, progress_bar, out_button, done, total, out_csv_fp
    q = queue.Queue()
    out_csv_fp = f"{os.path.dirname(os.path.dirname(os.path.realpath(__file__)))}/output/{datetime.date.today()}.csv"
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
    out_button.grid(column=0, row=4, padx=10, pady=12, columnspan=3)
    out_path.configure(text=f"{out_csv_fp}")
    out_path.update()
    json_fp.close()
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

def get_add_input():
    dialog = customtkinter.CTkInputDialog(text="Type in a symbol:", title="Add Symbol")
    text = dialog.get_input().upper()
    if text in names:
        CTkMessagebox(title="Symbol Exists!", message=f"{text} symbol already is stored in the program!", icon="cancel")
        return
    curr_box = customtkinter.CTkCheckBox(scroll_box, text=text)
    check_boxs.append(curr_box)
    curr_box.grid(column=0, row=len(check_boxs)-1, padx=5, pady=6)
    json_fp = open(f"{os.path.dirname(os.path.realpath(__file__))}/nasdaq.json", "+w")
    names.append(text)
    names.sort()
    json.dump({"data": names}, json_fp, indent=4)
    json_fp.close()
    nuke_scroll_box()
    change_to_edit()

def nuke_scroll_box():
    for widget in scroll_box.winfo_children():
        widget.destroy()


def sb_worker():
    populate_scroll_box()
    return

def sb_thread():    
    thread = threading.Thread(target=sb_worker)
    thread.setDaemon(True)
    thread.start()
    
    return

def populate_scroll_box():
    for i in names:
        curr_box = customtkinter.CTkCheckBox(scroll_box, text=i)
        check_boxs.append(curr_box)
        curr_box.grid(column=0, row=len(check_boxs)-1, padx=5, pady=6)   
    return

# WIP
def editGui(root):
    global check_boxs, scroll_box, names
    json_fp = open(f"{os.path.dirname(os.path.realpath(__file__))}/nasdaq.json")
    json_file = json.load(json_fp)
    names = json_file["data"] 
    check_boxs = []
    json_fp.close()
    
    page = customtkinter.CTkFrame(root)
    del_group = customtkinter.CTkFrame(page)
    scroll_box = customtkinter.CTkScrollableFrame(del_group, width=200, height=200)

    sb_thread()

    add_button = customtkinter.CTkButton(page, text="Add", font=("Roboto", 12), command=get_add_input)
    del_button = customtkinter.CTkButton(del_group, text="Delete", font=("Roboto", 12), command=remove_from_list)
    back = customtkinter.CTkButton(root, width=70, height=14, text="Back", font=("Roboto", 12), command=change_to_menu)

    page.grid(column=0, row=0, padx=60, pady=20)
    del_group.grid(column=0, row=0, padx=60, pady=20)
    del_button.grid(column=0, row=1, padx=10, pady=(0,12), sticky="ew")

    scroll_box.grid(column=0, row=0, padx=10, pady=12)

    add_button.grid(column=0, row=1, padx=10, pady=(0,20))
    
    back.grid(column=0, row=1, padx=10, pady=12)

def remove_from_list():
    write_list = []
    for curr_box in check_boxs:
        if(curr_box.get() == 0):
            write_list.append(curr_box.cget("text"))
        else:
            try:
                names.remove(curr_box.cget("text"))
            except ValueError:
                pass
            curr_box.destroy()
    json_fp = open(f"{os.path.dirname(os.path.realpath(__file__))}/nasdaq.json", "+w")
    write_list.sort()
    json.dump({"data": write_list}, json_fp, indent=4)
    json_fp.close()
    return

def menuGui(root):
    page = customtkinter.CTkFrame(root)
    title = customtkinter.CTkLabel(page, text="Welcome", font=("Roboto", 14))
    script_button = customtkinter.CTkButton(page, text="run", font=("Roboto", 12), command=change_to_script)
    edit_button = customtkinter.CTkButton(page, text="edit", font=("Roboto", 12), command=change_to_edit)

    page.grid(column=0, row=0, padx=60, pady=20)
    title.grid(column=0, row=0, padx=10, pady=12, columnspan=2)
    script_button.grid(column=0, row=1, padx=10, pady=12)
    edit_button.grid(column=1, row=1, padx=10, pady=12)


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
    back = customtkinter.CTkButton(root, width=70, height=14, text="Back", font=("Roboto", 12), command=change_to_menu)
    progress_bar.set(0)

    page.grid(column=0, row=0, padx=60, pady=20)
    greeting.grid(column=0, row=1, columnspan=3, padx=10, pady=12)

    start_button.grid(column=0, row=2, padx=10, pady=12, columnspan=3)
    progress_bar.grid(column=0, row=3, padx=10, pady=12, columnspan=2)
    out_path.grid(column=0, row=5, columnspan=3)
    back.grid(column=0, row=1, padx=10, pady=12)
    out_button.grid_remove()

def change_to_script():
    global root
    for widget in root.winfo_children():
        widget.destroy()
    scriptGui(root)

def change_to_edit():
    global root
    for widget in root.winfo_children():
        widget.destroy()
    editGui(root)

def change_to_menu():
    global root
    for widget in root.winfo_children():
        widget.destroy()
    menuGui(root)

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
    root.title("NASDAQ Reports")
    menuGui(root)
    root.protocol("WM_DELETE_WINDOW", on_quit)
    root.mainloop()

if __name__ == "__main__":
    main()
