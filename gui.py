import pandas as pd
pd.DataFrame(columns=['Date', 'UserID']).to_csv('attendance.csv', index=False)
pd.DataFrame(columns=['UserID', 'Name']).to_csv('users.csv', index=False)
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import threading
import recognize
import enrollment
import remove_face
import pandas as pd
import os

def threaded(func):
    def wrapper(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs).start()
    return wrapper

def enroll_user():
    # Ask for Name first
    name = simpledialog.askstring("Enroll", "Enter Name:")
    if not name or not name.strip().isalpha():
        messagebox.showerror("Error", "Name must have only letters (no numbers or symbols).")
        return
    # Ask for UserID next
    user_id = simpledialog.askstring("Enroll", "Enter UserID (only number, e.g. 4):")
    if not user_id or not user_id.isdigit():
        messagebox.showerror("Error", "You must enter a numeric UserID.")
        return
    user_id = int(user_id)
    # Save Name and UserID to users.csv
    users_csv = 'users.csv'
    if os.path.exists(users_csv):
        df_users = pd.read_csv(users_csv)
        df_users = df_users[df_users['UserID'] != user_id]  # remove old entry for re-enroll
    else:
        df_users = pd.DataFrame(columns=['UserID', 'Name'])
    df_users = pd.concat([df_users, pd.DataFrame([{'UserID':user_id, 'Name':name}])], ignore_index=True)
    df_users.to_csv(users_csv, index=False)
    threaded_enroll(user_id, name)

@threaded
def threaded_enroll(user_id, name):
    enrollment.run_enrollment(user_id)
    root.after(0, lambda: messagebox.showinfo("Done", f"Enrollment for User {user_id} ({name}) complete."))

def remove_user():
    uid = simpledialog.askstring("Remove", "Enter UserID to REMOVE (only number):")
    if not uid or not uid.isdigit():
        messagebox.showerror("Error", "You must enter a numeric UserID.")
        return
    user_id = int(uid)
    threaded_remove(user_id)

@threaded
def threaded_remove(user_id):
    count = remove_face.run_remove_user(user_id)
    root.after(0, lambda: messagebox.showinfo("Removed", f"Removed {count} face images for User {user_id}"))

@threaded
def start_attendance():
    recognize.run_attendance()

def show_attendance(today_only=True):
    if not os.path.exists("attendance.csv"):
        messagebox.showinfo("No Data", "No attendance marked yet!")
        return
    df = pd.read_csv("attendance.csv")
    if today_only and not df.empty:
        today = df['Date'].max()
        df = df[df['Date'] == today]
    if os.path.exists('users.csv'):
        users = pd.read_csv('users.csv')
        # Convert both UserID columns to string for exact match
        df['UserID'] = df['UserID'].astype(str)
        users['UserID'] = users['UserID'].astype(str)
        df = df.merge(users, how='left', on='UserID')
    else:
        df['Name'] = 'Unknown'
    window = tk.Toplevel(root)
    window.title("Attendance")
    tree = ttk.Treeview(window, columns=("Date", "UserID", "Name"), show="headings")
    tree.heading("Date", text="Date")
    tree.heading("UserID", text="User ID")
    tree.heading("Name", text="Name")
    for _, row in df.iterrows():
        tree.insert("", "end", values=(row["Date"], row["UserID"], row.get("Name", "Unknown")))
    tree.pack(fill="both", expand=True)
    scrollbar = tk.Scrollbar(window, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscroll=scrollbar.set)

# -------- GUI setup: right-side window --------
root = tk.Tk()
root.title("Face Recognition Attendance - Pro")
root.configure(bg="#23395d")

window_width = 600
window_height = 700
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = screen_width - window_width - 30  # rightmost + small margin
y = int((screen_height - window_height) / 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

title = tk.Label(root, text="Face Recognition Attendance", font=("Segoe UI", 22, "bold"), bg="#23395d", fg="#f9d342")
title.pack(pady=30)

frame = tk.Frame(root, bg="#193047")
frame.pack(pady=20, padx=30, fill="both", expand=True)

btn1 = tk.Button(frame, text="Start Attendance", font=("Segoe UI", 14), bg="#5daad7", fg="#fff", command=start_attendance, width=20, pady=10)
btn2 = tk.Button(frame, text="Enroll New User", font=("Segoe UI", 14), bg="#4bb543", fg="#fff", command=enroll_user, width=20, pady=10)
btn3 = tk.Button(frame, text="Remove User", font=("Segoe UI", 14), bg="#e43f5a", fg="#fff", command=remove_user, width=20, pady=10)
btn4 = tk.Button(frame, text="Show Today's Attendance", font=("Segoe UI", 14), bg="#f9d342", fg="#23395d", command=lambda: show_attendance(today_only=True), width=20, pady=10)
btn5 = tk.Button(frame, text="Show All Attendance", font=("Segoe UI", 14), bg="#f9d342", fg="#23395d", command=lambda: show_attendance(today_only=False), width=20, pady=10)
btn6 = tk.Button(frame, text="Quit", font=("Segoe UI", 14), bg="#23395d", fg="#fff", command=root.destroy, width=20, pady=10)

for btn in [btn1, btn2, btn3, btn4, btn5, btn6]:
    btn.pack(pady=7)

root.mainloop()