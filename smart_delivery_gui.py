import random
import time
import tkinter as tk
from tkinter import ttk, messagebox

from route_algorithms import nearest_neighbour, brute_force, dynamic_programming

ALGOS = [("Nearest Neighbour", nearest_neighbour, "#178a8a"),
         ("Brute Force", brute_force, "#e8912d"),
         ("Dynamic Programming", dynamic_programming, "#6f5cc7")]


def timed(func, dist):
    start = time.perf_counter()
    route, d = func(dist)
    return route, d, (time.perf_counter() - start) * 1000  # ms


class App:
    def __init__(self, root):
        root.title("Smart Delivery Route Planner")
        root.geometry("900x620")
        self.names, self.entries = [], {}

        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True)
        self.nb = nb
        self.t1, self.t2, self.t3 = ttk.Frame(nb), ttk.Frame(nb), ttk.Frame(nb)
        nb.add(self.t1, text="1. Locations & Distances")
        nb.add(self.t2, text="2. Route Comparison")
        nb.add(self.t3, text="3. Performance Graph")
        self.build_tab1()
        self.build_tab2()
        self.build_tab3()

    # ---------- Tab 1: input ----------
    def build_tab1(self):
        ttk.Label(self.t1, text="Delivery locations", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        top = ttk.Frame(self.t1)
        top.pack(fill="x", padx=10)
        ttk.Label(top, text="Location names (comma separated, first = warehouse):").pack(side="left")
        self.name_var = tk.StringVar(value="Warehouse, College, Hospital, Market, Station")
        ttk.Entry(top, textvariable=self.name_var, width=45).pack(side="left", padx=5)
        ttk.Button(top, text="Create distance table", command=self.create_table).pack(side="left")

        ttk.Label(self.t1, text="Enter distances in the upper triangle only; reverse distances fill automatically.").pack(anchor="w", padx=10, pady=5)
        self.grid_frame = ttk.Frame(self.t1)
        self.grid_frame.pack(padx=10, pady=5, anchor="w")

        bottom = ttk.Frame(self.t1)
        bottom.pack(side="bottom", fill="x", padx=10, pady=10)
        ttk.Button(bottom, text="Load example", command=self.load_example).pack(side="left")
        ttk.Button(bottom, text="Calculate & compare routes", command=self.calculate).pack(side="right")

    def create_table(self):
        names = [x.strip() for x in self.name_var.get().split(",") if x.strip()]
        if not 2 <= len(names) <= 10 or len(set(names)) != len(names):
            messagebox.showerror("Error", "Enter 2 to 10 different location names.")
            return False
        self.names = names
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.entries = {}
        n = len(names)
        ttk.Label(self.grid_frame, text="From / To").grid(row=0, column=0, padx=3, pady=3)
        for i, nm in enumerate(names):
            ttk.Label(self.grid_frame, text=nm, font=("Arial", 9, "bold")).grid(row=0, column=i + 1, padx=3)
            ttk.Label(self.grid_frame, text=nm, font=("Arial", 9, "bold")).grid(row=i + 1, column=0, padx=3)
        for i in range(n):
            for j in range(n):
                if i == j:
                    ttk.Label(self.grid_frame, text="0").grid(row=i + 1, column=j + 1)
                elif j > i:
                    e = ttk.Entry(self.grid_frame, width=8, justify="center")
                    e.grid(row=i + 1, column=j + 1, padx=2, pady=2)
                    self.entries[(i, j)] = e
                else:
                    ttk.Label(self.grid_frame, text="Auto-filled", foreground="gray").grid(row=i + 1, column=j + 1)
        return True

    def load_example(self):
        self.name_var.set("Warehouse, College, Hospital, Market, Station")
        self.create_table()
        data = {(0, 1): 10, (0, 2): 15, (0, 3): 20, (0, 4): 13,
                (1, 2): 20, (1, 3): 25, (1, 4): 17,
                (2, 3): 30, (2, 4): 14, (3, 4): 18}
        for key, val in data.items():
            self.entries[key].insert(0, str(val))

    def get_matrix(self):
        n = len(self.names)
        if n == 0:
            raise ValueError("Create the distance table first.")
        m = [[0] * n for _ in range(n)]
        for (i, j), e in self.entries.items():
            try:
                v = float(e.get())
            except ValueError:
                raise ValueError(f"Invalid distance for {self.names[i]} - {self.names[j]}.")
            if v < 0:
                raise ValueError("Distances must be non-negative.")
            m[i][j] = m[j][i] = v  # symmetric mirror
        return m

    def calculate(self):
        try:
            dist = self.get_matrix()
        except ValueError as err:
            messagebox.showerror("Input error", str(err))
            return
        self.tree.delete(*self.tree.get_children())
        for name, func, _ in ALGOS:
            route, d, t = timed(func, dist)
            path = " -> ".join(self.names[i] for i in route + [0])
            self.tree.insert("", "end", values=(name, path, f"{d:g}", f"{t:.4f}"))
        self.nb.select(self.t2)

    # ---------- Tab 2: results ----------
    def build_tab2(self):
        ttk.Label(self.t2, text="Route comparison", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        cols = ("Algorithm", "Route", "Total distance", "Time (ms)")
        self.tree = ttk.Treeview(self.t2, columns=cols, show="headings", height=6)
        for c, w in zip(cols, (150, 450, 100, 100)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(fill="x", padx=10)
        ttk.Label(self.t2, wraplength=800, text=(
            "Nearest Neighbour is fast but may miss the optimum. Brute Force checks every route. "
            "Dynamic Programming reuses subproblems and also finds the optimal route, "
            "usually faster than Brute Force for larger inputs.")).pack(anchor="w", padx=10, pady=10)

    # ---------- Tab 3: benchmark ----------
    def build_tab3(self):
        ttk.Label(self.t3, text="Algorithm performance", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        top = ttk.Frame(self.t3)
        top.pack(fill="x", padx=10)
        ttk.Label(top, text="Maximum locations (4-10):").pack(side="left")
        self.max_n = ttk.Combobox(top, values=list(range(4, 11)), width=4, state="readonly")
        self.max_n.set(9)
        self.max_n.pack(side="left", padx=5)
        ttk.Button(top, text="Run performance test", command=self.benchmark).pack(side="left")
        self.canvas = tk.Canvas(self.t3, width=800, height=330, bg="white")
        self.canvas.pack(padx=10, pady=10)
        self.table_lbl = ttk.Label(self.t3, justify="left", font=("Courier", 9))
        self.table_lbl.pack(anchor="w", padx=10)

    def benchmark(self):
        top_n = int(self.max_n.get())
        sizes = list(range(4, top_n + 1))
        results = {name: [] for name, _, _ in ALGOS}
        for n in sizes:
            for name, func, _ in ALGOS:
                total = 0
                for _ in range(3):  # average of 3 runs
                    random.seed(n)
                    m = [[0] * n for _ in range(n)]
                    for i in range(n):
                        for j in range(i + 1, n):
                            m[i][j] = m[j][i] = random.randint(5, 50)
                    total += timed(func, m)[2]
                results[name].append(total / 3)
            self.t3.update()
        self.draw_graph(sizes, results)
        lines = ["Avg time over 3 runs (ms):", "n | NN | BF | DP"]
        for k, n in enumerate(sizes):
            lines.append(f"{n} | " + " | ".join(f"{results[a[0]][k]:.4f}" for a in ALGOS))
        self.table_lbl.config(text="\n".join(lines))

    def draw_graph(self, sizes, results):
        c = self.canvas
        c.delete("all")
        L, R, T, B = 70, 780, 30, 290
        ymax = max(max(v) for v in results.values()) or 1
        c.create_line(L, T, L, B)
        c.create_line(L, B, R, B)
        c.create_text(20, (T + B) // 2, text="Time (ms)", angle=90)
        c.create_text((L + R) // 2, 320, text="Number of locations")
        for k in range(5):
            y = B - (B - T) * k / 4
            c.create_line(L, y, R, y, fill="#e5e5e5")
            c.create_text(L - 5, y, text=f"{ymax * k / 4:.2f}", anchor="e")
        step = (R - L) / (len(sizes) - 1)
        for k, n in enumerate(sizes):
            c.create_text(L + k * step, B + 12, text=str(n))
        for lx, (name, _, colour) in zip((200, 360, 520), ALGOS):
            c.create_line(lx, 12, lx + 25, 12, fill=colour, width=3)
            c.create_text(lx + 30, 12, text=name, anchor="w")
            pts = [(L + k * step, B - (B - T) * v / ymax) for k, v in enumerate(results[name])]
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                c.create_line(x1, y1, x2, y2, fill=colour, width=2)
            for x, y in pts:
                c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=colour, outline=colour)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()