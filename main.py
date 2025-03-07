import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime

DATA_FILE = "data.json"

# ---------------- Data Loading and Saving ----------------
def load_data(filename=DATA_FILE):
    if not os.path.exists(filename):
        return {"accounts": {}, "OTHERS": {}}
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except Exception as e:
        messagebox.showerror("Error", f"Error loading JSON file: {e}")
        return {"accounts": {}, "OTHERS": {}}

def save_data(data, filename=DATA_FILE, silent=False):
    try:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        if not silent:
            messagebox.showinfo("Save Successful", f"Data saved to {filename}.")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving JSON file: {e}")

# ---------------- Pretty Print Function ----------------
def pretty_print(data, indent=0):
    spacing = "  " * indent
    result = ""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                result += f"{spacing}{key}:\n{pretty_print(value, indent+1)}"
            else:
                result += f"{spacing}{key}: {value}\n"
    elif isinstance(data, list):
        for item in data:
            result += f"{spacing}- {pretty_print(item, indent+1).strip()}\n"
    else:
        result += f"{spacing}{data}\n"
    return result

# ---------------- Global Data and Variables ----------------
data = load_data()
selected_account_email = None
selected_service_index = None
edit_mode = False          # When True, account details fields are editable.
original_account = {}      # To store original values for comparison.

# ---------------- Main Window and Notebook ----------------
root = tk.Tk()
root.title("Account & Service Management")
root.geometry("1200x950")

main_notebook = ttk.Notebook(root)
main_notebook.pack(fill="both", expand=True, padx=10, pady=10)

# ---------------- Main Tab (Treeview) ----------------
main_tab = tk.Frame(main_notebook)
main_notebook.add(main_tab, text="Main")

main_tree_scroll = tk.Scrollbar(main_tab)
main_tree_scroll.pack(side="right", fill="y")

main_tree = ttk.Treeview(main_tab, yscrollcommand=main_tree_scroll.set)
main_tree_scroll.config(command=main_tree.yview)
main_tree["columns"] = ("Details",)
main_tree.column("#0", width=300, minwidth=150, stretch=tk.YES)
main_tree.column("Details", width=600, minwidth=150, stretch=tk.YES)
main_tree.heading("#0", text="Key/Name", anchor=tk.W)
main_tree.heading("Details", text="Value", anchor=tk.W)
main_tree.pack(fill="both", expand=True)

def insert_account_tree(account_email, account_data, tree_widget):
    account_node = tree_widget.insert("", "end", text=account_email, open=False)
    # Display "sign_in_with" value; remove this line if not needed.
    tree_widget.insert(account_node, "end", text="sign_in_with", values=(account_data.get("sign_in_with", ""),), open=False)
    services_branch = tree_widget.insert(account_node, "end", text="services", open=False)
    for service in account_data.get("services", []):
        service_node = tree_widget.insert(services_branch, "end", text=service.get("name", "Unnamed Service"), open=False)
        for key, value in service.items():
            if key == "name":
                continue
            if isinstance(value, dict):
                child_node = tree_widget.insert(service_node, "end", text=key, open=False)
                for subkey, subvalue in value.items():
                    tree_widget.insert(child_node, "end", text=subkey, values=(subvalue,), open=False)
            elif isinstance(value, list):
                list_node = tree_widget.insert(service_node, "end", text=key, open=False)
                for idx, item in enumerate(value):
                    tree_widget.insert(list_node, "end", text=f"[{idx}]", values=(item,), open=False)
            else:
                tree_widget.insert(service_node, "end", text=key, values=(value,), open=False)

def insert_tree_item(parent, key, value, tree_widget):
    if isinstance(value, dict):
        node = tree_widget.insert(parent, "end", text=key, open=False)
        for subkey, subvalue in value.items():
            insert_tree_item(node, subkey, subvalue, tree_widget)
    elif isinstance(value, list):
        node = tree_widget.insert(parent, "end", text=key, open=False)
        for idx, item in enumerate(value):
            display_key = item["name"] if isinstance(item, dict) and "name" in item else f"[{idx}]"
            insert_tree_item(node, display_key, item, tree_widget)
    else:
        tree_widget.insert(parent, "end", text=key, values=(value,), open=False)

