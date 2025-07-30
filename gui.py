import tkinter as tk
from tkinter import messagebox
import requests

# API Endpoint
API_URL = "http://localhost:8000/ads/"

# --- Functions ---
def get_ad_details():
    ad_id = id_entry.get().strip()
    if not ad_id:
        messagebox.showwarning("ورودی نامعتبر", "لطفاً شناسه آگهی را وارد کنید.")
        return

    try:
        ad_id = int(ad_id)
    except ValueError:
        messagebox.showerror("ورودی نامعتبر", "شناسه آگهی باید عددی باشد.")
        return

    try:
        response = requests.get(f"{API_URL}{ad_id}")
        response.raise_for_status()
        ad_data = response.json()

        # Clear previous details
        for widget in details_frame.winfo_children():
            widget.destroy()

        # Show Ad Info
        title_lbl = tk.Label(details_frame, text=f"عنوان: {ad_data.get('title', 'نامشخص')}", font=("B Nazanin", 14, "bold"), fg="#2E4053")
        title_lbl.pack(pady=6)

        link_lbl = tk.Label(details_frame, text=f"لینک: {ad_data.get('link', 'نامشخص')}", font=("Arial", 10), fg="#2874A6", cursor="hand2")
        link_lbl.pack(pady=2)

        for field, label in [
            ("price", "قیمت"),
            ("area", "منطقه"),
            ("publish_date", "تاریخ انتشار"),
            ("meterage", "متراژ"),
            ("num_rooms", "تعداد اتاق"),
            ("year_built", "سال ساخت")
        ]:
            value = ad_data.get(field, 'نامشخص')
            tk.Label(details_frame, text=f"{label}: {value}", font=("B Nazanin", 12)).pack(pady=2)

        desc_box = tk.Text(details_frame, height=8, width=70, wrap="word", font=("B Nazanin", 11))
        desc_box.insert(tk.END, f"توضیحات: {ad_data.get('description', 'نامشخص')}")
        desc_box.config(state="disabled", bg="#f7f9f9")
        desc_box.pack(pady=8)

    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            messagebox.showerror("خطا", "آگهی یافت نشد.")
        else:
            messagebox.showerror("خطای HTTP", f"{err}")
    except requests.exceptions.ConnectionError:
        messagebox.showerror("خطا", "ارتباط با سرور برقرار نشد. مطمئن شوید FastAPI اجرا شده است.")
    except Exception as e:
        messagebox.showerror("خطای ناشناخته", f"{e}")


# --- GUI Setup ---
root = tk.Tk()
root.title("جستجوگر آگهی دیوار")
root.geometry("750x750")
root.configure(bg="#EBF5FB")

# --- Input Section ---
input_frame = tk.Frame(root, bg="#EBF5FB")
input_frame.pack(pady=20)

tk.Label(input_frame, text="شناسه آگهی:", font=("B Nazanin", 13), bg="#EBF5FB").pack(side=tk.LEFT, padx=6)
id_entry = tk.Entry(input_frame, font=("Arial", 13), width=30)
id_entry.pack(side=tk.LEFT, padx=5)

search_button = tk.Button(input_frame, text="جستجو", command=get_ad_details,
                          font=("B Nazanin", 12, "bold"), bg="#3498DB", fg="white", padx=10, pady=2)
search_button.pack(side=tk.LEFT, padx=10)

# --- Results Section ---
details_frame = tk.LabelFrame(root, text="جزئیات آگهی", font=("B Nazanin", 14, "bold"),
                              padx=20, pady=20, bg="white", fg="#1F618D", bd=2, relief="groove")
details_frame.pack(padx=20, pady=10, fill="both", expand=True)

root.mainloop()
