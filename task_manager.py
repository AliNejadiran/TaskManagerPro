from datetime import datetime, timedelta
import json
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# تنظیمات ظاهری CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

tasks = []

# -------------------- FUNCTIONS -------------------- #
def save_tasks():
    with open("tasks.json", "w") as file:
        json.dump(tasks, file, indent=2)

def load_tasks():
    try:
        with open("tasks.json", "r") as file:
            loaded_tasks = json.load(file)
        if isinstance(loaded_tasks, list):
            tasks.clear()
            tasks.extend(loaded_tasks)
    except FileNotFoundError:
        pass
    update_task_list()
    update_stats()

def add_task():
    task_text = entry.get()
    priority = priority_var.get()
    category = category_var.get()
    
    if use_deadline_var.get():
        due_date = date_entry.get()
        due_time = time_entry.get()
        datetime_due = f"{due_date} {due_time}"
    else:
        datetime_due = "No Deadline"
    
    if not task_text:
        messagebox.showwarning("Warning", "Please enter a task!")
        return
    
    task = {
        'task': task_text,
        'priority': priority,
        'due_date': datetime_due,
        'category': category,
        'completed': False,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    tasks.append(task)
    update_task_list()
    entry.delete(0, tk.END)
    save_tasks()
    update_stats()

def remove_task():
    try:
        selected_index = listbox.curselection()[0]
        real_index = get_real_index(selected_index)
        if real_index is not None:
            tasks.pop(real_index)
            update_task_list()
            save_tasks()
            update_stats()
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to remove!")

def edit_task():
    try:
        selected_index = listbox.curselection()[0]
        real_index = get_real_index(selected_index)
        if real_index is not None:
            new_task = entry.get()
            if new_task:
                tasks[real_index]["task"] = new_task
                update_task_list()
                save_tasks()
                entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Warning", "Enter new task text!")
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to edit!")

def complete_task():
    try:
        selected_index = listbox.curselection()[0]
        real_index = get_real_index(selected_index)
        if real_index is not None:
            tasks[real_index]['completed'] = not tasks[real_index].get('completed', False)
            update_task_list()
            save_tasks()
            update_stats()
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task!")

def update_task_priority():
    try:
        selected_index = listbox.curselection()[0]
        real_index = get_real_index(selected_index)
        if real_index is not None:
            tasks[real_index]["priority"] = priority_var.get()
            update_task_list()
            save_tasks()
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task!")

def update_task_category():
    try:
        selected_index = listbox.curselection()[0]
        real_index = get_real_index(selected_index)
        if real_index is not None:
            tasks[real_index]["category"] = category_var.get()
            update_task_list()
            save_tasks()
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task!")

def get_real_index(displayed_index):
    search_text = search_entry.get().lower()
    filter_priority = filter_priority_var.get()
    filter_category = filter_category_var.get()
    
    filtered_tasks = []
    for task in tasks:
        if search_text and search_text not in task['task'].lower():
            continue
        if filter_priority != "All" and task['priority'] != filter_priority:
            continue
        if filter_category != "All" and task.get('category', 'Personal') != filter_category:
            continue
        filtered_tasks.append(task)
    
    if 0 <= displayed_index < len(filtered_tasks):
        return tasks.index(filtered_tasks[displayed_index])
    return None

def update_task_list():
    listbox.delete(0, tk.END)
    
    search_text = search_entry.get().lower()
    filter_priority = filter_priority_var.get()
    filter_category = filter_category_var.get()
    
    for task in tasks:
        if search_text and search_text not in task['task'].lower():
            continue
        if filter_priority != "All" and task['priority'] != filter_priority:
            continue
        if filter_category != "All" and task.get('category', 'Personal') != filter_category:
            continue
        
        status = "✅ " if task.get('completed', False) else "❌ "
        category = task.get('category', 'Personal')
        
        countdown = ""
        if task['due_date'] != "No Deadline":
            try:
                due = datetime.strptime(task['due_date'], "%Y-%m-%d %H:%M")
                now = datetime.now()
                if due > now:
                    remaining = due - now
                    days = remaining.days
                    hours = remaining.seconds // 3600
                    mins = (remaining.seconds % 3600) // 60
                    countdown = f" [⏳ {days}d {hours}h {mins}m left]"
                elif due < now:
                    countdown = " [⏰ OVERDUE]"
                else:
                    countdown = " [🔔 DUE NOW]"
            except:
                pass
        
        display_text = f"{status}{task['task']} | {task['priority']} | {category} | Due: {task['due_date']}{countdown}"
        listbox.insert(tk.END, display_text)
        
        if task['priority'] == "High":
            listbox.itemconfig(tk.END, fg='#d63031')
        elif task['priority'] == "Medium":
            listbox.itemconfig(tk.END, fg='#fdcb6e')
        else:
            listbox.itemconfig(tk.END, fg='#10B981')
        
        if task.get('completed', False):
            listbox.itemconfig(tk.END, overstrike=1)

def sort_by_priority():
    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    tasks.sort(key=lambda x: priority_order.get(x['priority'], 99))
    update_task_list()
    save_tasks()

def sort_by_due_date():
    def due_key(task):
        if task['due_date'] == "No Deadline":
            return "9999-12-31 23:59"
        return task['due_date']
    tasks.sort(key=due_key)
    update_task_list()
    save_tasks()

def sort_by_category():
    tasks.sort(key=lambda x: x.get('category', 'Personal'))
    update_task_list()
    save_tasks()

def apply_filters(event=None):
    update_task_list()
    update_stats()

def clear_filters():
    search_entry.delete(0, tk.END)
    filter_priority_var.set("All")
    filter_category_var.set("All")
    update_task_list()
    update_stats()

def update_stats():
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get('completed', False))
    pending = total - completed
    stats_label.configure(text=f"📊 Total: {total} | ✅ Completed: {completed} | ⏳ Pending: {pending}")
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_tasks = sum(1 for t in tasks if t['due_date'] != "No Deadline" and t['due_date'].startswith(today))
    today_label.configure(text=f"📅 Today: {today_tasks}")

