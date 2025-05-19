import customtkinter as ctk
import os
import sys
import subprocess
import mysql.connector
from datetime import datetime
from tkinter import messagebox
from PIL import Image, ImageTk

class PreviousBookingsPage:
    def __init__(self):
        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("Film Booking - Previous Bookings")
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
    def open_login(self):
        """Open login page"""
        try:
            # Close current window
            self.root.destroy()
            
            # Open login page
            subprocess.Popen([sys.executable, "login.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open login page: {e}")

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
            "Bookings": self.create_sidebar_button("📅", "Previous Bookings", is_active=True),
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

        # Content container with padding
        self.content_container = ctk.CTkFrame(main_content, fg_color="black")
        self.content_container.pack(fill="both", expand=True, padx=40, pady=40)

        # Main Title
        title_label = ctk.CTkLabel(
            self.content_container,
            text="Your Previous Bookings",
            font=("Arial", 32, "bold"),
            text_color="white"
        )
        title_label.pack(anchor="w", pady=(0, 30))

        # Get user's bookings
        self.bookings = self.get_user_bookings()

        # Add booking cards or message if no bookings
        if self.bookings:
            # Create scrollable frame for bookings
            self.create_booking_cards()
        else:
            # No bookings message
            self.show_no_bookings_message()

    def create_booking_cards(self):
        """Create a scrollable frame with booking cards"""
        # Create scrollable frame
        booking_frame = ctk.CTkScrollableFrame(
            self.content_container, 
            fg_color="black",
            width=900,
            height=500
        )
        booking_frame.pack(fill="both", expand=True)

        # Add booking cards
        for booking in self.bookings:
            self.create_booking_card(
                booking_frame,
                booking['movie_title'],
                booking['theater_name'],
                booking['show_date'],
                booking['show_time'],
                booking['seats'],
                booking['booking_id'],
                booking['total_price']
            )

    def create_booking_card(self, parent, movie, theater, date, time, seats, booking_id, total_price):
        """Create a styled booking card"""
        # Main card frame with dark gray background
        card = ctk.CTkFrame(
            parent,
            fg_color="#222222",
            corner_radius=10,
            height=120
        )
        card.pack(fill="x", pady=10, padx=5)
        card.pack_propagate(False)  # Maintain consistent height
        
        # Content frame for movie details
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=20, pady=15)
        
        # Movie title
        movie_title = ctk.CTkLabel(
            content,
            text=movie,
            font=("Arial", 20, "bold"),
            text_color="white",
            anchor="w"
        )
        movie_title.pack(anchor="w")
        
        # Movie details (theater, date, time, seats)
        details_frame = ctk.CTkFrame(content, fg_color="transparent")
        details_frame.pack(fill="x", pady=(5, 0))
        
        # Theater info
        theater_label = ctk.CTkLabel(
            details_frame,
            text=f"Theater: {theater}",
            font=("Arial", 14),
            text_color="#aaaaaa",
            anchor="w"
        )
        theater_label.pack(anchor="w")
        
        # Format date
        formatted_date = self.format_date(date)
        
        # Date info
        date_label = ctk.CTkLabel(
            details_frame,
            text=f"Date: {formatted_date}",
            font=("Arial", 14),
            text_color="#aaaaaa",
            anchor="w"
        )
        date_label.pack(anchor="w")
        
        # Time info
        time_label = ctk.CTkLabel(
            details_frame,
            text=f"Time: {time}",
            font=("Arial", 14),
            text_color="#aaaaaa",
            anchor="w"
        )
        time_label.pack(anchor="w")
        
        # Seats info
        seats_label = ctk.CTkLabel(
            details_frame,
            text=f"Seats: {seats}",
            font=("Arial", 14),
            text_color="#aaaaaa",
            anchor="w"
        )
        seats_label.pack(anchor="w")
        
        # Price info
        price_label = ctk.CTkLabel(
            details_frame,
            text=f"Total Price: ${total_price}",
            font=("Arial", 14),
            text_color="#aaaaaa",
            anchor="w"
        )
        price_label.pack(anchor="w")
        
        # Booking ID (small)
        booking_id_label = ctk.CTkLabel(
            details_frame,
            text=f"Booking ID: {booking_id}",
            font=("Arial", 12),
            text_color="#888888",
            anchor="w"
        )
        booking_id_label.pack(anchor="w", pady=(5, 0))
        
        # View ticket button
        view_btn = ctk.CTkButton(
            card,
            text="View Ticket",
            font=("Arial", 14, "bold"),
            fg_color="#d92525",
            text_color="white",
            hover_color="#b71c1c",
            corner_radius=5,
            width=120,
            height=40,
            command=lambda b_id=booking_id, m=movie: self.view_ticket(b_id, m)
        )
        view_btn.pack(side="right", padx=20)
        
        return card

    def show_no_bookings_message(self):
        """Show message when no bookings are found"""
        message_frame = ctk.CTkFrame(self.content_container, fg_color="#222222", corner_radius=10)
        message_frame.pack(fill="x", pady=20, padx=5)
        
        # Message
        ctk.CTkLabel(
            message_frame,
            text="You don't have any bookings yet.",
            font=("Arial", 18),
            text_color="white"
        ).pack(pady=(30, 10))
        
        # Subtext
        ctk.CTkLabel(
            message_frame,
            text="Explore movies and book your first ticket!",
            font=("Arial", 14),
            text_color="#aaaaaa"
        ).pack(pady=(0, 20))
        
        # Browse movies button
        browse_btn = ctk.CTkButton(
            message_frame,
            text="Browse Movies",
            font=("Arial", 14, "bold"),
            fg_color="#d92525",
            text_color="white",
            hover_color="#b71c1c",
            corner_radius=5,
            width=150,
            height=40,
            command=self.open_home_page
        )
        browse_btn.pack(pady=(10, 30))

    def view_ticket(self, booking_id, movie_title):
        """Show ticket details in a popup window"""
        # Get detailed booking information
        booking_details = self.get_booking_details(booking_id)
        
        if not booking_details:
            messagebox.showerror("Error", "Could not retrieve booking details.")
            return
            
        # Create ticket window
        ticket_window = ctk.CTkToplevel(self.root)
        ticket_window.title(f"Ticket - {movie_title}")
        ticket_window.geometry("600x700")
        ticket_window.grab_set()  # Make window modal
        
        # Main container
        ticket_container = ctk.CTkFrame(ticket_window, fg_color="#222222")
        ticket_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Ticket header
        header = ctk.CTkFrame(ticket_container, fg_color="#d92525", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Film Booking logo/title
        ctk.CTkLabel(
            header,
            text="Film Booking",
            font=("Arial", 24, "bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Movie title
        ctk.CTkLabel(
            ticket_container,
            text=movie_title,
            font=("Arial", 28, "bold"),
            text_color="white"
        ).pack(pady=(20, 5))
        
        # Create info grid
        info_frame = ctk.CTkFrame(ticket_container, fg_color="transparent")
        info_frame.pack(fill="x", pady=20, padx=30)
        
        # Add ticket information
        self.add_ticket_info(info_frame, "Date:", booking_details['show_date'])
        self.add_ticket_info(info_frame, "Time:", booking_details['show_time'])
        self.add_ticket_info(info_frame, "Theater:", booking_details['theater_name'])
        self.add_ticket_info(info_frame, "Seats:", booking_details['seats'])
        self.add_ticket_info(info_frame, "Total Price:", f"${booking_details['total_price']}")
        
        # QR code placeholder
        qr_frame = ctk.CTkFrame(ticket_container, fg_color="#333333", width=200, height=200)
        qr_frame.pack(pady=20)
        
        # QR Code text
        ctk.CTkLabel(
            qr_frame,
            text="QR Code",
            font=("Arial", 20),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Booking ID
        ctk.CTkLabel(
            ticket_container,
            text=f"Booking ID: {booking_id}",
            font=("Arial", 14),
            text_color="#aaaaaa"
        ).pack(pady=5)
        
        # PDF Download Button
        download_btn = ctk.CTkButton(
            ticket_container,
            text="Download PDF",
            font=("Arial", 14, "bold"),
            fg_color="#d92525",
            text_color="white",
            hover_color="#b71c1c",
            corner_radius=5,
            width=150,
            height=40,
            command=lambda: self.download_ticket_pdf(booking_id)
        )
        download_btn.pack(pady=20)

    def add_ticket_info(self, parent, label_text, value_text):
        """Add a row of information to the ticket details"""
        frame = ctk.CTkFrame(parent, fg_color="transparent", height=30)
        frame.pack(fill="x", pady=5)
        frame.pack_propagate(False)
        
        # Label
        ctk.CTkLabel(
            frame,
            text=label_text,
            font=("Arial", 16, "bold"),
            text_color="white",
            width=120
        ).pack(side="left")
        
        # Value
        ctk.CTkLabel(
            frame,
            text=value_text,
            font=("Arial", 16),
            text_color="white"
        ).pack(side="left")

    def download_ticket_pdf(self, booking_id):
        """Download ticket as PDF (placeholder functionality)"""
        messagebox.showinfo("Download PDF", f"Downloading ticket PDF for booking {booking_id}...\n\nThis feature would generate and download a PDF of the ticket.")

    def navigate_to(self, screen_name):
        """Handle navigation between different screens"""
        # Close current window
        self.root.withdraw()
        
        try:
            if screen_name == "Home":
                # Open Home page
                self.open_home_page()
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
            elif screen_name == "Previous Bookings":
                # Refresh current page
                self.root.deiconify()
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

    # Database methods
    def get_user_bookings(self):
        """Get user's bookings from database"""
        if not self.user_id:
            return []
            
        try:
            connection = mysql.connector.connect(**self.DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT b.bookingID, b.totalPrice, b.numTickets,
                   m.movieTitle, t.theaterName, 
                   s.showDate, s.showTime
            FROM Bookings b
            JOIN Show s ON b.showID = s.showID
            JOIN Movies m ON s.movieID = m.movieID
            JOIN Theaters t ON s.theaterID = t.theaterID
            WHERE b.userID = %s
            ORDER BY s.showDate DESC, s.showTime DESC
            """
            
            cursor.execute(query, (self.user_id,))
            bookings = cursor.fetchall()
            
            # Format the bookings data
            formatted_bookings = []
            for booking in bookings:
                # Get seats for this booking (placeholder - your DB structure might differ)
                seats = self.get_booking_seats(booking['bookingID'])
                
                formatted_bookings.append({
                    'booking_id': booking['bookingID'],
                    'total_price': booking['totalPrice'],
                    'movie_title': booking['movieTitle'],
                    'theater_name': booking['theaterName'],
                    'show_date': booking['showDate'],
                    'show_time': booking['showTime'],
                    'seats': seats
                })
            
            return formatted_bookings
        except Exception as e:
            print(f"Database error: {e}")
            return []
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def get_booking_seats(self, booking_id):
        """Get seats for a specific booking (placeholder)"""
        # In a real implementation, you would query your database
        # for the actual seats associated with this booking
        
        # For now, we'll return a placeholder based on booking_id
        seat_rows = ['A', 'B', 'C', 'D', 'E', 'F']
        seat_number = booking_id % 10
        
        # Generate some dummy seats
        seats = []
        for i in range(1, (booking_id % 3) + 2):  # 1-3 seats
            row = seat_rows[(booking_id + i) % len(seat_rows)]
            number = (seat_number + i) % 10 + 1
            seats.append(f"{row}{number}")
        
        return ", ".join(seats)

    def get_booking_details(self, booking_id):
        """Get detailed information for a specific booking"""
        try:
            connection = mysql.connector.connect(**self.DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT b.bookingID, b.totalPrice, b.numTickets,
                   m.movieTitle, t.theaterName, 
                   s.showDate, s.showTime
            FROM Bookings b
            JOIN Show s ON b.showID = s.showID
            JOIN Movies m ON s.movieID = m.movieID
            JOIN Theaters t ON s.theaterID = t.theaterID
            WHERE b.bookingID = %s
            """
            
            cursor.execute(query, (booking_id,))
            booking = cursor.fetchone()
            
            if not booking:
                return None
                
            # Get seats
            seats = self.get_booking_seats(booking_id)
                
            # Format the booking details
            details = {
                'booking_id': booking['bookingID'],
                'total_price': booking['totalPrice'],
                'movie_title': booking['movieTitle'],
                'theater_name': booking['theaterName'],
                'show_date': self.format_date(booking['showDate']),
                'show_time': booking['showTime'],
                'seats': seats,
                'num_tickets': booking['numTickets']
            }
            
            return details
        except Exception as e:
            print(f"Database error: {e}")
            return None
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def run(self):
        """Run the previous bookings application"""
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    bookings_page = PreviousBookingsPage()
    bookings_page.run()