def insert_others_tree(others_data, tree_widget):
    others_node = tree_widget.insert("", "end", text="OTHERS", open=False)
    for key, value in others_data.items():
        insert_tree_item(others_node, key, value, tree_widget)

def refresh_main_tree():
    main_tree.delete(*main_tree.get_children())
    for email, account in data.get("accounts", {}).items():
        insert_account_tree(email, account, main_tree)
    if "OTHERS" in data:
        insert_account_tree("OTHERS", data["OTHERS"], main_tree)

refresh_main_tree()

# ---------------- CRUD Tab (Form-Based Interface) ----------------
crud_tab = tk.Frame(main_notebook)
main_notebook.add(crud_tab, text="CRUD")

crud_left = tk.Frame(crud_tab)
crud_left.pack(side="left", fill="y", padx=10, pady=10)
tk.Label(crud_left, text="Accounts", font=("Helvetica", 12, "bold")).pack(pady=5)
accounts_listbox = tk.Listbox(crud_left, width=40, height=30, font=("Helvetica", 11))
accounts_listbox.pack(padx=5, pady=5, fill="both", expand=True)

crud_right = tk.Frame(crud_tab)
crud_right.pack(side="left", fill="both", expand=True, padx=10, pady=10)
selected_account_label_crud = tk.Label(crud_right, text="Selected Account: None", font=("Helvetica", 16, "bold"))
selected_account_label_crud.pack(anchor="nw", padx=5, pady=5)
crud_notebook = ttk.Notebook(crud_right)
crud_notebook.pack(fill="both", expand=True, padx=5, pady=5)

# ----- Account Details Sub-Tab -----
account_frame_crud = ttk.Frame(crud_notebook)
crud_notebook.add(account_frame_crud, text="Account Details")

