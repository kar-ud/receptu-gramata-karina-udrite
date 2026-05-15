import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

# Saglabā JSON failu tajā pašā mapē, kur atrodas programma
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "receptes.json")

def load_receptes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_receptes(receptes):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(receptes, f, ensure_ascii=False, indent=2)

KATEGORIJAS = ["Visi", "Zupas", "Salāti", "Deserti", "Galvenie ēdieni", "Uzkodas", "Cits"]

class ReceptuGramata:
    def __init__(self, root):
        self.root = root
        self.root.title("Receptu grāmata")
        self.root.geometry("900x600")
        self.root.configure(bg="#f5f0e8")
        self.receptes = load_receptes()
        self.build_ui()
        self.refresh_list()

    def build_ui(self):
        # Top bar
        top = tk.Frame(self.root, bg="#8b5e3c", pady=8)
        top.pack(fill=tk.X)
        tk.Label(top, text="🍽 Receptu grāmata", font=("Arial", 18, "bold"),
                 bg="#8b5e3c", fg="white").pack(side=tk.LEFT, padx=15)

        # Search + filter row
        mid = tk.Frame(self.root, bg="#f5f0e8", pady=6)
        mid.pack(fill=tk.X, padx=10)

        tk.Label(mid, text="Meklēt:", bg="#f5f0e8", font=("Arial", 11)).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh_list())
        tk.Entry(mid, textvariable=self.search_var, width=25, font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

        tk.Label(mid, text="Kategorija:", bg="#f5f0e8", font=("Arial", 11)).pack(side=tk.LEFT, padx=(15,0))
        self.kat_var = tk.StringVar(value="Visi")
        kat_menu = ttk.Combobox(mid, textvariable=self.kat_var, values=KATEGORIJAS,
                                 state="readonly", width=18, font=("Arial", 11))
        kat_menu.pack(side=tk.LEFT, padx=5)
        kat_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_list())

        # Main area
        main = tk.Frame(self.root, bg="#f5f0e8")
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # List frame
        list_frame = tk.Frame(main, bg="#f5f0e8")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(list_frame, font=("Arial", 12), selectbackground="#8b5e3c",
                                   selectforeground="white", activestyle="none",
                                   bd=0, highlightthickness=1, highlightcolor="#ccc")
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.configure(yscrollcommand=scrollbar.set)

        # Detail frame
        detail_frame = tk.Frame(main, bg="white", bd=1, relief=tk.GROOVE, width=380)
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10,0))
        detail_frame.pack_propagate(False)

        tk.Label(detail_frame, text="Receptes detaļas", font=("Arial", 13, "bold"),
                 bg="white", fg="#8b5e3c").pack(pady=(10,5))

        self.detail_name = tk.Label(detail_frame, text="", font=("Arial", 12, "bold"),
                                     bg="white", wraplength=340)
        self.detail_name.pack(padx=10)

        self.detail_kat = tk.Label(detail_frame, text="", font=("Arial", 10, "italic"),
                                    bg="white", fg="#888")
        self.detail_kat.pack(padx=10)

        ttk.Separator(detail_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)

        tk.Label(detail_frame, text="Ingredienti:", font=("Arial", 11, "bold"),
                 bg="white", anchor="w").pack(fill=tk.X, padx=10)
        self.detail_ing = tk.Text(detail_frame, font=("Arial", 10), height=6,
                                   state=tk.DISABLED, bd=0, bg="white", wrap=tk.WORD)
        self.detail_ing.pack(fill=tk.X, padx=10)

        tk.Label(detail_frame, text="Pagatavošana:", font=("Arial", 11, "bold"),
                 bg="white", anchor="w").pack(fill=tk.X, padx=10, pady=(5,0))
        self.detail_inst = tk.Text(detail_frame, font=("Arial", 10), height=10,
                                    state=tk.DISABLED, bd=0, bg="white", wrap=tk.WORD)
        self.detail_inst.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

        # Buttons
        btn_frame = tk.Frame(self.root, bg="#f5f0e8", pady=8)
        btn_frame.pack(fill=tk.X, padx=10)

        btn_style = {"font": ("Arial", 11), "bd": 0, "cursor": "hand2",
                     "padx": 16, "pady": 6, "relief": tk.FLAT}

        tk.Button(btn_frame, text="➕ Pievienot", bg="#4CAF50", fg="white",
                  command=self.pievienot, **btn_style).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="✏️ Rediģēt", bg="#2196F3", fg="white",
                  command=self.redighet, **btn_style).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="🗑 Dzēst", bg="#f44336", fg="white",
                  command=self.dzest, **btn_style).pack(side=tk.LEFT, padx=4)

        self.status = tk.Label(self.root, text="", bg="#f5f0e8", fg="#666", font=("Arial", 9))
        self.status.pack(pady=2)

    def refresh_list(self):
        search = self.search_var.get().lower()
        kat = self.kat_var.get()
        self.listbox.delete(0, tk.END)
        self.filtered = []
        for r in self.receptes:
            if search and search not in r["nosaukums"].lower():
                continue
            if kat != "Visi" and r.get("kategorija") != kat:
                continue
            self.filtered.append(r)
            self.listbox.insert(tk.END, f"  {r['nosaukums']}  [{r.get('kategorija','—')}]")
        if not self.filtered:
            self.listbox.insert(tk.END, "  Nav atrasts")
        self.status.config(text=f"Kopā receptes: {len(self.receptes)} | Rāda: {len(self.filtered)}")

    def on_select(self, event):
        sel = self.listbox.curselection()
        if not sel or not self.filtered:
            return
        idx = sel[0]
        if idx >= len(self.filtered):
            return
        r = self.filtered[idx]
        self.detail_name.config(text=r["nosaukums"])
        self.detail_kat.config(text=r.get("kategorija", "—"))

        def set_text(widget, txt):
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.insert(tk.END, txt)
            widget.config(state=tk.DISABLED)

        set_text(self.detail_ing, r.get("ingredienti", ""))
        set_text(self.detail_inst, r.get("instrukcijas", ""))

    def open_form(self, title, recepte=None):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("520x520")
        win.configure(bg="white")
        win.grab_set()

        def lbl(txt): return tk.Label(win, text=txt, bg="white", font=("Arial", 11, "bold"), anchor="w")
        def entry(): return tk.Entry(win, font=("Arial", 11), bd=1, relief=tk.SOLID)
        def text(h): return tk.Text(win, font=("Arial", 10), height=h, bd=1, relief=tk.SOLID, wrap=tk.WORD)

        lbl("Nosaukums:*").pack(fill=tk.X, padx=15, pady=(15,0))
        e_name = entry(); e_name.pack(fill=tk.X, padx=15)

        lbl("Kategorija:").pack(fill=tk.X, padx=15, pady=(10,0))
        kat_var = tk.StringVar(value=recepte.get("kategorija","Galvenie ēdieni") if recepte else "Galvenie ēdieni")
        kat_box = ttk.Combobox(win, textvariable=kat_var,
                                values=[k for k in KATEGORIJAS if k != "Visi"],
                                state="readonly", font=("Arial", 11))
        kat_box.pack(fill=tk.X, padx=15)

        lbl("Ingredienti:*").pack(fill=tk.X, padx=15, pady=(10,0))
        t_ing = text(5); t_ing.pack(fill=tk.X, padx=15)

        lbl("Pagatavošanas instrukcijas:").pack(fill=tk.X, padx=15, pady=(10,0))
        t_inst = text(6); t_inst.pack(fill=tk.X, padx=15)

        if recepte:
            e_name.insert(0, recepte.get("nosaukums",""))
            t_ing.insert("1.0", recepte.get("ingredienti",""))
            t_inst.insert("1.0", recepte.get("instrukcijas",""))

        result = {}

        def saglabat():
            name = e_name.get().strip()
            ing = t_ing.get("1.0", tk.END).strip()
            if not name or not ing:
                messagebox.showerror("Kļūda", "Lūdzu aizpildiet nosaukumu un ingredientus!", parent=win)
                return
            result["nosaukums"] = name
            result["kategorija"] = kat_var.get()
            result["ingredienti"] = ing
            result["instrukcijas"] = t_inst.get("1.0", tk.END).strip()
            win.destroy()

        btn_f = tk.Frame(win, bg="white")
        btn_f.pack(pady=10)
        tk.Button(btn_f, text="💾 Saglabāt", bg="#4CAF50", fg="white",
                  font=("Arial", 11), padx=12, pady=5, bd=0, command=saglabat).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_f, text="Atcelt", bg="#aaa", fg="white",
                  font=("Arial", 11), padx=12, pady=5, bd=0, command=win.destroy).pack(side=tk.LEFT)

        self.root.wait_window(win)
        return result if result else None

    def pievienot(self):
        r = self.open_form("Pievienot recepti")
        if r:
            self.receptes.append(r)
            save_receptes(self.receptes)
            self.refresh_list()

    def redighet(self):
        sel = self.listbox.curselection()
        if not sel or not self.filtered or sel[0] >= len(self.filtered):
            messagebox.showinfo("Info", "Lūdzu izvēlieties recepti!")
            return
        old = self.filtered[sel[0]]
        r = self.open_form("Rediģēt recepti", old)
        if r:
            idx = self.receptes.index(old)
            self.receptes[idx] = r
            save_receptes(self.receptes)
            self.refresh_list()

    def dzest(self):
        sel = self.listbox.curselection()
        if not sel or not self.filtered or sel[0] >= len(self.filtered):
            messagebox.showinfo("Info", "Lūdzu izvēlieties recepti!")
            return
        r = self.filtered[sel[0]]
        if messagebox.askyesno("Dzēst", f"Vai tiešām vēlaties dzēst šo recepti?\n\n'{r['nosaukums']}'"):
            self.receptes.remove(r)
            save_receptes(self.receptes)
            self.detail_name.config(text="")
            self.detail_kat.config(text="")
            for w in [self.detail_ing, self.detail_inst]:
                w.config(state=tk.NORMAL)
                w.delete("1.0", tk.END)
                w.config(state=tk.DISABLED)
            self.refresh_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReceptuGramata(root)
    root.mainloop()
