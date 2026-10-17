
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import date

FILE = "tasks.json"

BG = "#F3F6FC"
BLUE = "#4F46E5"
DARK = "#172033"
GREEN = "#16A34A"
RED = "#DC2626"


class TaskFlow:
    def __init__(self, root):
        self.root = root
        self.root.title("TaskFlow | Student Task Manager")
        self.root.geometry("850x650")
        self.root.minsize(700, 550)
        self.root.configure(bg=BG)

        self.tasks = self.load_tasks()
        self.filter_var = tk.StringVar(value="All")

        self.build_ui()
        self.refresh_tasks()

    def load_tasks(self):
        if os.path.exists(FILE):
            try:
                with open(FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def save_tasks(self):
        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=4)

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BLUE, padx=25, pady=20)
        header.pack(fill="x")

        tk.Label(
            header, text="TaskFlow",
            font=("Segoe UI", 25, "bold"),
            bg=BLUE, fg="white"
        ).pack(anchor="w")

        tk.Label(
            header, text="Plan smarter. Achieve more.",
            font=("Segoe UI", 11),
            bg=BLUE, fg="#E0E7FF"
        ).pack(anchor="w")

        # Statistics
        stats = tk.Frame(self.root, bg=BG, padx=20, pady=15)
        stats.pack(fill="x")

        self.total_label = self.stat_card(stats, "TOTAL TASKS", "0")
        self.pending_label = self.stat_card(stats, "PENDING", "0")
        self.done_label = self.stat_card(stats, "COMPLETED", "0")

        # Add task section
        form = tk.Frame(self.root, bg="white", padx=18, pady=15)
        form.pack(fill="x", padx=20, pady=5)

        tk.Label(
            form, text="Add a New Task",
            font=("Segoe UI", 14, "bold"),
            bg="white", fg=DARK
        ).grid(row=0, column=0, columnspan=4,
               sticky="w", pady=(0, 12))

        self.task_entry = self.make_entry(
            form, "Task name"
        )
        self.task_entry.grid(
            row=1, column=0, sticky="ew", padx=(0, 8)
        )

        self.date_entry = self.make_entry(
            form, "YYYY-MM-DD"
        )
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(
            row=1, column=1, sticky="ew", padx=8
        )

        self.priority = ttk.Combobox(
            form, values=["Low", "Medium", "High"],
            state="readonly", width=9
        )
        self.priority.set("Medium")
        self.priority.grid(row=1, column=2, padx=8)

        tk.Button(
            form, text="+ Add Task",
            command=self.add_task,
            bg=BLUE, fg="white",
            activebackground="#3730A3",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat", padx=12, pady=8,
            cursor="hand2"
        ).grid(row=1, column=3, padx=(8, 0))

        form.columnconfigure(0, weight=3)
        form.columnconfigure(1, weight=2)

        # Task list heading and filter
        controls = tk.Frame(self.root, bg=BG, padx=22, pady=12)
        controls.pack(fill="x")

        tk.Label(
            controls, text="Your Tasks",
            font=("Segoe UI", 16, "bold"),
            bg=BG, fg=DARK
        ).pack(side="left")

        self.filter_box = ttk.Combobox(
            controls, textvariable=self.filter_var,
            values=["All", "Pending", "Completed"],
            state="readonly", width=12
        )
        self.filter_box.pack(side="right")
        self.filter_box.bind(
            "<<ComboboxSelected>>",
            lambda event: self.refresh_tasks()
        )

        # Scrollable task list
        container = tk.Frame(self.root, bg=BG)
        container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.canvas = tk.Canvas(
            container, bg=BG, highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            container, orient="vertical",
            command=self.canvas.yview
        )
        self.list_frame = tk.Frame(self.canvas, bg=BG)

        self.list_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.list_frame, anchor="nw"
        )
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(
                self.canvas_window, width=event.width
            )
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.bind(
            "<Enter>",
            lambda event: self.canvas.bind_all(
                "<MouseWheel>", self._on_mousewheel
            )
        )
        self.canvas.bind(
            "<Leave>",
            lambda event: self.canvas.unbind_all("<MouseWheel>")
        )


        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(
            self.root, text="TaskFlow • Stay organized, one task at a time.",
            bg=BG, fg="#64748B",
            font=("Segoe UI", 9)
        ).pack(pady=(0, 10))

    def stat_card(self, parent, title, value):
        card = tk.Frame(
            parent, bg="white", padx=15, pady=12
        )
        card.pack(side="left", fill="x", expand=True, padx=5)

        tk.Label(
            card, text=title, bg="white", fg="#64748B",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        number = tk.Label(
            card, text=value, bg="white", fg=BLUE,
            font=("Segoe UI", 22, "bold")
        )
        number.pack(anchor="w")
        return number

    def make_entry(self, parent, placeholder):
        entry = tk.Entry(
            parent, font=("Segoe UI", 10),
            relief="solid", bd=1
        )
        entry.insert(0, placeholder)

        def focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, "end")

        entry.bind("<FocusIn>", focus_in)
        return entry

    def add_task(self):
        name = self.task_entry.get().strip()
        deadline = self.date_entry.get().strip()

        if not name or name == "Task name":
            messagebox.showwarning(
                "Missing Task", "Please enter a task name."
            )
            return

        try:
            date.fromisoformat(deadline)
        except ValueError:
            messagebox.showwarning(
                "Invalid Date", "Use the YYYY-MM-DD format."
            )
            return

        self.tasks.append({
            "name": name,
            "deadline": deadline,
            "priority": self.priority.get(),
            "completed": False
        })

        self.save_tasks()
        self.task_entry.delete(0, "end")
        self.refresh_tasks()

    def toggle_task(self, task):
        task["completed"] = not task["completed"]
        self.save_tasks()
        self.refresh_tasks()

    def delete_task(self, task):
        if messagebox.askyesno(
            "Delete Task", f"Delete '{task['name']}'?"
        ):
            self.tasks.remove(task)
            self.save_tasks()
            self.refresh_tasks()
            
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)), "units"
        )


    def refresh_tasks(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        total = len(self.tasks)
        completed = sum(
            1 for task in self.tasks if task["completed"]
        )
        pending = total - completed

        self.total_label.config(text=str(total))
        self.pending_label.config(text=str(pending))
        self.done_label.config(text=str(completed))

        selected = self.filter_var.get()
        visible = [
            task for task in self.tasks
            if selected == "All"
            or (selected == "Pending" and not task["completed"])
            or (selected == "Completed" and task["completed"])
        ]

        if not visible:
            tk.Label(
                self.list_frame,
                text="No tasks here yet. Add your first task!",
                font=("Segoe UI", 11),
                bg=BG, fg="#64748B", pady=25
            ).pack(fill="x")
            return

        for task in reversed(visible):
            card = tk.Frame(
                self.list_frame, bg="white",
                padx=12, pady=10
            )
            card.pack(fill="x", pady=5)

            color = (
                GREEN if task["completed"]
                else RED if task["priority"] == "High"
                else "#D97706" if task["priority"] == "Medium"
                else BLUE
            )

            tk.Frame(
                card, bg=color, width=5
            ).pack(side="left", fill="y", padx=(0, 12))

            info = tk.Frame(card, bg="white")
            info.pack(side="left", fill="x", expand=True)

            name = task["name"]
            if task["completed"]:
                name = "✓ " + name

            tk.Label(
                info, text=name,
                font=("Segoe UI", 11, "bold"),
                bg="white",
                fg="#94A3B8" if task["completed"] else DARK,
                anchor="w", wraplength=350
            ).pack(anchor="w")

            tk.Label(
                info,
                text=f"Due: {task['deadline']}  |  "
                     f"Priority: {task['priority']}",
                font=("Segoe UI", 9),
                bg="white", fg="#64748B"
            ).pack(anchor="w", pady=(3, 0))

            tk.Button(
                card,
                text="Undo" if task["completed"] else "Done",
                command=lambda t=task: self.toggle_task(t),
                bg="#DCFCE7", fg="#166534",
                relief="flat", cursor="hand2", padx=8
            ).pack(side="right", padx=4)

            tk.Button(
                card, text="Delete",
                command=lambda t=task: self.delete_task(t),
                bg="#FEE2E2", fg="#991B1B",
                relief="flat", cursor="hand2", padx=8
            ).pack(side="right", padx=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskFlow(root)
    root.mainloop()