def clear_entry():
    entry.delete(0, tk.END)

def on_task_select(event):
    try:
        selected_index = listbox.curselection()[0]
        real_index = get_real_index(selected_index)
        if real_index is not None:
            entry.delete(0, tk.END)
            entry.insert(0, tasks[real_index]['task'])
            priority_var.set(tasks[real_index]['priority'])
            category_var.set(tasks[real_index].get('category', 'Personal'))
    except:
        pass

def toggle_deadline():
    if use_deadline_var.get():
        deadline_frame.pack(fill='x', padx=20, pady=(5, 10))
    else:
        deadline_frame.pack_forget()

def update_countdown_timer():
    update_task_list()
    root.after(60000, update_countdown_timer)

# -------------------- GUI با چیدمان حرفه‌ای -------------------- #
root = ctk.CTk()
root.title("Task Manager Pro")
root.geometry("1100x800")
root.minsize(900, 600)

# ========== تم نارنجی-طلایی ==========
bg_color = "#0F0F0F"
card_color = "#1A1A1A"
accent_color = "#F97316"
text_color = "#FFFFFF"
text_secondary = "#A1A1AA"
complete_color = "#F59E0B"
delete_color = "#EF4444"
warning_color = "#F97316"
info_color = "#3B82F6"
success_color = "#10B981"

ctk.set_appearance_mode("dark")

# ========== هدر ==========
header = ctk.CTkFrame(root, fg_color=card_color, corner_radius=15)
header.pack(fill='x', padx=20, pady=(20, 10))

title = ctk.CTkLabel(header, text="✨ Task Manager Pro", font=ctk.CTkFont(size=28, weight="bold"), text_color=accent_color)
title.pack(pady=(20, 5))

subtitle = ctk.CTkLabel(header, text="Organize your tasks efficiently", font=ctk.CTkFont(size=12), text_color=text_secondary)
subtitle.pack(pady=(0, 15))

# ========== ردیف آمار و سورت (کنار هم) ==========
top_row = ctk.CTkFrame(root, fg_color="transparent")
top_row.pack(fill='x', padx=20, pady=(0, 10))

# آمار سمت چپ
stats_frame = ctk.CTkFrame(top_row, fg_color="transparent")
stats_frame.pack(side='left', fill='x', expand=True)

stats_label = ctk.CTkLabel(stats_frame, text="📊 Total: 0 | ✅ Completed: 0 | ⏳ Pending: 0",
                           font=ctk.CTkFont(size=13, weight="bold"), text_color=complete_color)
stats_label.pack(side='left')

today_label = ctk.CTkLabel(stats_frame, text="📅 Today: 0",
                           font=ctk.CTkFont(size=13, weight="bold"), text_color=warning_color)
today_label.pack(side='left', padx=(15, 0))

# دکمه‌های سورت سمت راست (بالا)
sort_frame = ctk.CTkFrame(top_row, fg_color="transparent")
sort_frame.pack(side='right')

