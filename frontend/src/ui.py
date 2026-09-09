import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox
from src import api


class App(tk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        master.title("Prevently")
        master.minsize(820, 560)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        self._build_dashboard_tab(notebook)
        self._build_details_tab(notebook)
        self._build_feature_tab(notebook)

        self._refresh_all()

    # ------------------------------------------------------------------
    # Dashboard tab
    # ------------------------------------------------------------------

    def _build_dashboard_tab(self, notebook: ttk.Notebook):
        dashboard_tab = ttk.Frame(notebook)
        notebook.add(dashboard_tab, text="Dashboard")

        ttk.Label(dashboard_tab, text="Nutzer:").grid(
            row=0, column=0, padx=8, pady=8, sticky=tk.E)

        self._user_combo = ttk.Combobox(dashboard_tab, state="readonly", width=30)
        self._user_combo.grid(row=0, column=1, padx=8, pady=8, sticky=tk.W)
        self._user_combo.bind("<<ComboboxSelected>>", self._on_user_selected)

        self._users = []
        self._current_user_id = None
        self._due_checkups = []
        self._completed_checkups = []

        ttk.Label(dashboard_tab, text="Offene Checkups:").grid(
            row=1, column=0, padx=8, pady=(8, 0), sticky=tk.W)

        due_columns = [
            ("title", "Checkup", 200),
            ("overdue_since", "Überfällig seit", 130),
            ("coverage_amount", "Coverage", 100),
        ]
        self._due_tree = ttk.Treeview(
            dashboard_tab, columns=[c[0] for c in due_columns], show="headings", height=8)
        for col, heading, width in due_columns:
            self._due_tree.heading(col, text=heading)
            self._due_tree.column(col, width=width)
        self._due_tree.grid(row=2, column=0, columnspan=2, padx=8, pady=(0, 8), sticky="nsew")
        self._due_tree.bind("<<TreeviewSelect>>", self._on_due_checkup_selected)

        ttk.Label(dashboard_tab, text="Erledigte Checkups:").grid(
            row=3, column=0, padx=8, pady=(8, 0), sticky=tk.W)

        completed_columns = [
            ("title", "Checkup", 180),
            ("completed_date", "Datum", 100),
            ("doctor_name", "Arzt", 150),
        ]
        self._completed_tree = ttk.Treeview(
            dashboard_tab, columns=[c[0] for c in completed_columns], show="headings", height=8)
        for col, heading, width in completed_columns:
            self._completed_tree.heading(col, text=heading)
            self._completed_tree.column(col, width=width)
        self._completed_tree.grid(row=4, column=0, columnspan=2, padx=8, pady=(0, 8), sticky="nsew")

        mark_frame = ttk.LabelFrame(
            dashboard_tab, text=" Ausgewählten Checkup als erledigt markieren (POST /completed-checkups) ")
        mark_frame.grid(row=5, column=0, columnspan=2, padx=8, pady=8, sticky="ew")

        ttk.Label(mark_frame, text="Arzt:").grid(
            row=0, column=0, padx=8, pady=4, sticky=tk.E)

        self._mark_doctor_combo = ttk.Combobox(mark_frame, state="readonly", width=30)
        self._mark_doctor_combo.grid(row=0, column=1, padx=8, pady=4, sticky=tk.W)

        self._mark_doctors = []

        self._mark_date_entry = self._labeled_entry(mark_frame, "Datum (YYYY-MM-DD)", 1)
        self._mark_date_entry.insert(0, date.today().isoformat())

        ttk.Button(mark_frame, text="Markieren", command=self._mark_completed).grid(
            row=2, column=0, columnspan=2, pady=8)

    def _load_dashboard(self):
        self._users = api.get_users()
        names = [f"{u['first_name']} {u['last_name']}" for u in self._users]
        self._user_combo["values"] = names
        if names:
            self._user_combo.current(0)
            self._on_user_selected()

    def _on_user_selected(self, event=None):
        index = self._user_combo.current()
        if index == -1:
            return
        self._current_user_id = self._users[index]["user_id"]
        self._refresh_due_checkups()
        self._refresh_completed_checkups()

    def _refresh_due_checkups(self):
        self._due_tree.delete(*self._due_tree.get_children())
        self._due_checkups = api.get_due_checkups(self._current_user_id)
        for checkup in self._due_checkups:
            overdue_since = checkup.get("overdue_since", "–")
            coverage = checkup.get("coverage_amount", "–")
            self._due_tree.insert(
                "", tk.END, values=(checkup["title"], overdue_since, coverage))

    def _refresh_completed_checkups(self):
        self._completed_tree.delete(*self._completed_tree.get_children())
        self._completed_checkups = api.get_completed_checkups(self._current_user_id)
        for checkup in self._completed_checkups:
            completed_date = checkup.get("completed_date", "–")
            doctor_name = checkup.get("doctor_name", "–")
            self._completed_tree.insert(
                "", tk.END, values=(checkup["title"], completed_date, doctor_name))

    def _on_due_checkup_selected(self, event=None):
        selection = self._due_tree.selection()
        if not selection:
            return
        index = self._due_tree.index(selection[0])
        checkup = self._due_checkups[index]
        try:
            self._mark_doctors = api.get_doctors_for_checkup(checkup["checkup_id"])
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
            return
        names = [d.get("d_name", str(d)) for d in self._mark_doctors]
        self._mark_doctor_combo["values"] = names
        if names:
            self._mark_doctor_combo.current(0)
        else:
            self._mark_doctor_combo.set("")

    def _mark_completed(self):
        selection = self._due_tree.selection()
        if not selection or self._current_user_id is None:
            messagebox.showwarning("Auswahl fehlt", "Bitte zuerst einen offenen Checkup auswählen.")
            return
        doctor_index = self._mark_doctor_combo.current()
        if doctor_index == -1:
            messagebox.showwarning("Auswahl fehlt", "Bitte einen Arzt auswählen.")
            return
        index = self._due_tree.index(selection[0])
        checkup = self._due_checkups[index]
        try:
            doctor_id = self._mark_doctors[doctor_index]["doctor_id"]
            completed_date = date.fromisoformat(self._mark_date_entry.get())
            api.post_completed_checkup(
                user_id=self._current_user_id,
                doctor_id=doctor_id,
                checkup_id=checkup["checkup_id"],
                completed_date=completed_date,
            )
            messagebox.showinfo("Erfolg", "Checkup wurde als erledigt markiert.")
            self._refresh_due_checkups()
            self._refresh_completed_checkups()
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    # ------------------------------------------------------------------
    # Details tab
    # ------------------------------------------------------------------

    def _build_details_tab(self, notebook: ttk.Notebook):
        details_tab = ttk.Frame(notebook)
        notebook.add(details_tab, text="Details")

        create_user_frame = ttk.LabelFrame(details_tab, text=" Neuen Nutzer anlegen (POST /users) ")
        create_user_frame.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

        self._new_first_name_entry = self._labeled_entry(create_user_frame, "Vorname", 0)
        self._new_last_name_entry = self._labeled_entry(create_user_frame, "Nachname", 1)
        self._new_dob_entry = self._labeled_entry(create_user_frame, "Geburtsdatum (YYYY-MM-DD)", 2)
        self._new_gender_entry = self._labeled_entry(create_user_frame, "Geschlecht", 3)

        ttk.Label(create_user_frame, text="Versicherung:").grid(
            row=4, column=0, padx=8, pady=4, sticky=tk.E)

        self._new_insurance_combo = ttk.Combobox(create_user_frame, state="readonly", width=30)
        self._new_insurance_combo.grid(row=4, column=1, padx=8, pady=4, sticky=tk.W)

        ttk.Button(create_user_frame, text="Anlegen", command=self._create_user).grid(
            row=5, column=0, columnspan=2, pady=8)

        book_frame = ttk.LabelFrame(details_tab, text=" Termin buchen (POST /appointments) ")
        book_frame.grid(row=1, column=0, padx=8, pady=8, sticky="ew")

        self._appt_user_entry = self._labeled_entry(book_frame, "User ID", 0)
        self._appt_doctor_entry = self._labeled_entry(book_frame, "Doctor ID", 1)
        self._appt_checkup_entry = self._labeled_entry(book_frame, "Checkup ID", 2)
        self._appt_date_entry = self._labeled_entry(book_frame, "Datum (YYYY-MM-DD)", 3)
        self._appt_duration_entry = self._labeled_entry(book_frame, "Dauer (Minuten)", 4)

        ttk.Button(book_frame, text="Buchen", command=self._book_appointment).grid(
            row=5, column=0, columnspan=2, pady=8)

    def _load_details(self):
        self._new_user_insurance_providers = api.get_insurance_providers()
        names = [ip.get("i_name", str(ip)) for ip in self._new_user_insurance_providers]
        self._new_insurance_combo["values"] = names
        if names:
            self._new_insurance_combo.current(0)

    def _create_user(self):
        try:
            insurance_index = self._new_insurance_combo.current()
            if insurance_index == -1:
                messagebox.showwarning("Auswahl fehlt", "Bitte eine Versicherung auswählen.")
                return
            first_name = self._new_first_name_entry.get()
            last_name = self._new_last_name_entry.get()
            date_of_birth = date.fromisoformat(self._new_dob_entry.get())
            gender = self._new_gender_entry.get()
            insurance_id = self._new_user_insurance_providers[insurance_index]["insurance_id"]
            api.post_user(first_name, last_name, date_of_birth, gender, insurance_id)
            messagebox.showinfo("Erfolg", "Nutzer wurde angelegt.")
            self._load_dashboard()
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def _book_appointment(self):
        try:
            user_id = int(self._appt_user_entry.get())
            doctor_id = int(self._appt_doctor_entry.get())
            checkup_id = int(self._appt_checkup_entry.get())
            checkup_date = date.fromisoformat(self._appt_date_entry.get())
            duration = int(self._appt_duration_entry.get())
            api.post_appointment(user_id, doctor_id, checkup_id, checkup_date, duration)
            messagebox.showinfo("Erfolg", "Termin wurde gebucht.")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    # ------------------------------------------------------------------
    # Feature tab
    # ------------------------------------------------------------------

    def _build_feature_tab(self, notebook: ttk.Notebook):
        feature_tab = ttk.Frame(notebook)
        notebook.add(feature_tab, text="Feature")

        doctor_frame = ttk.LabelFrame(
            feature_tab, text=" Ärzte für Checkup suchen (GET /checkups/{id}/doctors) ")
        doctor_frame.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

        ttk.Label(doctor_frame, text="Checkup:").grid(
            row=0, column=0, padx=8, pady=4, sticky=tk.E)

        self._doctor_checkup_combo = ttk.Combobox(doctor_frame, state="readonly", width=30)
        self._doctor_checkup_combo.grid(row=0, column=1, padx=8, pady=4, sticky=tk.W)

        self._checkups = []

        self._doctor_location_entry = self._labeled_entry(doctor_frame, "Ort (optional)", 1)

        ttk.Button(doctor_frame, text="Suchen", command=self._search_doctors).grid(
            row=2, column=0, columnspan=2, pady=8)

        doctor_columns = [
            ("doctor_id", "ID", 50),
            ("name", "Name", 160),
            ("location", "Ort", 140),
        ]
        self._doctor_tree = ttk.Treeview(
            feature_tab, columns=[c[0] for c in doctor_columns], show="headings", height=6)
        for col, heading, width in doctor_columns:
            self._doctor_tree.heading(col, text=heading)
            self._doctor_tree.column(col, width=width)
        self._doctor_tree.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

        insurance_frame = ttk.LabelFrame(
            feature_tab, text=" Checkups einer Versicherung (GET /insurance-providers/{id}/checkups) ")
        insurance_frame.grid(row=3, column=0, padx=8, pady=8, sticky="ew")

        ttk.Label(insurance_frame, text="Versicherung:").grid(
            row=0, column=0, padx=8, pady=4, sticky=tk.E)

        self._insurance_combo = ttk.Combobox(insurance_frame, state="readonly", width=30)
        self._insurance_combo.grid(row=0, column=1, padx=8, pady=4, sticky=tk.W)

        ttk.Button(insurance_frame, text="Anzeigen", command=self._search_insurance_checkups).grid(
            row=1, column=0, columnspan=2, pady=8)

        checkup_columns = [
            ("checkup_id", "ID", 50),
            ("title", "Titel", 200),
            ("coverage_amount", "Coverage [€]", 100),
        ]
        self._insurance_tree = ttk.Treeview(
            feature_tab, columns=[c[0] for c in checkup_columns], show="headings", height=6)
        for col, heading, width in checkup_columns:
            self._insurance_tree.heading(col, text=heading)
            self._insurance_tree.column(col, width=width)
        self._insurance_tree.grid(row=4, column=0, padx=8, pady=8, sticky="nsew")

        self._insurance_providers = []

    def _load_feature(self):
        self._insurance_providers = api.get_insurance_providers()
        insurance_names = [ip.get("i_name", str(ip)) for ip in self._insurance_providers]
        self._insurance_combo["values"] = insurance_names
        if insurance_names:
            self._insurance_combo.current(0)

        self._checkups = api.get_checkups()
        checkup_names = [c.get("title", str(c)) for c in self._checkups]
        self._doctor_checkup_combo["values"] = checkup_names
        if checkup_names:
            self._doctor_checkup_combo.current(0)

    def _search_doctors(self):
        checkup_index = self._doctor_checkup_combo.current()
        if checkup_index == -1:
            messagebox.showwarning("Auswahl fehlt", "Bitte zuerst einen Checkup auswählen.")
            return
        try:
            checkup_id = self._checkups[checkup_index]["checkup_id"]
            location = self._doctor_location_entry.get().strip() or None
            doctors = api.get_doctors_for_checkup(checkup_id, location)
            self._doctor_tree.delete(*self._doctor_tree.get_children())
            for doc in doctors:
                self._doctor_tree.insert(
                    "", tk.END,
                    values=(doc.get("doctor_id", ""), doc.get("d_name", ""), doc.get("location", "")))
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def _search_insurance_checkups(self):
        index = self._insurance_combo.current()
        if index == -1:
            messagebox.showwarning("Auswahl fehlt", "Bitte zuerst eine Versicherung auswählen.")
            return
        try:
            insurance_id = self._insurance_providers[index]["insurance_id"]
            checkups = api.get_insurance_checkups(insurance_id)
            self._insurance_tree.delete(*self._insurance_tree.get_children())
            for checkup in checkups:
                self._insurance_tree.insert(
                    "", tk.END,
                    values=(checkup.get("checkup_id", ""), checkup.get("title", ""),
                            checkup.get("coverage_amount", "")))
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _labeled_entry(self, parent, label: str, row: int) -> ttk.Entry:
        ttk.Label(parent, text=label + ":").grid(
            row=row, column=0, padx=8, pady=4, sticky=tk.E)
        entry = ttk.Entry(parent, width=30)
        entry.grid(row=row, column=1, padx=8, pady=4, sticky=tk.W)
        return entry

    def _refresh_all(self):
        self._load_dashboard()
        self._load_details()
        self._load_feature()
