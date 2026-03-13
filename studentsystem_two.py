import customtkinter as ctk
import sqlite3
import hashlib
from tkinter import messagebox, ttk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ===================== ADMIN CREDENTIALS =====================
ADMIN_EMAIL    = "admin@school.ug"
ADMIN_PASSWORD = "Adm!n2025Secure"

class SchoolApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("School Management System")
        self.geometry("920x720")
        self.resizable(False, False)

        self.current_user = None
        self.student_tree = None
        self.grade_tree   = None
        self.add_subject_entry = None
        self.add_grade_entry   = None

        self.init_database()
        self.create_login_frame()

    # ===================== DATABASE =====================
    def init_database(self):
        conn = sqlite3.connect('school.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS students (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     email TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL,
                     student_id TEXT UNIQUE NOT NULL,
                     created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS grades (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     student_id INTEGER NOT NULL,
                     subject TEXT NOT NULL,
                     grade TEXT NOT NULL,
                     added_by TEXT,
                     added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                     FOREIGN KEY(student_id) REFERENCES students(id))''')
        conn.commit()
        conn.close()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ===================== LOGIN =====================
    def create_login_frame(self):
        self.clear_frame()
        ctk.CTkLabel(self, text="School Management System", font=("Arial", 26, "bold")).pack(pady=50)
        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email", width=340); self.email_entry.pack(pady=12)
        self.pass_entry  = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=340); self.pass_entry.pack(pady=12)
        ctk.CTkButton(self, text="Login", width=340, height=40, command=self.login).pack(pady=25)
        ctk.CTkButton(self, text="Register New Student", fg_color="transparent", command=self.create_register_frame).pack()

    def create_register_frame(self):
        self.clear_frame()
        ctk.CTkLabel(self, text="Register New Student", font=("Arial", 22, "bold")).pack(pady=40)

        self.reg_name       = ctk.CTkEntry(self, placeholder_text="Full Name", width=340); self.reg_name.pack(pady=10)
        self.reg_email      = ctk.CTkEntry(self, placeholder_text="Email", width=340); self.reg_email.pack(pady=10)
        self.reg_student_id = ctk.CTkEntry(self, placeholder_text="Student ID (e.g. 2025/HD05/001)", width=340); self.reg_student_id.pack(pady=10)
        self.reg_pass       = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=340); self.reg_pass.pack(pady=10)
        self.reg_pass2      = ctk.CTkEntry(self, placeholder_text="Confirm Password", show="*", width=340); self.reg_pass2.pack(pady=10)

        ctk.CTkButton(self, text="Create Account", width=340, command=self.register).pack(pady=25)
        ctk.CTkButton(self, text="← Back to Login", fg_color="transparent", command=self.create_login_frame).pack()

    def register(self):
        name   = self.reg_name.get().strip()
        email  = self.reg_email.get().strip().lower()
        sid    = self.reg_student_id.get().strip().upper()
        p1     = self.reg_pass.get()
        p2     = self.reg_pass2.get()

        if not all([name, email, sid, p1, p2]) or p1 != p2:
            messagebox.showwarning("Error", "All fields required and passwords must match")
            return

        conn = sqlite3.connect('school.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO students (name, email, password, student_id) VALUES (?,?,?,?)",
                      (name, email, self.hash_password(p1), sid))
            conn.commit()
            messagebox.showinfo("Success", "Account created! Login now.")
            self.create_login_frame()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email or Student ID already exists")
        finally:
            conn.close()

    # ===================== LOGIN LOGIC =====================
    def login(self):
        email    = self.email_entry.get().strip().lower()
        password = self.pass_entry.get().strip()
        if not email or not password:
            messagebox.showwarning("Error", "Email and password required")
            return

        hashed = self.hash_password(password)

        conn = sqlite3.connect('school.db')
        c = conn.cursor()

        if email == ADMIN_EMAIL and hashed == self.hash_password(ADMIN_PASSWORD):
            self.current_user = {"name": "Administrator", "email": email, "student_id": "ADMIN", "db_id": None}
            conn.close()
            self.create_admin_dashboard()
            return

        c.execute("SELECT id, name, email, student_id FROM students WHERE email=? AND password=?", (email, hashed))
        user = c.fetchone()
        conn.close()

        if user:
            self.current_user = {"db_id": user[0], "name": user[1], "email": user[2], "student_id": user[3]}
            self.create_student_dashboard()
        else:
            messagebox.showerror("Failed", "Invalid credentials")

    # ===================== STUDENT DASHBOARD =====================
    def create_student_dashboard(self):
        self.clear_frame()
        ctk.CTkLabel(self, text=f"Welcome, {self.current_user['name']}!", font=("Arial", 22, "bold")).pack(pady=40)

        f = ctk.CTkFrame(self); f.pack(pady=20, padx=50, fill="x")
        ctk.CTkLabel(f, text=f"Student ID : {self.current_user['student_id']}", font=("Arial", 14)).pack(anchor="w", pady=6)
        ctk.CTkLabel(f, text=f"Email      : {self.current_user['email']}",      font=("Arial", 14)).pack(anchor="w", pady=6)

        ctk.CTkButton(self, text="View My Grades", width=340, height=45, command=self.view_my_grades).pack(pady=30)
        ctk.CTkButton(self, text="Logout", width=340, fg_color="#D32F2F", command=self.logout).pack(pady=10)

    # ===================== ADMIN DASHBOARD =====================
    def create_admin_dashboard(self):
        self.clear_frame()
        ctk.CTkLabel(self, text="Admin Panel", font=("Arial", 26, "bold"), text_color="#FF6B6B").pack(pady=25)

        sf = ctk.CTkFrame(self); sf.pack(pady=10, padx=40, fill="x")
        self.search_entry = ctk.CTkEntry(sf, placeholder_text="Search name or email...", width=400); self.search_entry.pack(side="left", padx=10)
        ctk.CTkButton(sf, text="Search", width=120, command=lambda: self.load_students(self.search_entry.get().strip())).pack(side="left")

        tf = ctk.CTkScrollableFrame(self, height=320); tf.pack(pady=15, padx=40, fill="both", expand=True)

        self.student_tree = ttk.Treeview(tf, columns=("ID","Name","Email","Student ID"), show="headings")
        for col, txt, w, anc in [("ID", "ID", 60, "center"), ("Name","Name",180,"w"), ("Email","Email",220,"w"), ("Student ID","Student ID",140,"center")]:
            self.student_tree.heading(col, text=txt)
            self.student_tree.column(col, width=w, anchor=anc)
        self.student_tree.pack(fill="both", expand=True)

        bf = ctk.CTkFrame(self); bf.pack(pady=15)
        buttons = [
            ("Refresh", lambda: self.load_students(), None),
            ("Edit Selected", self.edit_student, None),
            ("Delete Selected", self.delete_student, "#D32F2F"),
            ("Manage Grades", self.manage_grades_for_selected, None),
            ("Logout", self.logout, "#D32F2F")
        ]
        for txt, cmd, fg in buttons:
            ctk.CTkButton(bf, text=txt, width=130, fg_color=fg, command=cmd).pack(side="left", padx=8)

        self.load_students()

    def load_students(self, search=""):
        if not self.student_tree: return
        for i in self.student_tree.get_children(): self.student_tree.delete(i)

        conn = sqlite3.connect('school.db')
        c = conn.cursor()
        q = "SELECT id, name, email, student_id FROM students"
        if search:
            q += " WHERE name LIKE ? OR email LIKE ?"
            c.execute(q + " ORDER BY id", (f"%{search}%", f"%{search}%"))
        else:
            c.execute(q + " ORDER BY id")
        for row in c.fetchall():
            self.student_tree.insert("", "end", values=row)
        conn.close()

    # ===================== GRADES WINDOW (fixed table visibility) =====================
    def manage_grades_for_selected(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a student")
            return
        v = self.student_tree.item(sel[0])['values']
        self.manage_grades_window(v[0], v[1], True)

    def view_my_grades(self):
        if 'db_id' not in self.current_user: return
        self.manage_grades_window(self.current_user['db_id'], self.current_user['name'], False)

    def manage_grades_window(self, student_db_id, student_name, is_admin):
        win = ctk.CTkToplevel(self)
        win.title(f"Grades — {student_name}")
        win.geometry("800x650")
        win.grab_set()

        ctk.CTkLabel(win, text=f"Grades for {student_name}", font=("Arial", 20, "bold")).pack(pady=20)

        mode = "ADMIN MODE (add/edit/delete enabled)" if is_admin else "VIEW ONLY"
        ctk.CTkLabel(win, text=mode, text_color="#4CAF50" if is_admin else "#FF9800",
                     font=("Arial", 13, "italic")).pack(pady=(0,20))

        # Add section – only admin
        if is_admin:
            addf = ctk.CTkFrame(win); addf.pack(pady=10, padx=50, fill="x")
            ctk.CTkLabel(addf, text="Add New Grade", font=("Arial", 16)).pack(pady=(0,12))

            row1 = ctk.CTkFrame(addf); row1.pack(fill="x", pady=5)
            ctk.CTkLabel(row1, text="Subject:").pack(side="left", padx=10)
            self.add_subject_entry = ctk.CTkEntry(row1, width=400); self.add_subject_entry.pack(side="left", fill="x", expand=True, padx=10)

            row2 = ctk.CTkFrame(addf); row2.pack(fill="x", pady=5)
            ctk.CTkLabel(row2, text="Grade:").pack(side="left", padx=10)
            self.add_grade_entry = ctk.CTkEntry(row2, width=400); self.add_grade_entry.pack(side="left", fill="x", expand=True, padx=10)

            ctk.CTkButton(addf, text="Add Grade", width=180, command=lambda: self._add_grade(student_db_id)).pack(pady=15)

        # Table section – always visible
        table_container = ctk.CTkFrame(win); table_container.pack(pady=10, padx=50, fill="both", expand=True)

        scroll_frame = ctk.CTkScrollableFrame(table_container); scroll_frame.pack(fill="both", expand=True)

        self.grade_tree = ttk.Treeview(scroll_frame, columns=("ID","Subject","Grade","By","Date"), show="headings")
        headings = ["ID", "Subject", "Grade", "Added By", "Date"]
        widths   = [50, 220, 100, 140, 180]
        anchors  = ["center", "w", "center", "w", "center"]
        for h, w, a, col in zip(headings, widths, anchors, self.grade_tree["columns"]):
            self.grade_tree.heading(col, text=h)
            self.grade_tree.column(col, width=w, anchor=a)

        self.grade_tree.pack(fill="both", expand=True, padx=5, pady=5)

        self._load_grades(student_db_id)

        # Buttons at bottom
        bf = ctk.CTkFrame(win); bf.pack(pady=20)
        if is_admin:
            ctk.CTkButton(bf, text="Edit Selected", command=lambda: self._edit_grade(student_db_id)).pack(side="left", padx=10)
            ctk.CTkButton(bf, text="Delete Selected", fg_color="#D32F2F", command=lambda: self._delete_grade(student_db_id)).pack(side="left", padx=10)
        ctk.CTkButton(bf, text="Close", command=win.destroy).pack(side="left", padx=10)

    def _add_grade(self, student_db_id):
        sub = (self.add_subject_entry or ctk.CTkEntry()).get().strip()
        gr  = (self.add_grade_entry   or ctk.CTkEntry()).get().strip()
        if not sub or not gr:
            messagebox.showwarning("Required", "Subject and Grade needed")
            return

        conn = sqlite3.connect('school.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO grades (student_id, subject, grade, added_by) VALUES (?,?,?,?)",
                      (student_db_id, sub, gr, self.current_user['email']))
            conn.commit()
            if self.add_subject_entry: self.add_subject_entry.delete(0, 'end')
            if self.add_grade_entry:   self.add_grade_entry.delete(0, 'end')
            self._load_grades(student_db_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def _load_grades(self, student_db_id):
        if not hasattr(self, 'grade_tree') or not self.grade_tree: return
        for i in self.grade_tree.get_children():
            self.grade_tree.delete(i)

        conn = sqlite3.connect('school.db')
        c = conn.cursor()
        c.execute("SELECT id, subject, grade, added_by, added_at FROM grades WHERE student_id = ? ORDER BY added_at DESC", (student_db_id,))
        rows = c.fetchall()
        for row in rows:
            self.grade_tree.insert("", "end", values=row)
        if not rows:
            self.grade_tree.insert("", "end", values=("", "No grades yet", "", "", ""))
        conn.close()

    # (edit_grade, delete_grade, edit_student, delete_student, logout functions remain the same as before)

    def logout(self):
        self.current_user = None
        self.create_login_frame()

    # ... (add the missing edit/delete student and grade functions from your previous version if needed)

if __name__ == "__main__":
    app = SchoolApp()
    app.mainloop()