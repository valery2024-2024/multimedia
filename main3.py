import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

root = tk.Tk()
root.title("Практична №3 — SpriteSheet Cutter (Tkinter + Pillow)")
root.geometry("480x480")
root.resizable(False, False)

# --- глобальні змінні ---
mode = tk.StringVar(value="count")
filename = None
img_info_var = tk.StringVar(value="(файл не обрано)")
status_var = tk.StringVar(value="Готово")
divisors_var = tk.StringVar(value="")  # тут будемо показувати дільники

# --- функція пошуку дільників ---
def get_divisors(n: int):
    divs = []
    for i in range(1, n + 1):
        if n % i == 0:
            divs.append(i)
    return divs

# --- вибір зображення ---
def open_file():
    global filename
    path = filedialog.askopenfilename(
        title="Обрати зображення",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
    )
    if not path:
        return
    try:
        with Image.open(path) as im:
            w, h = im.size
        filename = path
        img_info_var.set(f"Файл: {os.path.basename(path)}  |  {w}×{h}px")

        # знайдемо дільники для ширини та висоти
        div_w = get_divisors(w)
        div_h = get_divisors(h)
        divisors_var.set(
            f"Дільники ширини {w}: {div_w}\n"
            f"Дільники висоти {h}: {div_h}\n\n"
            "👉 Обери одну ширину та висоту з цього списку\n"
            "в режимі 'за розміром'."
        )

        status_var.set("Файл завантажено")
    except Exception as ex:
        messagebox.showerror("Помилка", f"Не вдалося відкрити файл:\n{ex}")
        filename = None
        img_info_var.set("(файл не обрано)")
        status_var.set("Помилка відкриття")

# --- перемикач режимів ---
def update_fields():
    if mode.get() == "count":
        frame_count.pack(fill="x", padx=10, pady=(0, 10))
        frame_size.forget()
    else:
        frame_size.pack(fill="x", padx=10, pady=(0, 10))
        frame_count.forget()

# --- допоміжні функції ---
def parse_positive_int(entry: tk.Entry, field_name: str) -> int:
    try:
        val = int(entry.get())
        if val <= 0:
            raise ValueError
        return val
    except ValueError:
        messagebox.showwarning("Помилка", f"{field_name} має бути цілим > 0")
        raise

def ensure_image_loaded() -> Image.Image:
    if not filename:
        messagebox.showinfo("Немає файлу", "Спочатку обери зображення")
        raise RuntimeError
    return Image.open(filename)

def choose_save_dir() -> str:
    save_path = filedialog.askdirectory(title="Оберіть папку для збереження")
    if not save_path:
        raise RuntimeError
    return save_path

# --- основна функція нарізання ---
def save_sprites():
    try:
        img = ensure_image_loaded()
        save_dir = choose_save_dir()
    except RuntimeError:
        return

    try:
        if mode.get() == "count":
            rows = parse_positive_int(rows_entry, "Рядки")
            cols = parse_positive_int(cols_entry, "Стовпці")
            if img.width % cols != 0 or img.height % rows != 0:
                messagebox.showerror("Неподільні розміри",
                    f"{img.width}×{img.height} не ділиться на {rows}×{cols}")
                return
            cell_w = img.width // cols
            cell_h = img.height // rows
        else:
            cell_w = parse_positive_int(cell_w_entry, "Ширина спрайта")
            cell_h = parse_positive_int(cell_h_entry, "Висота спрайта")
            if img.width % cell_w != 0 or img.height % cell_h != 0:
                messagebox.showerror("Неподільні розміри",
                    f"{img.width}×{img.height} не ділиться на {cell_w}×{cell_h}")
                return
            cols = img.width // cell_w
            rows = img.height // cell_h

    except ValueError:
        return

    os.makedirs(save_dir, exist_ok=True)
    index = 0
    for r in range(rows):
        for c in range(cols):
            x1, y1 = c * cell_w, r * cell_h
            x2, y2 = x1 + cell_w, y1 + cell_h
            sprite = img.crop((x1, y1, x2, y2))
            sprite.save(os.path.join(save_dir, f"sprite_{index}.png"))
            index += 1

    messagebox.showinfo("Готово", f"Збережено {index} файлів у {save_dir}")
    status_var.set(f"Збережено {index} спрайтів")

# --- UI ---
file_frame = tk.Frame(root, padx=10, pady=10)
file_frame.pack(fill="x")
tk.Button(file_frame, text="Обрати зображення", command=open_file).pack(side="left")
tk.Label(file_frame, textvariable=img_info_var, wraplength=280, justify="left").pack(side="left", padx=10)

mode_frame = tk.Frame(root, padx=10)
mode_frame.pack(fill="x")
tk.Radiobutton(mode_frame, text="Нарізати за кількістю", variable=mode, value="count", command=update_fields).pack(anchor="w")
tk.Radiobutton(mode_frame, text="Нарізати за розміром", variable=mode, value="size", command=update_fields).pack(anchor="w")

frame_count = tk.Frame(root, padx=10)
tk.Label(frame_count, text="Рядки:").pack(anchor="w")
rows_entry = tk.Entry(frame_count); rows_entry.insert(0, "4"); rows_entry.pack(fill="x")
tk.Label(frame_count, text="Стовпці:").pack(anchor="w")
cols_entry = tk.Entry(frame_count); cols_entry.insert(0, "4"); cols_entry.pack(fill="x")
frame_count.pack(fill="x", padx=10, pady=(0, 10))

frame_size = tk.Frame(root, padx=10)
tk.Label(frame_size, text="Ширина спрайта:").pack(anchor="w")
cell_w_entry = tk.Entry(frame_size); cell_w_entry.insert(0, "64"); cell_w_entry.pack(fill="x")
tk.Label(frame_size, text="Висота спрайта:").pack(anchor="w")
cell_h_entry = tk.Entry(frame_size); cell_h_entry.insert(0, "64"); cell_h_entry.pack(fill="x")

btns = tk.Frame(root, padx=10, pady=5); btns.pack(fill="x")
tk.Button(btns, text="Нарізати та зберегти", command=save_sprites).pack(fill="x")

# поле з підказкою для дільників
hint_frame = tk.Frame(root, padx=10, pady=5); hint_frame.pack(fill="x")
tk.Label(hint_frame, textvariable=divisors_var, justify="left", fg="blue", wraplength=460).pack()

status_bar = tk.Label(root, textvariable=status_var, anchor="w", bd=1, relief="sunken")
status_bar.pack(side="bottom", fill="x")

root.mainloop()
