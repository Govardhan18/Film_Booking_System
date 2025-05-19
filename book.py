import customtkinter as ctk
from PIL import Image, ImageTk
import os
import sys
import subprocess
import mysql.connector
from datetime import datetime
from tkinter import messagebox

class MovieBookingPage:
    def __init__(self):
        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("Film Booking - Movie Details")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)

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

        # Load selected movie
        self.movie_id = None
        self.movie_title = None
        self.load_selected_movie()

        # Get movie details from database
        self.movie_details = self.get_movie_details() if self.movie_id else None

        # Create UI components
        self.create_sidebar()
        self.create_main_content()

    def load_user_session(self):
        """Load user session data from file"""
        try:
            with open("session.txt", "r") as file:
                lines = file.readlines()
                for line in lines:
                    if "user_id=" in line:
                        self.user_id = line.strip().split("=")[1]
                    elif "name=" in line:
                        self.user_name = line.strip().split("=")[1]
                    elif "role=" in line:
                        self.user_role = line.strip().split("=")[1]
        except Exception as e:
            print(f"Error loading session: {e}")
            # Redirect to login if session can't be loaded
            self.logout()

    def load_selected_movie(self):
        """Load selected movie from file"""
        try:
            with open("selected_movie.txt", "r") as file:
                lines = file.readlines()
                for line in lines:
                    if "movie_id=" in line:
                        self.movie_id = line.strip().split("=")[1]
                    elif "movie_title=" in line:
                        self.movie_title = line.strip().split("=")[1]
        except Exception as e:
            print(f"Error loading selected movie: {e}")
            # If we can't load the movie, go back to home
            self.open_home_page()

    def create_sidebar(self):
        # Sidebar Frame
        self.sidebar = ctk.CTkFrame(self.root, fg_color="#d92525", width=300, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

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
            "Home": self.create_sidebar_button("🏠", "Home", is_active=True),
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

        # Content container with padding
        content_container = ctk.CTkFrame(main_content, fg_color="black")
        content_container.pack(fill="both", expand=True, padx=40, pady=40)

        if not self.movie_details:
            # Display error message if movie details not found
            ctk.CTkLabel(
                content_container,
                text="Movie details not found. Please go back and try again.",
                font=("Arial", 18),
                text_color="white"
            ).pack(pady=50)
            
            # Back button
            back_btn = ctk.CTkButton(
                content_container,
                text="Back to Home",
                font=("Arial", 16),
                fg_color="#d92525",
                hover_color="#b71c1c",
                command=self.open_home_page
            )
            back_btn.pack(pady=20)
            
            return

        # Movie content layout using grid
        movie_content = ctk.CTkFrame(content_container, fg_color="black")
        movie_content.pack(fill="both", expand=True)

        # Movie Poster
        self.create_movie_poster(movie_content)

        # Movie Details
        self.create_movie_details(movie_content)

    def create_movie_poster(self, parent):
        poster_frame = ctk.CTkFrame(parent, fg_color="black", width=300, height=450)
        poster_frame.grid(row=0, column=0, padx=(0, 30), sticky="nw")
        poster_frame.grid_propagate(False)  # Maintain size

        # Try to load movie poster image
        image_path = f"images/{self.movie_id}.jpg"
        if not os.path.exists(image_path):
            image_path = "images/default.jpg"  # Fallback to default

        try:
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img = img.resize((300, 450), Image.LANCZOS)
                movie_img = ImageTk.PhotoImage(img)
                img_label = ctk.CTkLabel(poster_frame, image=movie_img, text="")
                img_label.image = movie_img  # Keep a reference
                img_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                # Placeholder if image not found
                placeholder = ctk.CTkFrame(poster_frame, fg_color="#333333", corner_radius=10, width=300, height=450)
                placeholder.place(relx=0.5, rely=0.5, anchor="center")
                
                # Movie title on placeholder
                ctk.CTkLabel(
                    placeholder, 
                    text=self.movie_details['movieTitle'], 
                    font=("Arial", 20, "bold"), 
                    text_color="white",
                    wraplength=250
                ).place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            print(f"Error loading image: {e}")
            # Placeholder if image loading fails
            placeholder = ctk.CTkFrame(poster_frame, fg_color="#333333", corner_radius=10, width=300, height=450)
            placeholder.place(relx=0.5, rely=0.5, anchor="center")
            
            # Movie title on placeholder
            ctk.CTkLabel(
                placeholder, 
                text=self.movie_details['movieTitle'], 
                font=("Arial", 20, "bold"), 
                text_color="white",
                wraplength=250
            ).place(relx=0.5, rely=0.5, anchor="center")

    def create_movie_details(self, parent):
        details_frame = ctk.CTkFrame(parent, fg_color="black")
        details_frame.grid(row=0, column=1, sticky="nw")

        # Movie title with large bold font
        title_label = ctk.CTkLabel(
            details_frame, 
            text=self.movie_details['movieTitle'], 
            font=("Arial", 32, "bold"), 
            text_color="white"
        )
        title_label.pack(anchor="w", pady=(0, 10))

        # Movie metadata (genre, duration, rating)
        metadata = f"{self.movie_details['movieGenre']} | {self.movie_details['movieDuration']} minutes | Rating: {self.movie_details['movieRating']}/10"
        metadata_label = ctk.CTkLabel(
            details_frame, 
            text=metadata, 
            font=("Arial", 16), 
            text_color="#aaaaaa"
        )
        metadata_label.pack(anchor="w", pady=(0, 20))

        # Movie description (if available)
        if 'description' in self.movie_details and self.movie_details['description']:
            description_text = self.movie_details['description']
        else:
            # Generic description if not available
            description_text = f"Experience the magic of '{self.movie_details['movieTitle']}' on the big screen. " \
                              f"This {self.movie_details['movieGenre']} film runs for {self.movie_details['movieDuration']} minutes " \
                              f"and has received a rating of {self.movie_details['movieRating']}/10."
        
        description_label = ctk.CTkLabel(
            details_frame, 
            text=description_text, 
            font=("Arial", 16), 
            text_color="white",
            wraplength=600,
            justify="left"
        )
        description_label.pack(anchor="w", pady=(0, 30))

        # Show times section
        self.create_showtimes_section(details_frame)

    def create_showtimes_section(self, parent):
        # Show times title
        showtimes_label = ctk.CTkLabel(
            parent, 
            text="Available Show Times:", 
            font=("Arial", 18, "bold"), 
            text_color="white"
        )
        showtimes_label.pack(anchor="w", pady=(0, 15))

        # Get show times for this movie
        shows = self.get_movie_showtimes()

        if not shows:
            # No shows available
            ctk.CTkLabel(
                parent,
                text="No showtimes currently available for this movie.",
                font=("Arial", 14),
                text_color="#aaaaaa"
            ).pack(anchor="w", pady=(0, 20))
            return

        # Group shows by date
        show_dates = {}
        for show in shows:
            date = show['showDate']
            if date not in show_dates:
                show_dates[date] = []
            show_dates[date].append(show)

        # Create date tabs container
        dates_frame = ctk.CTkFrame(parent, fg_color="black")
        dates_frame.pack(fill="x", pady=(0, 15))

        # Show content frame (where times will be displayed)
        self.shows_content_frame = ctk.CTkFrame(parent, fg_color="#222222", corner_radius=10)
        self.shows_content_frame.pack(fill="x", pady=(0, 20))

        # Track active date button
        self.active_date_btn = None
        self.date_buttons = {}

        # Create a button for each date
        for i, date in enumerate(sorted(show_dates.keys())):
            # Format date for display
            formatted_date = self.format_date(date)
            
            # Create date button
            date_btn = ctk.CTkButton(
                dates_frame,
                text=formatted_date,
                font=("Arial", 14),
                fg_color="#333333" if i > 0 else "#d92525",  # First date active by default
                text_color="white",
                hover_color="#b71c1c",
                width=120,
                height=40,
                corner_radius=5,
                command=lambda d=date, shows=show_dates[date]: self.show_times_for_date(d, shows)
            )
            date_btn.pack(side="left", padx=(0, 10))
            
            # Store reference to button
            self.date_buttons[date] = date_btn
            
            # Set first date as active by default
            if i == 0:
                self.active_date_btn = date_btn
                # Show times for first date
                self.show_times_for_date(date, show_dates[date])

    def show_times_for_date(self, date, shows):
        """Show all times for the selected date"""
        # Update active button
        if self.active_date_btn:
            self.active_date_btn.configure(fg_color="#333333")
        self.active_date_btn = self.date_buttons[date]
        self.active_date_btn.configure(fg_color="#d92525")
        
        # Clear existing content
        for widget in self.shows_content_frame.winfo_children():
            widget.destroy()
            
        # Group shows by theater
        theaters = {}
        for show in shows:
            theater_id = show['theaterID']
            if theater_id not in theaters:
                # Get theater name
                theater_name = self.get_theater_name(theater_id)
                theaters[theater_id] = {
                    'name': theater_name,
                    'shows': []
                }
            theaters[theater_id]['shows'].append(show)
            
        # Create content for each theater
        for theater_id, theater_data in theaters.items():
            # Theater name
            theater_label = ctk.CTkLabel(
                self.shows_content_frame,
                text=theater_data['name'],
                font=("Arial", 16, "bold"),
                text_color="white"
            )
            theater_label.pack(anchor="w", padx=20, pady=(15, 10))
            
            # Times container
            times_frame = ctk.CTkFrame(self.shows_content_frame, fg_color="transparent")
            times_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            # Add time buttons
            for show in theater_data['shows']:
                time_btn = ctk.CTkButton(
                    times_frame,
                    text=show['showTime'],
                    font=("Arial", 14),
                    fg_color="#d92525",
                    text_color="white",
                    hover_color="#b71c1c",
                    width=100,
                    height=35,
                    corner_radius=5,
                    command=lambda s=show, tn=theater_data['name']: self.select_showtime(s, tn)
                )
                time_btn.pack(side="left", padx=(0, 10), pady=5)

    def select_showtime(self, show, theater_name):
        """Handle selection of a specific showtime"""
        try:
            # Save show information for seat selection page
            with open("selected_show.txt", "w") as file:
                file.write(f"show_id={show['showID']}\n")
                file.write(f"movie_title={self.movie_details['movieTitle']}\n")
                file.write(f"theater_name={theater_name}\n")
                file.write(f"show_date={show['showDate']}\n")
                file.write(f"show_time={show['showTime']}\n")
                
            # Open seat selection page
            subprocess.Popen([sys.executable, "seat.py"])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to proceed to seat selection: {e}")

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
            # Format as "Mon, Apr 10"
            return date_obj.strftime("%a, %b %d")
        except Exception as e:
            print(f"Date formatting error: {e}")
            return date_str  # Return original if error

    # Database methods
    def get_movie_details(self):
        """Get movie details from database"""
        if not self.movie_id:
            return None
            
        try:
            connection = mysql.connector.connect(**self.DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM Movies WHERE movieID = %s"
            cursor.execute(query, (self.movie_id,))
            movie = cursor.fetchone()
            
            return movie
        except Exception as e:
            print(f"Database error: {e}")
            return None
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def get_movie_showtimes(self):
        """Get showtimes for this movie"""
        if not self.movie_id:
            return []
            
        try:
            connection = mysql.connector.connect(**self.DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            # Get upcoming shows for this movie
            query = """
            SELECT * FROM Show 
            WHERE movieID = %s AND showDate >= CURDATE()
            ORDER BY showDate, showTime
            """
            
            cursor.execute(query, (self.movie_id,))
            shows = cursor.fetchall()
            
            return shows
        except Exception as e:
            print(f"Database error: {e}")
            return []
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def get_theater_name(self, theater_id):
        """Get theater name by ID"""
        try:
            connection = mysql.connector.connect(**self.DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT theaterName FROM Theaters WHERE theaterID = %s"
            cursor.execute(query, (theater_id,))
            result = cursor.fetchone()
            
            return result['theaterName'] if result else f"Theater {theater_id}"
        except Exception as e:
            print(f"Database error: {e}")
            return f"Theater {theater_id}"
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def run(self):
        """Run the movie booking application"""
        # Ensure images directory exists
        if not os.path.exists("images"):
            os.makedirs("images")
            
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    booking_page = MovieBookingPage()
    booking_page.run()