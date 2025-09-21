import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

root = tk.Tk()
root.title("Практична №3 — SpriteSheet Cutter")

# -------------------------------
# Змінна режиму
# -------------------------------
mode = tk.StringVar(value="count")
filename = None

# -------------------------------
# Поля для варіанта "за кількістю"
# -------------------------------
frame_count = tk.Frame(root)

tk.Label(frame_count, text="Рядки (rows):").pack()
rows_entry = tk.Entry(frame_count)
rows_entry.pack()

tk.Label(frame_count, text="Стовпці (columns):").pack()
cols_entry = tk.Entry(frame_count)
cols_entry.pack()

# -------------------------------
# Поля для варіанта "за розміром"
# -------------------------------
frame_size = tk.Frame(root)

tk.Label(frame_size, text="Ширина спрайта (px):").pack()
cell_w_entry = tk.Entry(frame_size)
cell_w_entry.pack()

tk.Label(frame_size, text="Висота спрайта (px):").pack()
cell_h_entry = tk.Entry(frame_size)
cell_h_entry.pack()

# -------------------------------
# Функція перемикання режимів
# -------------------------------
def update_fields():
    if mode.get() == "count":
        frame_count.pack()
        frame_size.forget()
    else:
        frame_size.pack()
        frame_count.forget()

# -------------------------------
# Радіокнопки для вибору режиму
# -------------------------------
tk.Radiobutton(root, text="Нарізати за кількістю", 
               variable=mode, value="count", command=update_fields).pack()
tk.Radiobutton(root, text="Нарізати за розміром", 
               variable=mode, value="size", command=update_fields).pack()

frame_count.pack()  # стартовий варіант

# -------------------------------
# Вибір зображення
# -------------------------------
def open_file():
    global filename
    filename = filedialog.askopenfilename(
        title="Обрати зображення",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
    )
    if filename:
        messagebox.showinfo("Файл обрано", f"Ви вибрали файл:\n{filename}")

# -------------------------------
# Збереження нарізаних спрайтів
# -------------------------------
def save_sprites():
    if not filename:
        messagebox.showwarning("Помилка", "Спочатку оберіть зображення!")
        return

    save_path = filedialog.askdirectory(title="Куди зберегти спрайти?")
    if not save_path:
        return

    img = Image.open(filename)

    if mode.get() == "count":
        rows = int(rows_entry.get())
        cols = int(cols_entry.get())
        if img.width % cols != 0 or img.height % rows != 0:
            messagebox.showerror("Помилка",
                                 f"Зображення {img.width}×{img.height}px "
                                 f"не ділиться на {rows}×{cols} без остачі.")
            return
        cell_w = img.width // cols
        cell_h = img.height // rows
    else:
        cell_w = int(cell_w_entry.get())
        cell_h = int(cell_h_entry.get())
        if img.width % cell_w != 0 or img.height % cell_h != 0:
            messagebox.showerror("Помилка",
                                 f"Ширина/висота {cell_w}×{cell_h}px "
                                 f"не ділить зображення {img.width}×{img.height}px без остачі.")
            return
        cols = img.width // cell_w
        rows = img.height // cell_h

    index = 0
    for r in range(rows):
        for c in range(cols):
            x1 = c * cell_w
            y1 = r * cell_h
            x2 = x1 + cell_w
            y2 = y1 + cell_h
            sprite = img.crop((x1, y1, x2, y2))
            sprite.save(f"{save_path}/sprite_{index}.png")
            index += 1

    messagebox.showinfo("Готово", f"Збережено {index} спрайтів у {save_path}")

# -------------------------------
# Кнопки дії
# -------------------------------
tk.Button(root, text="Вибрати зображення", command=open_file).pack(pady=5)
tk.Button(root, text="Нарізати та зберегти", command=save_sprites).pack(pady=5)

root.mainloop()