sort_buttons = [
    ("🔄 Sort Priority", sort_by_priority),
    ("📅 Sort Due Date", sort_by_due_date),
    ("📂 Sort Category", sort_by_category),
]

for text, cmd in sort_buttons:
    btn = ctk.CTkButton(sort_frame, text=text, command=cmd, fg_color=info_color, height=32,
                         font=ctk.CTkFont(size=11, weight="bold"), width=130)
    btn.pack(side='left', padx=3)

# ========== کارت افزودن تسک ==========
input_card = ctk.CTkFrame(root, fg_color=card_color, corner_radius=15)
input_card.pack(fill='x', padx=20, pady=10)

ctk.CTkLabel(input_card, text="➕ Add New Task", font=ctk.CTkFont(size=18, weight="bold"), text_color=accent_color).pack(anchor='w', padx=20, pady=(15, 10))

# Task Name
ctk.CTkLabel(input_card, text="Task Name:", font=ctk.CTkFont(size=12)).pack(anchor='w', padx=20)
entry = ctk.CTkEntry(input_card, height=40, font=ctk.CTkFont(size=13), fg_color=bg_color, border_color=accent_color)
entry.pack(fill='x', padx=20, pady=(5, 10))

# ردیف اولویت و دسته
row1 = ctk.CTkFrame(input_card, fg_color="transparent")
row1.pack(fill='x', padx=20, pady=5)

ctk.CTkLabel(row1, text="Priority:", font=ctk.CTkFont(size=12)).pack(side='left', padx=(0, 10))
priority_var = ctk.StringVar(value="Medium")

priority_frame = ctk.CTkFrame(row1, fg_color="transparent")
priority_frame.pack(side='left', padx=(0, 30))

ctk.CTkRadioButton(priority_frame, text="High", variable=priority_var, value="High", fg_color=delete_color, hover_color=delete_color).pack(side='left', padx=5)
ctk.CTkRadioButton(priority_frame, text="Medium", variable=priority_var, value="Medium", fg_color=warning_color, hover_color=warning_color).pack(side='left', padx=5)
ctk.CTkRadioButton(priority_frame, text="Low", variable=priority_var, value="Low", fg_color=success_color, hover_color=success_color).pack(side='left', padx=5)

ctk.CTkLabel(row1, text="Category:", font=ctk.CTkFont(size=12)).pack(side='left', padx=(0, 10))
category_var = ctk.StringVar(value="Personal")
category_options = ["Personal", "Work", "Shopping", "Health", "Education"]
category_menu = ctk.CTkOptionMenu(row1, variable=category_var, values=category_options, width=120, fg_color=accent_color, button_color=accent_color)
category_menu.pack(side='left')

# ددلاین چک‌باکس
use_deadline_var = ctk.BooleanVar(value=False)
deadline_check = ctk.CTkCheckBox(input_card, text="📅 Set Deadline (Date & Time)", variable=use_deadline_var,
                                  command=toggle_deadline, fg_color=accent_color, hover_color=accent_color)
deadline_check.pack(anchor='w', padx=20, pady=(10, 5))

# فریم ددلاین (مخفی در ابتدا)
deadline_frame = ctk.CTkFrame(input_card, fg_color=bg_color, corner_radius=10)

date_entry = ctk.CTkEntry(deadline_frame, placeholder_text="YYYY-MM-DD", width=120)
date_entry.pack(side='left', padx=5)
date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

time_entry = ctk.CTkEntry(deadline_frame, placeholder_text="HH:MM", width=80)
time_entry.pack(side='left', padx=5)
time_entry.insert(0, "23:59")

# دکمه Add
add_btn = ctk.CTkButton(input_card, text="➕ Add Task", command=add_task, height=40,
                         font=ctk.CTkFont(size=13, weight="bold"), fg_color=accent_color, hover_color=complete_color)
add_btn.pack(fill='x', padx=20, pady=(15, 15))

# ========== کارت جستجو و فیلتر ==========
filter_card = ctk.CTkFrame(root, fg_color=card_color, corner_radius=15)
filter_card.pack(fill='x', padx=20, pady=5)

ctk.CTkLabel(filter_card, text="🔍 Search & Filter", font=ctk.CTkFont(size=15, weight="bold"), text_color=accent_color).pack(anchor='w', padx=20, pady=(10, 5))

filter_row = ctk.CTkFrame(filter_card, fg_color="transparent")
filter_row.pack(fill='x', padx=20, pady=(0, 10))

