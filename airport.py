import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="airport_db",
    charset='utf8',
    port=3306
)
cursor = conn.cursor()

# Main Application
root = tk.Tk()
root.title("Airport Management System")
root.geometry("1000x800")

style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=10)
style.configure("TLabel", font=("Arial", 12))
style.configure("TEntry", font=("Arial", 12))


# ========== Admin Login ==========
def admin_login():
    login_window = tk.Toplevel(root)
    login_window.title("Admin Login")
    login_window.geometry("500x500")

    def verify_login():
        username = entry_username.get()
        password = entry_password.get()
        if username == "admin" and password == "admin123":
            login_window.destroy()
            open_admin_panel()
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    ttk.Label(login_window, text="Username:").pack()
    entry_username = ttk.Entry(login_window)
    entry_username.pack()

    ttk.Label(login_window, text="Password:").pack()
    entry_password = ttk.Entry(login_window, show="*")
    entry_password.pack()

    ttk.Button(login_window, text="Login", command=verify_login).pack()


# ========== Admin Panel ==========
def open_admin_panel():
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Page")
    admin_window.geometry("500x400")

    def add_flight():
        airline = entry_airline.get()
        source = entry_source.get()
        destination = entry_destination.get()
        departure = entry_departure.get()
        total_seats = entry_seats.get()

        if not airline or not source or not destination or not departure or not total_seats:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            cursor.execute("INSERT INTO flights (airline, source, destination, departure_time, total_seats, available_seats) VALUES (%s, %s, %s, %s, %s, %s)", 
                           (airline, source, destination, departure, total_seats, total_seats))
            conn.commit()
            messagebox.showinfo("Success", "Flight Added!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Label(admin_window, text="Airline:").pack()
    entry_airline = ttk.Entry(admin_window)
    entry_airline.pack()

    ttk.Label(admin_window, text="Source:").pack()
    entry_source = ttk.Entry(admin_window)
    entry_source.pack()

    ttk.Label(admin_window, text="Destination:").pack()
    entry_destination = ttk.Entry(admin_window)
    entry_destination.pack()

    ttk.Label(admin_window, text="Departure Time:").pack()
    entry_departure = ttk.Entry(admin_window)
    entry_departure.pack()

    ttk.Label(admin_window, text="Total Seats:").pack()
    entry_seats = ttk.Entry(admin_window)
    entry_seats.pack()

    ttk.Button(admin_window, text="Add Flight", command=add_flight).pack()


# ========== Passenger Panel ==========
def open_passenger_panel():
    passenger_window = tk.Toplevel(root)
    passenger_window.title("Passenger Page")
    passenger_window.geometry("500x400")

    def show_available_seats():
        flight_id = entry_flight.get()
        cursor.execute("SELECT seat_number FROM seats WHERE flight_id = %s AND status = 'Available'", (flight_id,))
        available_seats = cursor.fetchall()

        seat_list.delete(0, tk.END)
        for seat in available_seats:
            seat_list.insert(tk.END, seat[0])

    def book_seat():
        passenger_name = entry_name.get()
        flight_id = entry_flight.get()
        selected_seat = seat_list.get(tk.ACTIVE)

        if not passenger_name or not flight_id or not selected_seat:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            cursor.execute("INSERT INTO passengers (name, age, gender, contact) VALUES (%s, %s, %s, %s)", 
                           (passenger_name, 25, 'Male', '9876543210'))
            passenger_id = cursor.lastrowid

            cursor.execute("INSERT INTO bookings (passenger_id, flight_id, date_of_travel, seat_number) VALUES (%s, %s, CURDATE(), %s)", 
                           (passenger_id, flight_id, selected_seat))

            cursor.execute("UPDATE seats SET status = 'Booked' WHERE flight_id = %s AND seat_number = %s", 
                           (flight_id, selected_seat))

            cursor.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE flight_id = %s", (flight_id,))
            conn.commit()
            messagebox.showinfo("Success", f"Seat {selected_seat} booked successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Label(passenger_window, text="Passenger Name:").pack()
    entry_name = ttk.Entry(passenger_window)
    entry_name.pack()

    ttk.Label(passenger_window, text="Flight ID:").pack()
    entry_flight = ttk.Entry(passenger_window)
    entry_flight.pack()

    ttk.Button(passenger_window, text="Show Available Seats", command=show_available_seats).pack()
    seat_list = tk.Listbox(passenger_window)
    seat_list.pack()

    ttk.Button(passenger_window, text="Book Seat", command=book_seat).pack()


# ========== View Available Flights ==========
def open_flight_info():
    flights_window = tk.Toplevel(root)
    flights_window.title("Available Flights")
    flights_window.geometry("600x300")

    def show_flights():
        cursor.execute("SELECT * FROM flights")
        flights = cursor.fetchall()

        for row in tree.get_children():
            tree.delete(row)

        for flight in flights:
            tree.insert("", "end", values=flight)

    columns = ("Flight ID", "Airline", "Source", "Destination", "Departure", "Seats", "Available")
    tree = ttk.Treeview(flights_window, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)

    tree.pack()
    ttk.Button(flights_window, text="Refresh Flights", command=show_flights).pack()
    show_flights()


# ========== Main Menu ==========
ttk.Label(root, text="Welcome to Airport Management System", font=("Arial", 18, "bold")).pack(pady=20)

ttk.Button(root, text="Admin Panel", command=admin_login).pack(pady=10)
ttk.Button(root, text="Passenger Panel", command=open_passenger_panel).pack(pady=10)
ttk.Button(root, text="View Flights", command=open_flight_info).pack(pady=10)

root.mainloop()
