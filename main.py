import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "data.json"

# ---------------- Data Loading and Saving ----------------
def load_data(filename=DATA_FILE):
    if not os.path.exists(filename):
        messagebox.showerror("File Not Found", f"{filename} does not exist.")
        return {"accounts": {}, "OTHERS": {}}
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except Exception as e:
        messagebox.showerror("Error", f"Error loading JSON file: {e}")
        return {"accounts": {}, "OTHERS": {}}

def save_data(data, filename=DATA_FILE):
    try:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
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

# ---------------- Main Window and Notebook ----------------
root = tk.Tk()
root.title("Account & Service Management")
root.geometry("1200x850")

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

def insert_others_tree(others_data, tree_widget):
    others_node = tree_widget.insert("", "end", text="OTHERS", open=False)
    for key, value in others_data.items():
        if isinstance(value, dict):
            sub_node = tree_widget.insert(others_node, "end", text=key, open=False)
            for subkey, subvalue in value.items():
                tree_widget.insert(sub_node, "end", text=subkey, values=(subvalue,), open=False)
        elif isinstance(value, list):
            list_node = tree_widget.insert(others_node, "end", text=key, open=False)
            for idx, item in enumerate(value):
                tree_widget.insert(list_node, "end", text=f"[{idx}]", values=(item,), open=False)
        else:
            tree_widget.insert(others_node, "end", text=key, values=(value,), open=False)

def refresh_main_tree():
    main_tree.delete(*main_tree.get_children())
    for email, account in data.get("accounts", {}).items():
        insert_account_tree(email, account, main_tree)
    if "OTHERS" in data:
        insert_others_tree(data["OTHERS"], main_tree)

refresh_main_tree()

# ---------------- CRUD Tab (Form-Based Interface) ----------------
crud_tab = tk.Frame(main_notebook)
main_notebook.add(crud_tab, text="CRUD")

# Split the CRUD tab into left and right panels.
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

