
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DB_PATH = "rendezvous.db"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestion des rendez-vous")
        self.geometry("950x600")
        self._create_widgets()
        self._init_db()
        self.selected_id = None
        self._load_rows()

    # ---------- Base de données ----------


    # ---------- Interface graphique ----------

    def _create_widgets(self):

        # Configuration de la fenêtre
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Formulaire
        form = ttk.LabelFrame(self, text="Informations du rendez-vous")
        form.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        # Ligne 0 : Client et activité
        ttk.Label(form, text="Nom du client :").grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.ent_client = ttk.Entry(form)
        self.ent_client.grid(row=0, column=1, padx=5, pady=8, sticky="ew")

        ttk.Label(form, text="Activité :").grid(row=0, column=2, padx=5, pady=8, sticky="w")
        self.combo_activite = ttk.Combobox(form, values=["Natation", "Yoga", "Musculation", "Tennis", "Fitness"], state="readonly")
        self.combo_activite.grid(row=0, column=3, padx=5, pady=8, sticky="ew")

        # Ligne 1 : Date et heure
        ttk.Label(form, text="Date (AAAA-MM-JJ) :").grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.ent_date = ttk.Entry(form)
        self.ent_date.grid(row=1, column=1, padx=5, pady=8, sticky="ew")

        ttk.Label(form, text="Heure (HH:MM) :").grid(row=1, column=2, padx=5, pady=8, sticky="w")
        self.ent_heure = ttk.Entry(form)
        self.ent_heure.grid(row=1, column=3, padx=5, pady=8, sticky="ew")

        # Ligne 2 : Durée et statut
        ttk.Label(form, text="Durée (minutes) :").grid(row=2, column=0, padx=5, pady=8, sticky="w")
        self.ent_duree = ttk.Entry(form)
        self.ent_duree.grid(row=2, column=1, padx=5, pady=8, sticky="ew")

        ttk.Label(form, text="Statut :").grid(row=2, column=2, padx=5, pady=8, sticky="w")
        self.combo_statut = ttk.Combobox(form, values=["En attente", "Confirmé", "Annulé"], state="readonly")
        self.combo_statut.grid(row=2, column=3, padx=5, pady=8, sticky="ew")

        # Boutons
        btns = ttk.Frame(form)
        btns.grid(row=3, column=0, columnspan=4, pady=12)

        ttk.Button(btns, text="Nouveau", command=self._on_new).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Ajouter", command=self._on_add).grid(row=0, column=1, padx=5)
        ttk.Button(btns, text="Modifier", command=self._on_update).grid(row=0, column=2, padx=5)
        ttk.Button(btns, text="Supprimer", command=self._on_delete).grid(row=0, column=3, padx=5)

        # Tableau
        table_frame = ttk.LabelFrame(self, text="Liste des rendez-vous")
        table_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        cols = ("id", "client", "activite", "date", "heure", "duree", "statut")

        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("client", text="Client")
        self.tree.heading("activite", text="Activité")
        self.tree.heading("date", text="Date")
        self.tree.heading("heure", text="Heure")
        self.tree.heading("duree", text="Durée")
        self.tree.heading("statut", text="Statut")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("client", width=180)
        self.tree.column("activite", width=130)
        self.tree.column("date", width=110, anchor="center")
        self.tree.column("heure", width=80, anchor="center")
        self.tree.column("duree", width=80, anchor="center")
        self.tree.column("statut", width=110, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _init_db(self):
        self.conn = sqlite3.connect("database.db")
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS rendezvous (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        client TEXT NOT NULL, 
        activite TEXT NOT NULL, 
        date TEXT NOT NULL, 
        heure TEXT NOT NULL, 
        duree TEXT NOT NULL, 
        statut TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def _insert(self, client, activite, date, heure, duree, statut):
        self.conn.execute(
            """INSERT INTO rendezvous (client, activite, date, heure, duree, statut) VALUES (?, ?, ?, ?, ?, ?)""",
            (client, activite, date, heure, duree, statut)
        )
        self.conn.commit()

    def _update(self, row_id, client, activite, date, heure, duree, statut):
        self.conn.execute(
            "UPDATE rendezvous SET client=?, activite=?, date=?, heure=?, duree=?, statut=? WHERE id=?",
            (client, activite, date, heure, duree, statut, row_id)
        )
        self.conn.commit()

    def _delete(self, row_id):
        self.conn.execute(
            "DELETE FROM rendezvous WHERE id=?",
            (row_id,)
        )
        self.conn.commit()

    def _fetch_all(self):
        cursor = self.conn.execute(
            "SELECT * FROM rendezvous ORDER BY id"
        )
        return cursor.fetchall()

    def _load_rows(self):
        self.tree.delete(*self.tree.get_children())
        for row in self._fetch_all():
            self.tree.insert('', 'end', values=row)

    def _get_form_data(self):
        client = self.ent_client.get()
        activite = self.combo_activite.get()
        date = self.ent_date.get()
        heure = self.ent_heure.get()
        duree = self.ent_duree.get()
        statut = self.combo_statut.get()

        if not client or not activite or not date or not heure or not duree or not statut:
            messagebox.showwarning("Champs Obligatoires", "Merci de remplir tous les champs")
            return None
        if not duree.isdigit() or int(duree) <= 0:
            messagebox.showerror("Durée invalide", "Merci de mettre un entier positif")
            return None
        try:
            date_valide = datetime.strptime(date, "%Y-%m-%d")
            if date_valide.strftime("%Y-%m-%d") != date:
                raise ValueError("Date invalide")
        except ValueError:
            messagebox.showerror("Date invalide", "Merci de mettre une date valide")
            return None
        try:
            heure_valide = datetime.strptime(heure, "%H:%M")
            if heure_valide.strftime("%H:%M") != heure:
                raise ValueError("Heure invalide")
        except ValueError:
            messagebox.showerror("Heure invalide", "Merci de mettre une heure valide")
            return None

        return client, activite, date, heure, int(duree), statut


    def _on_add(self):
        data = self._get_form_data()
        if data is None:
            return

        try:
            self._insert(*data)
            self._load_rows()
            messagebox.showinfo("Ajout", "Rendez-vous ajouté avec succès")
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))

    def _on_delete(self):
        if self.selected_id is None:
            messagebox.showwarning("Selection Requise", "Veuillez sélectinner un RDV à modifier")
            return

        confirmation = messagebox.askyesno("supprimer", "supprimer un RDV")
        if not confirmation:
            return

        try:
            self._delete(self.selected_id)
            self._load_rows()
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))

    def _on_update(self):
        if self.selected_id is None:
            messagebox.showwarning("Selection Requise", "Veuillez sélectinner un RDV à modifier")
            return
        data = self._get_form_data()
        if data is None:
            return
        confirmation = messagebox.askyesno("Modification", "Modifier un RDV")
        if not confirmation:
            return

        try:
            self._update(self.selected_id, *data)
            self._load_rows()
            messagebox.showinfo("Modification", "RDV modifié avec succès")
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))

    def _on_select(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")

        self._empty_form()

        self.ent_client.insert(tk.END, values[1])
        self.combo_activite.set(values[2])
        self.ent_date.insert(tk.END, values[3])
        self.ent_heure.insert(tk.END, values[4])
        self.ent_duree.insert(tk.END, values[5])
        self.combo_statut.set(values[6])

        self.selected_id = values[0]

    def _on_new(self):
        self._empty_form()
        self.selected_id = None

    def _empty_form(self):
        self.ent_client.delete(0, tk.END)
        self.combo_activite.set('')
        self.ent_date.delete(0, tk.END)
        self.ent_heure.delete(0, tk.END)
        self.ent_duree.delete(0, tk.END)
        self.combo_statut.set('')













if __name__ == "__main__":
    App().mainloop()
