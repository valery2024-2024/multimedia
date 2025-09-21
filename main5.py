import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

root = tk.Tk()
root.title("Практична №3 — SpriteSheet Cutter (як у викладача)")

# Змінні стану

mode = tk.StringVar(value="count")   # "count" або "size"
filename = None
trim_var = tk.BooleanVar(value=True)  # обрізати краї, якщо не ділиться 

# Блок вибору режиму

def update_fields():
    if mode.get() == "count":
        frame_count.pack()
        frame_size.forget()
    else:
        frame_size.pack()
        frame_count.forget()

tk.Radiobutton(root, text="Нарізати за кількістю (рядки × стовпці)",
               variable=mode, value="count", command=update_fields).pack(anchor="w", padx=8, pady=(8, 0))
tk.Radiobutton(root, text="Нарізати за розміром (ширина × висота)",
               variable=mode, value="size", command=update_fields).pack(anchor="w", padx=8)

# Чекбокс — обрізати краї, якщо не ділиться
tk.Checkbutton(
    root,
    text="Обрізати краї, якщо не ділиться (поведінка як у викладача)",
    variable=trim_var
).pack(anchor="w", padx=8, pady=(0, 8))

# Поля для варіанта "за кількістю"

frame_count = tk.Frame(root, padx=8, pady=4, borderwidth=0)
tk.Label(frame_count, text="Рядки (rows):").pack(anchor="w")
rows_entry = tk.Entry(frame_count)
rows_entry.insert(0, "10")
rows_entry.pack(fill="x")

tk.Label(frame_count, text="Стовпці (columns):").pack(anchor="w", pady=(6, 0))
cols_entry = tk.Entry(frame_count)
cols_entry.insert(0, "10")
cols_entry.pack(fill="x")

frame_count.pack(fill="x")

# Поля для варіанта "за розміром"

frame_size = tk.Frame(root, padx=8, pady=4, borderwidth=0)
tk.Label(frame_size, text="Ширина спрайта (px):").pack(anchor="w")
cell_w_entry = tk.Entry(frame_size)
cell_w_entry.insert(0, "64")
cell_w_entry.pack(fill="x")

tk.Label(frame_size, text="Висота спрайта (px):").pack(anchor="w", pady=(6, 0))
cell_h_entry = tk.Entry(frame_size)
cell_h_entry.insert(0, "64")
cell_h_entry.pack(fill="x")

# Вибір зображення

def open_file():
    global filename
    filename = filedialog.askopenfilename(
        title="Обрати зображення",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
    )
    if filename:
        try:
            with Image.open(filename) as im:
                w, h = im.size
            messagebox.showinfo("Файл обрано", f"Файл: {filename}\nРозмір: {w}×{h}px")
        except Exception as ex:
            messagebox.showerror("Помилка", f"Не вдалося відкрити зображення:\n{ex}")
            filename = None

# Допоміжне: читання додатних цілих

def parse_int(entry: tk.Entry, name: str) -> int:
    try:
        v = int(entry.get())
        if v <= 0:
            raise ValueError
        return v
    except ValueError:
        messagebox.showwarning("Некоректне значення", f"{name} має бути додатним цілим.")
        raise

# Збереження нарізаних спрайтів

def save_sprites():
    if not filename:
        messagebox.showwarning("Немає файлу", "Спочатку оберіть зображення.")
        return

    save_dir = filedialog.askdirectory(title="Куди зберегти спрайти?")
    if not save_dir:
        return

    try:
        img = Image.open(filename)
    except Exception as ex:
        messagebox.showerror("Помилка", f"Не вдалося відкрити зображення:\n{ex}")
        return

    W, H = img.width, img.height
    trim = trim_var.get()

    # Обчислення параметрів під обраний режим
    try:
        if mode.get() == "count":
            rows = parse_int(rows_entry, "Рядки")
            cols = parse_int(cols_entry, "Стовпці")

            # Базові розміри клітинок через цілочисельне ділення
            cell_w = W // cols
            cell_h = H // rows

            # Якщо не ділиться і trim=False — показуємо помилку, інакше просто ігноруємо «хвіст»
            if (W % cols != 0 or H % rows != 0) and not trim:
                messagebox.showerror(
                    "Неподільні розміри",
                    f"Зображення {W}×{H}px не ділиться на {rows}×{cols} без остачі.\n"
                    f"Увімкніть опцію «Обрізати краї…» або змініть параметри."
                )
                return

        else:  # mode == "size"
            cell_w = parse_int(cell_w_entry, "Ширина спрайта")
            cell_h = parse_int(cell_h_entry, "Висота спрайта")

            # Кількість цілих тайлів, що вмістяться
            cols = W // cell_w
            rows = H // cell_h

            if (W % cell_w != 0 or H % cell_h != 0):
                if not trim:
                    messagebox.showerror(
                        "Неподільні розміри",
                        f"{cell_w}×{cell_h}px не ділить {W}×{H}px без остачі.\n"
                        f"Увімкніть опцію «Обрізати краї…» або змініть параметри."
                    )
                    return
                # Якщо дозволено обрізання, але нічого не влазить — також зупиняємось
                if cols == 0 or rows == 0:
                    messagebox.showerror(
                        "Занадто великі тайли",
                        f"За розміру {cell_w}×{cell_h}px у {W}×{H}px не поміщається жодного цілого спрайта."
                    )
                    return

        # Нарізання (ігноруємо правий/нижній «хвіст», якщо такий є)
        index = 0
        for r in range(rows):
            for c in range(cols):
                x1 = c * cell_w
                y1 = r * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h
                sprite = img.crop((x1, y1, x2, y2))
                sprite.save(f"{save_dir}/sprite_{index}.png", format="PNG")
                index += 1

        # Якщо був «хвіст» і ми його обрізали — підкажемо користувачу
        tail_w = W - cols * cell_w
        tail_h = H - rows * cell_h
        note = ""
        if trim and (tail_w or tail_h):
            note = f"\n(Обрізано краї: праворуч {tail_w}px, знизу {tail_h}px)"

        messagebox.showinfo("Готово", f"Збережено {index} спрайтів у:\n{save_dir}{note}")

    except Exception as ex:
        messagebox.showerror("Помилка", f"Сталася помилка:\n{ex}")

# Кнопки керування

tk.Button(root, text="Обрати зображення", command=open_file).pack(fill="x", padx=8, pady=(6, 3))
tk.Button(root, text="Нарізати та зберегти", command=save_sprites).pack(fill="x", padx=8, pady=(0, 10))

root.mainloop()