# Email
tk.Label(account_frame_crud, text="Email:", font=("Helvetica", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
email_entry = tk.Entry(account_frame_crud, width=60, font=("Helvetica", 11), state="disabled")
email_entry.grid(row=0, column=1, padx=5, pady=5)

# (Removed the Sign In With field for account details)

# Password
tk.Label(account_frame_crud, text="Password:", font=("Helvetica", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
acc_password_entry = tk.Entry(account_frame_crud, width=60, font=("Helvetica", 11), state="disabled")
acc_password_entry.grid(row=1, column=1, padx=5, pady=5)
def toggle_password_edit():
    if acc_password_entry.cget("state") == "disabled":
        acc_password_entry.config(state="normal")
        edit_password_btn.config(text="Lock")
        update_acc_btn.config(bg="yellow")
    else:
        acc_password_entry.config(state="disabled")
        edit_password_btn.config(text="Edit")
        update_acc_btn.config(bg=default_update_bg)
edit_password_btn = tk.Button(account_frame_crud, text="Edit", command=toggle_password_edit, font=("Helvetica", 11))
edit_password_btn.grid(row=1, column=2, padx=5, pady=5)

# Date Created
tk.Label(account_frame_crud, text="Date Created:", font=("Helvetica", 11)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
acc_date_entry = tk.Entry(account_frame_crud, width=60, font=("Helvetica", 11), state="disabled")
acc_date_entry.grid(row=2, column=1, padx=5, pady=5)

# Phone(s)
tk.Label(account_frame_crud, text="Phone(s):", font=("Helvetica", 11)).grid(row=3, column=0, sticky="e", padx=5, pady=5)
phone_entry = tk.Entry(account_frame_crud, width=60, font=("Helvetica", 11), state="disabled")
phone_entry.grid(row=3, column=1, padx=5, pady=5)

# Account Buttons and Edit All
acc_button_frame_crud = tk.Frame(account_frame_crud)
acc_button_frame_crud.grid(row=4, column=1, pady=10)
new_acc_btn = tk.Button(acc_button_frame_crud, text="New Account", command=lambda: new_account(), font=("Helvetica", 11))
new_acc_btn.pack(side="left", padx=5)
add_svc_btn = tk.Button(acc_button_frame_crud, text="Add Service", command=lambda: add_service(), font=("Helvetica", 11))
add_svc_btn.pack(side="left", padx=5)
update_acc_btn = tk.Button(acc_button_frame_crud, text="Update Account", command=lambda: update_account(), font=("Helvetica", 11))
update_acc_btn.pack(side="left", padx=5)
delete_acc_btn = tk.Button(acc_button_frame_crud, text="Delete Account", command=lambda: delete_account(), font=("Helvetica", 11))
delete_acc_btn.pack(side="left", padx=5)
default_update_bg = update_acc_btn.cget("bg")
def toggle_edit_mode():
    global edit_mode, original_account
    if selected_account_email == "OTHERS":
        messagebox.showinfo("Info", "The OTHERS account cannot edit the email field.")
    if not edit_mode:
        edit_mode = True
        original_account = {
            "email": email_entry.get(),
            "password": acc_password_entry.get(),
            "dateCreated": acc_date_entry.get(),
            "phone": phone_entry.get()
        }
        if selected_account_email != "OTHERS":
            email_entry.config(state="normal")
        phone_entry.config(state="normal")
        acc_date_entry.config(state="normal")
        acc_password_entry.config(state="normal")
        update_acc_btn.config(bg="yellow")
        edit_all_btn.config(text="Cancel Edit")
    else:
        edit_mode = False
        if selected_account_email != "OTHERS":
            email_entry.config(state="normal")
            email_entry.delete(0, tk.END)
            email_entry.insert(0, original_account.get("email", ""))
            email_entry.config(state="disabled")
        phone_entry.config(state="normal")
        phone_entry.delete(0, tk.END)
        phone_entry.insert(0, original_account.get("phone", ""))
        phone_entry.config(state="disabled")
        acc_date_entry.config(state="normal")
        acc_date_entry.delete(0, tk.END)
        acc_date_entry.insert(0, original_account.get("dateCreated", ""))
        acc_date_entry.config(state="disabled")
        acc_password_entry.config(state="normal")
        acc_password_entry.delete(0, tk.END)
        acc_password_entry.insert(0, original_account.get("password", ""))
        acc_password_entry.config(state="disabled")
        update_acc_btn.config(bg=default_update_bg)
        edit_all_btn.config(text="Edit All")
edit_all_btn = tk.Button(acc_button_frame_crud, text="Edit All", command=toggle_edit_mode, font=("Helvetica", 11))
edit_all_btn.pack(side="left", padx=5)

# ----- Service Details Sub-Tab -----
service_frame_crud = ttk.Frame(crud_notebook)
crud_notebook.add(service_frame_crud, text="Service Details")

tk.Label(service_frame_crud, text="Service Name:", font=("Helvetica", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
sname_entry = tk.Entry(service_frame_crud, width=60, font=("Helvetica", 11))
sname_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(service_frame_crud, text="Username:", font=("Helvetica", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
susername_entry = tk.Entry(service_frame_crud, width=60, font=("Helvetica", 11))
susername_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(service_frame_crud, text="Email:", font=("Helvetica", 11)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
semail_entry = tk.Entry(service_frame_crud, width=60, font=("Helvetica", 11))
semail_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(service_frame_crud, text="Link:", font=("Helvetica", 11)).grid(row=3, column=0, sticky="e", padx=5, pady=5)
slink_entry = tk.Entry(service_frame_crud, width=60, font=("Helvetica", 11))
slink_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Label(service_frame_crud, text="Webpage:", font=("Helvetica", 11)).grid(row=4, column=0, sticky="e", padx=5, pady=5)
swebpage_entry = tk.Entry(service_frame_crud, width=60, font=("Helvetica", 11))
swebpage_entry.grid(row=4, column=1, padx=5, pady=5)

tk.Label(service_frame_crud, text="URL:", font=("Helvetica", 11)).grid(row=5, column=0, sticky="e", padx=5, pady=5)
surl_entry = tk.Entry(service_frame_crud, width=60, font=("Helvetica", 11))
surl_entry.grid(row=5, column=1, padx=5, pady=5)

tk.Label(service_frame_crud, text="Password:", font=("Helvetica", 11)).grid(row=6, column=0, sticky="e", padx=5, pady=5)
spassword_entry = tk.Entry(service_frame_crud, width=60, font=("Helvetica", 11))
spassword_entry.grid(row=6, column=1, padx=5, pady=5)

tk.Label(service_frame_crud, text="PIN:", font=("Helvetica", 11)).grid(row=7, column=0, sticky="e", padx=5, pady=5)
spin_entry = tk.Entry(service_frame_crud, width=60, font=("Helvetica", 11))
spin_entry.grid(row=7, column=1, padx=5, pady=5)

tk.Label(service_frame_crud, text="Phone:", font=("Helvetica", 11)).grid(row=8, column=0, sticky="e", padx=5, pady=5)
sphone_entry = tk.Entry(service_frame_crud, width=60, font=("Helvetica", 11))
sphone_entry.grid(row=8, column=1, padx=5, pady=5)

tk.Label(service_frame_crud, text="Date Created:", font=("Helvetica", 11)).grid(row=9, column=0, sticky="e", padx=5, pady=5)
sdate_entry = tk.Entry(service_frame_crud, width=60, font=("Helvetica", 11))
sdate_entry.grid(row=9, column=1, padx=5, pady=5)

# New: Sign In With field for the service details
tk.Label(service_frame_crud, text="Sign In With:", font=("Helvetica", 11)).grid(row=10, column=0, sticky="e", padx=5, pady=5)
sign_in_with_entry = tk.Entry(service_frame_crud, width=60, font=("Helvetica", 11))
sign_in_with_entry.grid(row=10, column=1, padx=5, pady=5)

tk.Label(service_frame_crud, text="Note:", font=("Helvetica", 11)).grid(row=11, column=0, sticky="e", padx=5, pady=5)
snote_entry = tk.Entry(service_frame_crud, width=60, font=("Helvetica", 11))
snote_entry.grid(row=11, column=1, padx=5, pady=5)

tk.Label(service_frame_crud, text="Details (JSON):", font=("Helvetica", 11)).grid(row=12, column=0, sticky="ne", padx=5, pady=5)
sdetails_text = tk.Text(service_frame_crud, width=60, height=8, font=("Helvetica", 11))
sdetails_text.grid(row=12, column=1, padx=5, pady=5)

# ---- New: Service List & Search Area ----
# Create a frame that will hold the search bar (with autosuggest dropdown)
# on the left side and the services list (output box) on the right.
service_list_frame = tk.Frame(service_frame_crud)
service_list_frame.grid(row=13, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

# Left side: Search frame with a label and a combobox for autosuggest.
search_frame = tk.Frame(service_list_frame)
search_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
tk.Label(search_frame, text="Search:", font=("Helvetica", 11)).pack(anchor="w")
search_combobox = ttk.Combobox(search_frame, width=30)
search_combobox.pack(anchor="w", pady=2)

# Right side: Output box (the services list)
# Right side: Output box (the services list)
list_frame = tk.Frame(service_list_frame)
list_frame.grid(row=0, column=1, sticky="nw", padx=5, pady=5)
tk.Label(list_frame, text="Services List:", font=("Helvetica", 11)).pack(anchor="w")
services_listbox = tk.Listbox(list_frame, width=55, height=8, font=("Helvetica", 11))
services_listbox.pack(anchor="w", pady=2)
services_listbox.bind("<<ListboxSelect>>", lambda event: on_service_select(event))

# Functions for auto-suggest and filtering
def filter_services(text):
    services_listbox.delete(0, tk.END)
    if selected_account_email is None:
        return
    if selected_account_email == "OTHERS":
        account = data["OTHERS"]
    else:
        account = data["accounts"].get(selected_account_email, {})
    for svc in account.get("services", []):
        svc_name = svc.get("name", "")
        if text == "" or text.lower() in svc_name.lower():
            services_listbox.insert(tk.END, svc_name)

def on_search_update():
    text = search_combobox.get().lower()
    if selected_account_email is None:
        return
    if selected_account_email == "OTHERS":
        services = data["OTHERS"].get("services", [])
    else:
        services = data["accounts"].get(selected_account_email, {}).get("services", [])
    suggestions = [svc.get("name", "") for svc in services if text in svc.get("name", "").lower()]
    search_combobox['values'] = suggestions
    filter_services(text)

def on_search_select():
    text = search_combobox.get()
    filter_services(text)

# Bind the search combobox events.
search_combobox.bind("<KeyRelease>", lambda event: on_search_update())
search_combobox.bind("<<ComboboxSelected>>", lambda event: on_search_select())

# Modify refresh_services_list() to respect any search text.
def refresh_services_list():
    # If search_combobox exists, use its text; otherwise show all.
    search_text = ""
    try:
        search_text = search_combobox.get().lower()
    except:
        pass
    if selected_account_email is None:
        return
    services_listbox.delete(0, tk.END)
    if selected_account_email == "OTHERS":
        account = data["OTHERS"]
    else:
        account = data["accounts"].get(selected_account_email, {})
    for svc in account.get("services", []):
        svc_name = svc.get("name", "")
        if search_text == "" or search_text in svc_name.lower():
            services_listbox.insert(tk.END, svc_name)

# ---- End of Service List & Search Area ----

svc_button_frame_crud = tk.Frame(service_frame_crud)
svc_button_frame_crud.grid(row=14, column=1, pady=10)
create_svc_btn = tk.Button(svc_button_frame_crud, text="Create Service", command=lambda: create_service(), font=("Helvetica", 11))
create_svc_btn.pack(side="left", padx=5)
update_svc_btn = tk.Button(svc_button_frame_crud, text="Update Service", command=lambda: update_service(), font=("Helvetica", 11))
update_svc_btn.pack(side="left", padx=5)
delete_svc_btn = tk.Button(svc_button_frame_crud, text="Delete Service", command=lambda: delete_service(), font=("Helvetica", 11))
delete_svc_btn.pack(side="left", padx=5)

# ---------------- Context Menu for CRUD (Right-Click Options) ----------------
current_widget = None
def cut_text():
    global current_widget
    try:
        current_widget.event_generate("<<Cut>>")
    except Exception:
        pass
def copy_text():
    global current_widget
    try:
        current_widget.event_generate("<<Copy>>")
    except Exception:
        pass
def paste_text():
    global current_widget
    try:
        current_widget.event_generate("<<Paste>>")
    except Exception:
        pass
def delete_text():
    global current_widget
    try:
        current_widget.delete("sel.first", "sel.last")
    except Exception:
        pass
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Cut", command=cut_text)
context_menu.add_command(label="Copy", command=copy_text)
context_menu.add_command(label="Paste", command=paste_text)
context_menu.add_command(label="Delete", command=delete_text)
def show_context_menu(event):
    global current_widget
    current_widget = event.widget
    context_menu.tk_popup(event.x_root, event.y_root)
    return "break"
def bind_context_menu(widget):
    widget.bind("<Button-3>", show_context_menu)
for w in [email_entry, acc_password_entry, acc_date_entry, phone_entry,
          sname_entry, susername_entry, semail_entry, slink_entry, swebpage_entry,
          surl_entry, spassword_entry, spin_entry, sphone_entry, sdate_entry, snote_entry, sign_in_with_entry]:
    bind_context_menu(w)
bind_context_menu(sdetails_text)

def refresh_account_list():
    accounts_listbox.delete(0, tk.END)
    for email in data.get("accounts", {}):
        accounts_listbox.insert(tk.END, email)
    if "OTHERS" in data:
        accounts_listbox.insert(tk.END, "OTHERS")

def on_account_select(event):
    global selected_account_email, selected_service_index, edit_mode, original_account
    selection = accounts_listbox.curselection()
    if not selection:
        return
    index = selection[0]
    selected_account_email = accounts_listbox.get(index)
    selected_account_label_crud.config(text="Selected Account: " + selected_account_email)
    if selected_account_email == "OTHERS":
        account = data["OTHERS"]
        password = account.get("password", "")
        dateCreated = account.get("dateCreated", "")
        phone_arr = account.get("phone", [])
    else:
        account = data["accounts"].get(selected_account_email, {})
        password = account.get("password", "")
        dateCreated = account.get("dateCreated", "")
        phone_arr = account.get("phone", [])
    edit_mode = False
    edit_all_btn.config(text="Edit All")
    update_acc_btn.config(bg=default_update_bg)
    email_entry.config(state="normal")
    email_entry.delete(0, tk.END)
    email_entry.insert(0, selected_account_email)
    email_entry.config(state="disabled")
    acc_password_entry.config(state="normal")
    acc_password_entry.delete(0, tk.END)
    acc_password_entry.insert(0, password)
    acc_password_entry.config(state="disabled")
    edit_password_btn.config(text="Edit")
    acc_date_entry.config(state="normal")
    acc_date_entry.delete(0, tk.END)
    acc_date_entry.insert(0, dateCreated)
    acc_date_entry.config(state="disabled")
    phone_entry.config(state="normal")
    phone_entry.delete(0, tk.END)
    phone_entry.insert(0, ", ".join(phone_arr))
    phone_entry.config(state="disabled")
    original_account = {
        "email": selected_account_email,
        "password": password,
        "dateCreated": dateCreated,
        "phone": phone_entry.get()
    }
    refresh_services_list()
    clear_service_form()
    selected_service_index = None
    update_account_buttons()

def new_account():
    global selected_account_email
    new_email = email_entry.get().strip()
    if not new_email:
        messagebox.showwarning("Input Error", "Enter an email for the new account.")
        return
    if new_email == "OTHERS":
        messagebox.showwarning("Input Error", "The account name 'OTHERS' is reserved.")
        return
    if new_email in data.get("accounts", {}):
        messagebox.showwarning("Input Error", "Account with this email already exists.")
        return
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["accounts"][new_email] = {
        "sign_in_with": new_email,  # or adjust as needed
        "password": "",
        "dateCreated": now,
        "phone": [],
        "services": []
    }
    selected_account_email = new_email
    selected_account_label_crud.config(text="Selected Account: " + new_email)
    refresh_account_list()
    refresh_services_list()
    update_account_buttons()
    save_data(data, silent=True)

def add_service():
    if selected_account_email is None:
        messagebox.showwarning("No Account Selected", "Please select an existing account first.")
        return
    crud_notebook.select(service_frame_crud)
    clear_service_form()

def update_account():
    global selected_account_email, edit_mode
    new_email = email_entry.get().strip()
    if not new_email:
        messagebox.showwarning("Input Error", "Email is required.")
        return
    password_val = acc_password_entry.get().strip()
    date_val = acc_date_entry.get().strip()
    phone_str = phone_entry.get().strip()
    phone_list = [p.strip() for p in phone_str.split(",") if p.strip()] if phone_str else []
    if edit_mode:
        if (new_email == original_account.get("email") and
            password_val == original_account.get("password") and
            date_val == original_account.get("dateCreated") and
            phone_str == original_account.get("phone")):
            messagebox.showinfo("No Changes", "No changes made.")
            toggle_edit_mode()
            return
    if selected_account_email is None:
        messagebox.showwarning("No Account Selected", "Select an account first.")
        return
    if selected_account_email != "OTHERS":
        if new_email != selected_account_email:
            if new_email in data["accounts"]:
                messagebox.showwarning("Input Error", "Account with this email already exists.")
                return
            data["accounts"][new_email] = data["accounts"].pop(selected_account_email)
            selected_account_email = new_email
        data["accounts"][selected_account_email]["password"] = password_val
        data["accounts"][selected_account_email]["dateCreated"] = date_val
        data["accounts"][selected_account_email]["phone"] = phone_list
    else:
        data["OTHERS"]["password"] = password_val
        data["OTHERS"]["dateCreated"] = date_val
        data["OTHERS"]["phone"] = phone_list
    refresh_account_list()
    selected_account_label_crud.config(text="Selected Account: " + selected_account_email)
    update_account_buttons()
    save_data(data, silent=True)
    if edit_mode:
        toggle_edit_mode()

def delete_account():
    global selected_account_email
    if selected_account_email is None:
        messagebox.showwarning("No Account Selected", "Select an account first.")
        return
    if selected_account_email == "OTHERS":
        messagebox.showwarning("Action Not Allowed", "Cannot delete the reserved OTHERS account.")
        return
    if messagebox.askyesno("Confirm Delete", f"Delete account {selected_account_email}?"):
        data["accounts"].pop(selected_account_email, None)
        selected_account_email = None
        refresh_account_list()
        clear_account_form()
        services_listbox.delete(0, tk.END)
        selected_account_label_crud.config(text="Selected Account: None")
        update_account_buttons()
        save_data(data, silent=True)

def clear_account_form():
    email_entry.config(state="normal")
    email_entry.delete(0, tk.END)
    email_entry.config(state="disabled")
    acc_password_entry.config(state="normal")
    acc_password_entry.delete(0, tk.END)
    acc_password_entry.config(state="disabled")
    acc_date_entry.config(state="normal")
    acc_date_entry.delete(0, tk.END)
    acc_date_entry.config(state="disabled")
    phone_entry.config(state="normal")
    phone_entry.delete(0, tk.END)
    phone_entry.config(state="disabled")

def update_account_buttons():
    if selected_account_email:
        add_svc_btn.config(state="normal")
    else:
        add_svc_btn.config(state="disabled")

def on_service_select(event):
    global selected_service_index
    selection = services_listbox.curselection()
    if not selection or selected_account_email is None:
        return
    selected_service_index = selection[0]
    if selected_account_email == "OTHERS":
        account = data["OTHERS"]
    else:
        account = data["accounts"][selected_account_email]
    svc = account["services"][selected_service_index]
    sname_entry.delete(0, tk.END)
    sname_entry.insert(0, svc.get("name", ""))
    susername_entry.delete(0, tk.END)
    susername_entry.insert(0, svc.get("username", ""))
    semail_entry.delete(0, tk.END)
    semail_entry.insert(0, svc.get("email", ""))
    slink_entry.delete(0, tk.END)
    slink_entry.insert(0, svc.get("link", ""))
    swebpage_entry.delete(0, tk.END)
    swebpage_entry.insert(0, svc.get("webpage", ""))
    surl_entry.delete(0, tk.END)
    surl_entry.insert(0, svc.get("url", ""))
    spassword_entry.delete(0, tk.END)
    spassword_entry.insert(0, svc.get("password", ""))
    spin_entry.delete(0, tk.END)
    spin_entry.insert(0, svc.get("PIN", ""))
    sphone_entry.delete(0, tk.END)
    sphone_entry.insert(0, svc.get("phone", ""))
    sdate_entry.delete(0, tk.END)
    sdate_entry.insert(0, svc.get("dateCreated", ""))
    sign_in_with_entry.delete(0, tk.END)
    sign_in_with_entry.insert(0, svc.get("sign_in_with", ""))
    snote_entry.delete(0, tk.END)
    snote_entry.insert(0, svc.get("note", ""))
    sdetails_text.delete("1.0", tk.END)
    details = svc.get("details", "")
    if isinstance(details, dict):
        sdetails_text.insert(tk.END, pretty_print(details))
    else:
        sdetails_text.insert(tk.END, details)

def clear_service_form():
    sname_entry.delete(0, tk.END)
    susername_entry.delete(0, tk.END)
    semail_entry.delete(0, tk.END)
    slink_entry.delete(0, tk.END)
    swebpage_entry.delete(0, tk.END)
    surl_entry.delete(0, tk.END)
    spassword_entry.delete(0, tk.END)
    spin_entry.delete(0, tk.END)
    sphone_entry.delete(0, tk.END)
    sdate_entry.delete(0, tk.END)
    sign_in_with_entry.delete(0, tk.END)
    snote_entry.delete(0, tk.END)
    sdetails_text.delete("1.0", tk.END)

def create_service():
    if selected_account_email is None:
        messagebox.showwarning("No Account Selected", "Select an account first.")
        return
    svc_name = sname_entry.get().strip()
    if not svc_name:
        messagebox.showwarning("Input Error", "Service name is required.")
        return
    new_svc = {
        "name": svc_name,
        "username": susername_entry.get().strip(),
        "email": semail_entry.get().strip(),
        "link": slink_entry.get().strip(),
        "webpage": swebpage_entry.get().strip(),
        "url": surl_entry.get().strip(),
        "password": spassword_entry.get().strip(),
        "PIN": spin_entry.get().strip(),
        "phone": sphone_entry.get().strip(),
        "dateCreated": sdate_entry.get().strip(),
        "sign_in_with": sign_in_with_entry.get().strip(),
        "note": snote_entry.get().strip()
    }
    details_str = sdetails_text.get("1.0", tk.END).strip()
    if details_str:
        try:
            new_svc["details"] = json.loads(details_str)
        except Exception:
            new_svc["details"] = details_str
    else:
        new_svc["details"] = ""
    if selected_account_email == "OTHERS":
        data["OTHERS"].setdefault("services", []).append(new_svc)
    else:
        data["accounts"][selected_account_email]["services"].append(new_svc)
    refresh_services_list()
    clear_service_form()
    save_data(data, silent=True)

def update_service():
    global selected_service_index
    if selected_account_email is None or selected_service_index is None:
        messagebox.showwarning("No Service Selected", "Select a service first.")
        return
    svc_name = sname_entry.get().strip()
    if not svc_name:
        messagebox.showwarning("Input Error", "Service name is required.")
        return
    updated_svc = {
        "name": svc_name,
        "username": susername_entry.get().strip(),
        "email": semail_entry.get().strip(),
        "link": slink_entry.get().strip(),
        "webpage": swebpage_entry.get().strip(),
        "url": surl_entry.get().strip(),
        "password": spassword_entry.get().strip(),
        "PIN": spin_entry.get().strip(),
        "phone": sphone_entry.get().strip(),
        "dateCreated": sdate_entry.get().strip(),
        "sign_in_with": sign_in_with_entry.get().strip(),
        "note": snote_entry.get().strip()
    }
    details_str = sdetails_text.get("1.0", tk.END).strip()
    if details_str:
        try:
            updated_svc["details"] = json.loads(details_str)
        except Exception:
            updated_svc["details"] = details_str
    else:
        updated_svc["details"] = ""
    if selected_account_email == "OTHERS":
        data["OTHERS"]["services"][selected_service_index] = updated_svc
    else:
        data["accounts"][selected_account_email]["services"][selected_service_index] = updated_svc
    refresh_services_list()
    clear_service_form()
    save_data(data, silent=True)

def delete_service():
    global selected_service_index
    if selected_account_email is None or selected_service_index is None:
        messagebox.showwarning("No Service Selected", "Select a service first.")
        return
    if messagebox.askyesno("Confirm Delete", "Delete the selected service?"):
        if selected_account_email == "OTHERS":
            data["OTHERS"]["services"].pop(selected_service_index)
        else:
            data["accounts"][selected_account_email]["services"].pop(selected_service_index)
        refresh_services_list()
        clear_service_form()
        selected_service_index = None
        save_data(data, silent=True)

def save_all():
    save_data(data, silent=False)
    refresh_account_list()
    refresh_main_tree()
    if selected_account_email:
        idxs = [i for i, email in enumerate(accounts_listbox.get(0, tk.END)) if email == selected_account_email]
        if idxs:
            accounts_listbox.selection_clear(0, tk.END)
            accounts_listbox.selection_set(idxs[0])
            on_account_select(None)

accounts_listbox.bind("<<ListboxSelect>>", on_account_select)
services_listbox.bind("<<ListboxSelect>>", on_service_select)
refresh_account_list()

global_btn_frame = tk.Frame(root)
global_btn_frame.pack(side="bottom", fill="x", padx=10, pady=10)
save_all_btn = tk.Button(global_btn_frame, text="Save All Changes", command=save_all, font=("Helvetica", 12, "bold"))
save_all_btn.pack(side="left", padx=5)

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to save changes before quitting?"):
        save_all()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