tk.Label(account_frame_crud, text="Email:", font=("Helvetica", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
email_entry = tk.Entry(account_frame_crud, width=60, font=("Helvetica", 11))
email_entry.grid(row=0, column=1, padx=5, pady=5)
email_entry.bind("<KeyRelease>", lambda event: update_account_buttons())

tk.Label(account_frame_crud, text="Sign In With:", font=("Helvetica", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
signin_entry = tk.Entry(account_frame_crud, width=60, font=("Helvetica", 11))
signin_entry.grid(row=1, column=1, padx=5, pady=5)

acc_button_frame_crud = tk.Frame(account_frame_crud)
acc_button_frame_crud.grid(row=2, column=1, pady=10)
new_acc_btn = tk.Button(acc_button_frame_crud, text="New Account", command=lambda: new_account(), font=("Helvetica", 11))
new_acc_btn.pack(side="left", padx=5)
add_svc_btn = tk.Button(acc_button_frame_crud, text="Add Service", command=lambda: add_service(), font=("Helvetica", 11))
add_svc_btn.pack(side="left", padx=5)
update_acc_btn = tk.Button(acc_button_frame_crud, text="Update Account", command=lambda: update_account(), font=("Helvetica", 11))
update_acc_btn.pack(side="left", padx=5)
delete_acc_btn = tk.Button(acc_button_frame_crud, text="Delete Account", command=lambda: delete_account(), font=("Helvetica", 11))
delete_acc_btn.pack(side="left", padx=5)

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

tk.Label(service_frame_crud, text="Note:", font=("Helvetica", 11)).grid(row=10, column=0, sticky="e", padx=5, pady=5)
snote_entry = tk.Entry(service_frame_crud, width=60, font=("Helvetica", 11))
snote_entry.grid(row=10, column=1, padx=5, pady=5)

tk.Label(service_frame_crud, text="Details (JSON):", font=("Helvetica", 11)).grid(row=11, column=0, sticky="ne", padx=5, pady=5)
sdetails_text = tk.Text(service_frame_crud, width=60, height=8, font=("Helvetica", 11))
sdetails_text.grid(row=11, column=1, padx=5, pady=5)

tk.Label(service_frame_crud, text="Services List:", font=("Helvetica", 11)).grid(row=12, column=0, sticky="nw", padx=5, pady=5)
services_listbox = tk.Listbox(service_frame_crud, width=40, height=10, font=("Helvetica", 11))
services_listbox.grid(row=12, column=1, sticky="w", padx=5, pady=5)

svc_button_frame_crud = tk.Frame(service_frame_crud)
svc_button_frame_crud.grid(row=13, column=1, pady=10)
create_svc_btn = tk.Button(svc_button_frame_crud, text="Create Service", command=lambda: create_service(), font=("Helvetica", 11))
create_svc_btn.pack(side="left", padx=5)
update_svc_btn = tk.Button(svc_button_frame_crud, text="Update Service", command=lambda: update_service(), font=("Helvetica", 11))
update_svc_btn.pack(side="left", padx=5)
delete_svc_btn = tk.Button(svc_button_frame_crud, text="Delete Service", command=lambda: delete_service(), font=("Helvetica", 11))
delete_svc_btn.pack(side="left", padx=5)

# ---------------- Global CRUD Functions ----------------
def refresh_account_list():
    accounts_listbox.delete(0, tk.END)
    for email in data.get("accounts", {}):
        accounts_listbox.insert(tk.END, email)

def on_account_select(event):
    global selected_account_email, selected_service_index
    selection = accounts_listbox.curselection()
    if not selection:
        return
    index = selection[0]
    selected_account_email = accounts_listbox.get(index)
    selected_account_label_crud.config(text="Selected Account: " + selected_account_email)
    account = data["accounts"].get(selected_account_email, {})
    email_entry.delete(0, tk.END)
    email_entry.insert(0, selected_account_email)
    signin_entry.delete(0, tk.END)
    signin_entry.insert(0, account.get("sign_in_with", ""))
    refresh_services_list()
    clear_service_form()
    selected_service_index = None
    update_account_buttons()

def new_account():
    global selected_account_email
    accounts_listbox.selection_clear(0, tk.END)
    selected_account_email = None
    selected_account_label_crud.config(text="Selected Account: None")
    clear_account_form()
    update_account_buttons()

def add_service():
    if selected_account_email is None:
        messagebox.showwarning("No Account Selected", "Please select an existing account first.")
        return
    crud_notebook.select(service_frame_crud)
    clear_service_form()

def update_account():
    global selected_account_email
    new_email = email_entry.get().strip()
    if not new_email:
        messagebox.showwarning("Input Error", "Email is required.")
        return
    sign_in = signin_entry.get().strip()
    if selected_account_email is None:
        messagebox.showwarning("No Account Selected", "Select an account first.")
        return
    if new_email != selected_account_email:
        if new_email in data["accounts"]:
            messagebox.showwarning("Input Error", "Account with this email already exists.")
            return
        data["accounts"][new_email] = data["accounts"].pop(selected_account_email)
        selected_account_email = new_email
    data["accounts"][selected_account_email]["sign_in_with"] = sign_in
    refresh_account_list()
    selected_account_label_crud.config(text="Selected Account: " + selected_account_email)
    update_account_buttons()

def delete_account():
    global selected_account_email
    if selected_account_email is None:
        messagebox.showwarning("No Account Selected", "Select an account first.")
        return
    if messagebox.askyesno("Confirm Delete", f"Delete account {selected_account_email}?"):
        data["accounts"].pop(selected_account_email, None)
        selected_account_email = None
        refresh_account_list()
        clear_account_form()
        services_listbox.delete(0, tk.END)
        selected_account_label_crud.config(text="Selected Account: None")
        update_account_buttons()

def clear_account_form():
    email_entry.delete(0, tk.END)
    signin_entry.delete(0, tk.END)

def update_account_buttons():
    email = email_entry.get().strip()
    if email and email in data.get("accounts", {}):
        add_svc_btn.config(state="normal")
    else:
        add_svc_btn.config(state="disabled")

def refresh_services_list():
    services_listbox.delete(0, tk.END)
    if selected_account_email is None:
        return
    account = data["accounts"].get(selected_account_email, {})
    for svc in account.get("services", []):
        services_listbox.insert(tk.END, svc.get("name", "Unnamed Service"))

def on_service_select(event):
    global selected_service_index
    selection = services_listbox.curselection()
    if not selection or selected_account_email is None:
        return
    selected_service_index = selection[0]
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
    snote_entry.delete(0, tk.END)
    snote_entry.insert(0, svc.get("note", ""))
    sdetails_text.delete("1.0", tk.END)
    details = svc.get("details", {})
    if details == {"source": "Login"}:
        sdetails_text.insert(tk.END, "")
    else:
        sdetails_text.insert(tk.END, pretty_print(details))

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
        "note": snote_entry.get().strip()
    }
    details_str = sdetails_text.get("1.0", tk.END).strip()
    try:
        new_svc["details"] = json.loads(details_str) if details_str else {}
    except Exception as e:
        messagebox.showerror("Invalid JSON", f"Error in details field: {e}")
        return
    data["accounts"][selected_account_email]["services"].append(new_svc)
    refresh_services_list()
    clear_service_form()

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
        "note": snote_entry.get().strip()
    }
    details_str = sdetails_text.get("1.0", tk.END).strip()
    try:
        updated_svc["details"] = json.loads(details_str) if details_str else {}
    except Exception as e:
        messagebox.showerror("Invalid JSON", f"Error in details field: {e}")
        return
    data["accounts"][selected_account_email]["services"][selected_service_index] = updated_svc
    refresh_services_list()
    clear_service_form()

def delete_service():
    global selected_service_index
    if selected_account_email is None or selected_service_index is None:
        messagebox.showwarning("No Service Selected", "Select a service first.")
        return
    if messagebox.askyesno("Confirm Delete", "Delete the selected service?"):
        account = data["accounts"][selected_account_email]
        account["services"].pop(selected_service_index)
        refresh_services_list()
        clear_service_form()
        selected_service_index = None

def save_all():
    save_data(data)
    refresh_account_list()
    refresh_main_tree()
    if selected_account_email:
        idxs = [i for i, email in enumerate(accounts_listbox.get(0, tk.END)) if email == selected_account_email]
        if idxs:
            accounts_listbox.selection_clear(0, tk.END)
            accounts_listbox.selection_set(idxs[0])
            on_account_select(None)

# Bind listbox selections for CRUD tab
accounts_listbox.bind("<<ListboxSelect>>", on_account_select)
services_listbox.bind("<<ListboxSelect>>", on_service_select)
refresh_account_list()

# ---------------- Global Save Button ----------------
global_btn_frame = tk.Frame(root)
global_btn_frame.pack(side="bottom", fill="x", padx=10, pady=10)
save_all_btn = tk.Button(global_btn_frame, text="Save All Changes", command=save_all, font=("Helvetica", 12, "bold"))
save_all_btn.pack(side="left", padx=5)

root.mainloop()