ctk.CTkLabel(filter_row, text="Search:").pack(side='left', padx=(0, 5))
search_entry = ctk.CTkEntry(filter_row, width=180)
search_entry.pack(side='left', padx=(0, 15))
search_entry.bind('<KeyRelease>', apply_filters)

ctk.CTkLabel(filter_row, text="Priority:").pack(side='left', padx=(0, 5))
filter_priority_var = ctk.StringVar(value="All")
filter_priority_menu = ctk.CTkOptionMenu(filter_row, variable=filter_priority_var,
                                          values=["All", "High", "Medium", "Low"], width=100, fg_color=accent_color, button_color=accent_color)
filter_priority_menu.pack(side='left', padx=(0, 15))
filter_priority_var.trace('w', lambda *args: apply_filters())

ctk.CTkLabel(filter_row, text="Category:").pack(side='left', padx=(0, 5))
filter_category_var = ctk.StringVar(value="All")
filter_category_menu = ctk.CTkOptionMenu(filter_row, variable=filter_category_var,
                                          values=["All", "Personal", "Work", "Shopping", "Health", "Education"], width=120, fg_color=accent_color, button_color=accent_color)
filter_category_menu.pack(side='left')
filter_category_var.trace('w', lambda *args: apply_filters())

# ========== کارت لیست تسک‌ها ==========
list_card = ctk.CTkFrame(root, fg_color=card_color, corner_radius=15)
list_card.pack(fill='both', expand=True, padx=20, pady=10)

ctk.CTkLabel(list_card, text="📋 Your Tasks", font=ctk.CTkFont(size=16, weight="bold"), text_color=accent_color).pack(anchor='w', padx=20, pady=(10, 5))

# لیست باکس با اسکرول
list_container = ctk.CTkFrame(list_card, fg_color=bg_color, corner_radius=10)
list_container.pack(fill='both', expand=True, padx=15, pady=(0, 10))

scrollbar = ctk.CTkScrollbar(list_container, orientation="vertical", fg_color=bg_color, button_color=accent_color)
scrollbar.pack(side='right', fill='y')

listbox = tk.Listbox(list_container, bg=bg_color, fg=text_color,
                     selectbackground=accent_color, selectforeground='white',
                     font=("Segoe UI", 10), relief='flat', borderwidth=0,
                     yscrollcommand=scrollbar.set, height=12)
listbox.pack(side='left', fill='both', expand=True, padx=5, pady=5)
scrollbar.configure(command=listbox.yview)
listbox.bind('<<ListboxSelect>>', on_task_select)

# ========== ردیف دکمه‌های عملیاتی ==========
action_frame = ctk.CTkFrame(root, fg_color="transparent")
action_frame.pack(fill='x', padx=20, pady=(5, 5))

action_buttons = [
    ("✅ Complete", complete_task, complete_color),
    ("✏️ Edit", edit_task, warning_color),
    ("🗑️ Remove", remove_task, delete_color),
    ("🏷️ Update Priority", update_task_priority, accent_color),
    ("📁 Update Category", update_task_category, info_color),
]

for text, cmd, color in action_buttons:
    btn = ctk.CTkButton(action_frame, text=text, command=cmd, fg_color=color, height=35,
                         font=ctk.CTkFont(size=11, weight="bold"), hover_color=color)
    btn.pack(side='left', padx=3, expand=True, fill='x')

# ========== ردیف پایین (Clear ها) ==========
bottom_frame = ctk.CTkFrame(root, fg_color="transparent")
bottom_frame.pack(fill='x', padx=20, pady=(5, 15))

clear_buttons = [
    ("🧹 Clear Entry", clear_entry, text_secondary),
    ("🗑️ Clear Filters", clear_filters, delete_color),
]

for text, cmd, color in clear_buttons:
    btn = ctk.CTkButton(bottom_frame, text=text, command=cmd, fg_color=color, height=35,
                         font=ctk.CTkFont(size=11, weight="bold"), width=150)
    btn.pack(side='left', padx=5)

# ========== فوتر ==========
footer = ctk.CTkFrame(root, fg_color="transparent", height=30)
footer.pack(fill='x', side='bottom')

ctk.CTkLabel(footer, text="💪 Stay organized, stay productive | Countdown updates every minute",
             font=ctk.CTkFont(size=10), text_color=text_secondary).pack(pady=5)

# بارگذاری اولیه
load_tasks()
update_countdown_timer()

root.mainloop()