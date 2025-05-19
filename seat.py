import customtkinter as ctk
import os
import sys
import subprocess
import mysql.connector
from datetime import datetime
from tkinter import messagebox

class SeatSelectionPage:
    def __init__(self):
        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("Film Booking - Select Your Seats")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)

        # Set appearance mode
        ctk.set_appearance_mode("dark")

        # Database configuration
        self.DB_CONFIG = {
            'host': 'localhost',
            'user': 'root',
            'password': 'new_password',  # Update with your MySQL password
            'database': 'film_booking'
        }

        # Load user session
        self.user_id = None
        self.user_name = None
        self.user_role = None
        self.load_user_session()

        # Load selected show information
        self.show_id = None
        self.movie_title = None
        self.theater_name = None
        self.show_date = None
        self.show_time = None
        self.load_selected_show()

        # Initialize seat selection variables
        self.selected_seats = set()
        self.seat_status = {}  # Will store status of each seat (available, unavailable, selected)
        self.seat_buttons = {}  # Will store references to seat buttons
        self.seat_colors = {
            "available": "#008000",   # Green
            "selected": "#FFD700",    # Yellow
            "unavailable": "#808080"  # Gray
        }

        # Get already booked seats for this show
        self.get_booked_seats()

        # Create UI components
        self.create_sidebar()
        self.create_main_content()

    def load_user_session(self):
        """Load user session data from file"""
        try:
            with open("session.txt", "r") as file:
                lines = file.readlines()
                session_data = {}
                for line in lines:
                    key, value = line.strip().split('=', 1)
                    session_data[key] = value

                # Use dictionary get method with a default value
                self.user_id = session_data.get('user_id') or session_data.get('userID')
                self.user_name = session_data.get('name')
                self.user_role = session_data.get('role')
                
                # More robust validation
                if not self.user_id:
                    raise ValueError("No user ID found in session")
        except Exception as e:
            print(f"Error loading session: {e}")
            # Instead of directly logging out, show a message and redirect to login
            messagebox.showerror("Session Error", "Your session has expired. Please log in again.")
            self.open_login()

    def load_selected_show(self):
        """Load selected show data from file"""
        try:
            with open("selected_show.txt", "r") as file:
                lines = file.readlines()
                for line in lines:
                    if "show_id=" in line:
                        self.show_id = line.strip().split("=")[1]
                    elif "movie_title=" in line:
                        self.movie_title = line.strip().split("=")[1]
                    elif "theater_name=" in line:
                        self.theater_name = line.strip().split("=")[1]
                    elif "show_date=" in line:
                        self.show_date = line.strip().split("=")[1]
                    elif "show_time=" in line:
                        self.show_time = line.strip().split("=")[1]
            
            # If no show ID, go back to home
            if not self.show_id:
                raise Exception("No show ID found")
        except Exception as e:
            print(f"Error loading selected show: {e}")
            # Go back to home page if show data can't be loaded
            self.open_home_page()

    def get_booked_seats(self):
        """Get already booked seats for this show from database"""
        try:
            # This is a placeholder function - in a real implementation, 
            # you would query your database to get seats that are already booked
            # For now, we'll set some seats as unavailable for demonstration
            
            # In a real implementation, you might do something like:
            # connection = mysql.connector.connect(**self.DB_CONFIG)
            # cursor = connection.cursor()
            # query = "SELECT seat_number FROM Booking_Seats WHERE show_id = %s"
            # cursor.execute(query, (self.show_id,))
            # booked_seats = [row[0] for row in cursor.fetchall()]
            
            # For demonstration, we'll mark some seats as unavailable
            booked_seats = ["A3", "A6", "A10", "B6", "B10"]
            
            # Set status for each booked seat
            for seat in booked_seats:
                self.seat_status[seat] = "unavailable"
                
        except Exception as e:
            print(f"Error getting booked seats: {e}")

    def create_sidebar(self):
        # Sidebar Frame
        self.sidebar = ctk.CTkFrame(self.root, fg_color="#d92525", width=300, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)  # Prevent the frame from shrinking

        # Sidebar Title
        ctk.CTkLabel(self.sidebar, text="Film Booking", 
                     font=("Arial", 28, "bold"), 
                     text_color="white").pack(pady=(40, 30), padx=20, anchor="w")
                     
        # User Welcome Message
        if self.user_name:
            ctk.CTkLabel(self.sidebar, text=f"Welcome, {self.user_name}", 
                        font=("Arial", 16), 
                        text_color="white").pack(pady=(0, 30), padx=20, anchor="w")

        # Create navigation buttons
        self.buttons = {
            "Home": self.create_sidebar_button("🏠", "Home"),
            "Bookings": self.create_sidebar_button("📅", "Previous Bookings"),
            "Profile": self.create_sidebar_button("👤", "Profile"),
            "About": self.create_sidebar_button("ℹ️", "About")
        }
        
        # Add admin button if user has admin role
        if self.user_role == "admin":
            self.buttons["Admin"] = self.create_sidebar_button("⚙️", "Admin Dashboard")

        # Logout button
        self.create_logout_button()

    def create_sidebar_button(self, icon, text, is_active=False):
        button_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=40)
        button_frame.pack(fill="x", pady=3)
        button_frame.pack_propagate(False)

        # Icon
        icon_label = ctk.CTkLabel(button_frame, text=icon, 
                                  font=("Arial", 16), 
                                  text_color="white", 
                                  width=30)
        icon_label.pack(side="left", padx=(20, 10))

        # Text
        text_label = ctk.CTkLabel(button_frame, text=text, 
                                  font=("Arial", 16), 
                                  text_color="white", 
                                  anchor="w")
        text_label.pack(side="left", fill="x", expand=True)

        # Hover and click effects
        def on_enter(e):
            button_frame.configure(fg_color="#b71c1c")
        def on_leave(e):
            button_frame.configure(fg_color="#b71c1c" if is_active else "transparent")
        def on_click(e):
            self.navigate_to(text)

        # Bind events to entire frame and its children
        for widget in [button_frame, icon_label, text_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

        # Set initial state if active
        if is_active:
            button_frame.configure(fg_color="#b71c1c")

        return button_frame

    def create_logout_button(self):
        logout_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=40)
        logout_frame.pack(side="bottom", fill="x", pady=(0, 30))
        logout_frame.pack_propagate(False)

        logout_icon = ctk.CTkLabel(logout_frame, text="📤", 
                                   font=("Arial", 16), 
                                   text_color="white", 
                                   width=30)
        logout_icon.pack(side="left", padx=(20, 10))

        logout_text = ctk.CTkLabel(logout_frame, text="Logout", 
                                   font=("Arial", 16), 
                                   text_color="white", 
                                   anchor="w")
        logout_text.pack(side="left")

        # Hover and click effects
        def on_enter(e):
            logout_frame.configure(fg_color="#b71c1c")
        def on_leave(e):
            logout_frame.configure(fg_color="transparent")
        def on_logout(e):
            self.logout()

        for widget in [logout_frame, logout_icon, logout_text]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_logout)

    def create_main_content(self):
        # Main Content Frame
        main_content = ctk.CTkFrame(self.root, fg_color="black", corner_radius=0)
        main_content.pack(side="right", fill="both", expand=True)

        # Center the content vertically and horizontally
        content_container = ctk.CTkFrame(main_content, fg_color="black")
        content_container.place(relx=0.5, rely=0.5, anchor="center")

        # Movie and show information
        info_frame = ctk.CTkFrame(content_container, fg_color="black")
        info_frame.pack(pady=(0, 20))
        
        if self.movie_title:
            ctk.CTkLabel(
                info_frame,
                text=self.movie_title,
                font=("Arial", 24, "bold"),
                text_color="white"
            ).pack()
        
        if self.theater_name and self.show_date and self.show_time:
            # Format date if available
            formatted_date = self.format_date(self.show_date) if self.show_date else "Unknown Date"
            
            show_info = f"{self.theater_name} | {formatted_date} | {self.show_time}"
            ctk.CTkLabel(
                info_frame,
                text=show_info,
                font=("Arial", 16),
                text_color="#aaaaaa"
            ).pack(pady=(5, 0))

        # Title
        title_label = ctk.CTkLabel(
            content_container, 
            text="Select Your Seats", 
            font=("Arial", 28, "bold"), 
            text_color="white"
        )
        title_label.pack(pady=(0, 20))

        # Screen display
        screen_label = ctk.CTkLabel(
            content_container, 
            text="SCREEN", 
            font=("Arial", 16, "bold"), 
            text_color="white",
            fg_color="#d92525",  # Red background
            width=700,  # Wider screen
            height=40,
            corner_radius=0
        )
        screen_label.pack(pady=(0, 40))

        # Seat grid container
        seat_grid = ctk.CTkFrame(content_container, fg_color="black")
        seat_grid.pack(pady=(0, 30))

        # Create the seat grid
        self.create_seat_grid(seat_grid)

        # Seat legend
        self.create_seat_legend(content_container)

        # Create the "Proceed to Checkout" button
        self.checkout_btn = ctk.CTkButton(
            content_container,
            text="Proceed to Checkout",
            font=("Arial", 16, "bold"),
            fg_color="#d92525",  # Red background
            text_color="white",
            hover_color="#b71c1c",
            corner_radius=5,
            height=45,
            width=200,
            command=self.proceed_to_checkout
        )
        self.checkout_btn.pack(pady=20)

        # Enable checkout button only if seats are selected
        if not self.selected_seats:
            self.checkout_btn.configure(state="disabled", fg_color="#999999", hover_color="#999999")

    def create_seat_grid(self, parent):
        """Create the grid of seat buttons"""
        # Create seat rows
        rows = ["A", "B", "C", "D", "E", "F"]
        columns = list(range(1, 11))

        # Create each row of seats
        for i, row in enumerate(rows):
            row_frame = ctk.CTkFrame(parent, fg_color="black")
            row_frame.pack(pady=5)
            
            # Add row label on the left
            row_label = ctk.CTkLabel(
                row_frame,
                text=row,
                font=("Arial", 14, "bold"),
                text_color="white",
                width=30
            )
            row_label.pack(side="left", padx=(0, 10))
            
            for col in columns:
                seat_id = f"{row}{col}"
                status = self.seat_status.get(seat_id, "available")
                
                # Determine seat color based on status
                if status == "unavailable":
                    color = self.seat_colors["unavailable"]
                elif status == "selected":
                    color = self.seat_colors["selected"]
                    self.selected_seats.add(seat_id)  # Add to selected seats if pre-selected
                else:
                    color = self.seat_colors["available"]
                
                # Create the seat button
                seat_btn = ctk.CTkButton(
                    row_frame,
                    text=seat_id,
                    font=("Arial", 14, "bold"),
                    fg_color=color,
                    text_color="white",
                    hover_color=color if status == "unavailable" else "#005000" if status == "available" else "#DAA520",
                    width=50,
                    height=50,
                    corner_radius=5
                )
                seat_btn.pack(side="left", padx=5)
                
                # Store button reference and add command if seat is available
                self.seat_buttons[seat_id] = seat_btn
                
                if status != "unavailable":
                    seat_btn.configure(command=lambda s=seat_id, b=seat_btn: self.toggle_seat(s, b))

    def create_seat_legend(self, parent):
        """Create legend explaining seat colors"""
        legend_frame = ctk.CTkFrame(parent, fg_color="black")
        legend_frame.pack(pady=(0, 20))
        
        # Available seat
        available_frame = ctk.CTkFrame(legend_frame, fg_color="transparent")
        available_frame.pack(side="left", padx=20)
        
        available_box = ctk.CTkLabel(
            available_frame,
            text="",
            width=20,
            height=20,
            fg_color=self.seat_colors["available"],
            corner_radius=5
        )
        available_box.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(
            available_frame,
            text="Available",
            font=("Arial", 12),
            text_color="white"
        ).pack(side="left")
        
        # Selected seat
        selected_frame = ctk.CTkFrame(legend_frame, fg_color="transparent")
        selected_frame.pack(side="left", padx=20)
        
        selected_box = ctk.CTkLabel(
            selected_frame,
            text="",
            width=20,
            height=20,
            fg_color=self.seat_colors["selected"],
            corner_radius=5
        )
        selected_box.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(
            selected_frame,
            text="Selected",
            font=("Arial", 12),
            text_color="white"
        ).pack(side="left")
        
        # Unavailable seat
        unavailable_frame = ctk.CTkFrame(legend_frame, fg_color="transparent")
        unavailable_frame.pack(side="left", padx=20)
        
        unavailable_box = ctk.CTkLabel(
            unavailable_frame,
            text="",
            width=20,
            height=20,
            fg_color=self.seat_colors["unavailable"],
            corner_radius=5
        )
        unavailable_box.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(
            unavailable_frame,
            text="Booked",
            font=("Arial", 12),
            text_color="white"
        ).pack(side="left")

    def toggle_seat(self, seat, button):
        """Toggle seat selection"""
        if self.seat_status.get(seat, "available") == "unavailable":
            return  # Ignore clicks on unavailable seats
        
        current_status = "selected" if seat in self.selected_seats else "available"
        
        if current_status == "selected":
            self.selected_seats.remove(seat)
            button.configure(fg_color=self.seat_colors["available"])
        else:
            self.selected_seats.add(seat)
            button.configure(fg_color=self.seat_colors["selected"])
        
        # Update the "Proceed to Checkout" button based on selection
        if self.selected_seats:
            self.checkout_btn.configure(state="normal", fg_color="#d92525", hover_color="#b71c1c")
        else:
            self.checkout_btn.configure(state="disabled", fg_color="#999999", hover_color="#999999")
        
        # Update number of tickets and total in the UI
        self.update_ticket_total()
        
        # Print selected seats for debugging
        print(f"Selected seats: {self.selected_seats}")

    def update_ticket_total(self):
        """Update ticket count and total (placeholder - would be implemented in real app)"""
        # This would typically update a UI element showing the number of tickets and total price
        # For now, we just print to console
        ticket_price = 12.50  # Example ticket price
        num_tickets = len(self.selected_seats)
        total = num_tickets * ticket_price
        
        print(f"Tickets: {num_tickets}, Total: ${total:.2f}")

    def proceed_to_checkout(self):
        """Handle checkout process"""
        if not self.selected_seats:
            messagebox.showwarning("No Seats Selected", "Please select at least one seat to proceed.")
            return
            
        try:
            # Create a booking
            booking_id = self.create_booking()
            
            if booking_id:
                messagebox.showinfo("Booking Successful", 
                                   f"Booking confirmed! Your seats: {', '.join(sorted(self.selected_seats))}")
                
                # Redirect to booking confirmation or home page
                self.open_home_page()
            else:
                messagebox.showerror("Booking Error", "Unable to complete booking. Please try again.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during checkout: {e}")

    def create_booking(self):
        """Create a booking in the database (placeholder)"""
        # This is a placeholder function - in a real implementation, 
        # you would insert the booking into your database
        
        try:
            # Calculate total price
            ticket_price = 12.50  # Example ticket price
            num_tickets = len(self.selected_seats)
            total_price = num_tickets * ticket_price
            
            # In a real implementation, you might do something like:
            # connection = mysql.connector.connect(**self.DB_CONFIG)
            # cursor = connection.cursor()
            # cursor.execute(
            #    "INSERT INTO Bookings (userID, showID, numTickets, totalPrice) VALUES (%s, %s, %s, %s)",
            #    (self.user_id, self.show_id, num_tickets, total_price)
            # )
            # booking_id = cursor.lastrowid
            # 
            # # Insert seats
            # for seat in self.selected_seats:
            #    cursor.execute(
            #        "INSERT INTO Booking_Seats (bookingID, seatNumber) VALUES (%s, %s)",
            #        (booking_id, seat)
            #    )
            #
            # connection.commit()
            
            # For demonstration, we'll return a dummy booking ID
            return 12345
            
        except Exception as e:
            print(f"Error creating booking: {e}")
            return None

    def navigate_to(self, screen_name):
        """Handle navigation between different screens"""
        # Close current window
        self.root.withdraw()
        
        try:
            if screen_name == "Home":
                # Open Home page
                self.open_home_page()
            elif screen_name == "Previous Bookings":
                # Open Bookings page
                subprocess.Popen([sys.executable, "prevbook.py"])
                self.root.destroy()
            elif screen_name == "Profile":
                # Open Profile page
                subprocess.Popen([sys.executable, "profile.py"])
                self.root.destroy()
            elif screen_name == "About":
                # Open About page
                subprocess.Popen([sys.executable, "about.py"])
                self.root.destroy()
            elif screen_name == "Admin Dashboard" and self.user_role == "admin":
                # Open Admin page
                subprocess.Popen([sys.executable, "admin.py"])
                self.root.destroy()
        except Exception as e:
            print(f"Navigation error: {e}")
            # Reopen current window if navigation fails
            self.root.deiconify()

    def open_home_page(self):
        """Open the home page"""
        try:
            subprocess.Popen([sys.executable, "home.py"])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open home page: {e}")

    def logout(self):
        """Handle logout functionality"""
        try:
            # Remove session file
            if os.path.exists("session.txt"):
                os.remove("session.txt")
                
            # Close current window
            self.root.destroy()
            
            # Open login page
            subprocess.Popen([sys.executable, "login.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Logout error: {e}")

    # Helper methods
    def format_date(self, date_str):
        """Format date string for display"""
        try:
            # Parse date string to datetime object
            date_obj = datetime.strptime(str(date_str), "%Y-%m-%d")
            # Format as "Monday, April 10, 2023"
            return date_obj.strftime("%A, %B %d, %Y")
        except Exception as e:
            print(f"Date formatting error: {e}")
            return date_str  # Return original if error

    def run(self):
        """Run the seat selection application"""
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    seat_page = SeatSelectionPage()
    seat_page.run()