import customtkinter as ctk
from PIL import Image, ImageTk
import os
import sys
import subprocess
import mysql.connector
from datetime import datetime
from tkinter import messagebox
import random

class HomePage:
    def __init__(self, previous_window=None):
        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("Film Booking - Homepage")
        self.root.geometry("1920x1080")
        self.root.resizable(False, False)

        # Store reference to previous window
        self.previous_window = previous_window

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

        # Ensure images directory exists
        if not os.path.exists("images"):
            os.makedirs("images")
            print("Created 'images' directory for movie posters.")

        # Create UI components
        self.create_sidebar()
        self.create_main_content()

    def load_user_session(self):
        """Load user session data from file"""
        try:
            with open("session.txt", "r") as file:
                lines = file.readlines()
                for line in lines:
                    if "userID=" in line:
                        self.user_id = line.strip().split("=")[1]
                    elif "name=" in line:
                        self.user_name = line.strip().split("=")[1]
                    elif "role=" in line:
                        self.user_role = line.strip().split("=")[1]
        except Exception as e:
            print(f"Error loading session: {e}")
            # If session can't be loaded, continue without user info

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

        # Content Container
        content_container = ctk.CTkFrame(main_content, fg_color="black")
        content_container.pack(fill="both", expand=True, padx=40, pady=40)

        # Welcome Title
        ctk.CTkLabel(
            content_container, 
            text="Welcome to Film Booking", 
            font=("Arial", 32, "bold"), 
            text_color="white"
        ).pack(anchor="w", pady=(0, 10))

        # Subtitle
        ctk.CTkLabel(
            content_container, 
            text="Browse and book your favorite movies", 
            font=("Arial", 16), 
            text_color="#cccccc"
        ).pack(anchor="w", pady=(0, 30))

        # Search bar for movies
        self.create_search_bar(content_container)

        # Now Showing Section
        self.create_now_showing(content_container)

        # Featured Theaters Section
        self.create_featured_theaters(content_container)

    def create_search_bar(self, parent):
        # Search bar container
        search_frame = ctk.CTkFrame(parent, fg_color="black", height=50)
        search_frame.pack(fill="x", pady=(0, 30))
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search for movies...",
            font=("Arial", 14),
            height=40,
            width=300,
            fg_color="#333333",
            text_color="white",
            border_width=0
        )
        self.search_entry.pack(side="left")
        
        # Search button
        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            font=("Arial", 14),
            height=40,
            fg_color="#d92525",
            hover_color="#b71c1c",
            command=self.search_movies
        )
        search_btn.pack(side="left", padx=(10, 0))
        
        # Bind Enter key to search
        self.search_entry.bind("<Return>", lambda e: self.search_movies())

    def search_movies(self):
        """Search for movies in database"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            return
            
        try:
            # Open a search results window
            self.open_search_results(search_term)
        except Exception as e:
            messagebox.showerror("Search Error", f"Error searching for movies: {e}")

    def open_search_results(self, search_term):
        """Open a window with search results"""
        # Get search results from database
        results = self.get_movies_by_search(search_term)
        
        # Create search results window
        results_window = ctk.CTkToplevel(self.root)
        results_window.title(f"Search Results for '{search_term}'")
        results_window.geometry("600x500")
        results_window.grab_set()  # Make window modal
        
        # Create scrollable frame
        results_frame = ctk.CTkScrollableFrame(results_window, fg_color="#222222")
        results_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add results
        if results:
            for movie in results:
                self.create_movie_result_item(results_frame, movie)
        else:
            ctk.CTkLabel(
                results_frame,
                text="No movies found matching your search term.",
                font=("Arial", 14),
                text_color="white"
            ).pack(pady=20)

    def create_movie_result_item(self, parent, movie):
        """Create a movie item for search results"""
        item_frame = ctk.CTkFrame(parent, fg_color="#333333", corner_radius=10, height=80)
        item_frame.pack(fill="x", pady=5, padx=5)
        item_frame.pack_propagate(False)
        
        # Movie title
        title_label = ctk.CTkLabel(
            item_frame,
            text=movie['movieTitle'],
            font=("Arial", 16, "bold"),
            text_color="white"
        )
        title_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Movie details
        details = f"Genre: {movie['movieGenre']} | Duration: {movie['movieDuration']} | Rating: {movie['movieRating']}"
        details_label = ctk.CTkLabel(
            item_frame,
            text=details,
            font=("Arial", 12),
            text_color="#aaaaaa"
        )
        details_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Make the item clickable
        def on_click(e):
            self.show_movie_details(movie['movieID'], movie['movieTitle'])
            
        for widget in [item_frame, title_label, details_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", lambda e: item_frame.configure(fg_color="#444444"))
            widget.bind("<Leave>", lambda e: item_frame.configure(fg_color="#333333"))

    def create_now_showing(self, parent):
        # Now Showing Title
        ctk.CTkLabel(
            parent, 
            text="Now Showing", 
            font=("Arial", 24, "bold"), 
            text_color="white"
        ).pack(anchor="w", pady=(0, 20))

        # Get movies from database
        movies = self.get_now_showing_movies()

        # Container to hold movie posters
        movies_container = ctk.CTkScrollableFrame(parent, fg_color="black", orientation="horizontal", height=350)
        movies_container.pack(fill="x", pady=(0, 50))

        # Create movie posters
        if movies:
            for i, movie in enumerate(movies):
                self.create_movie_poster(movies_container, movie, i)
        else:
            # Display message if no movies found
            ctk.CTkLabel(
                movies_container,
                text="No movies currently showing. Check back later!",
                font=("Arial", 16),
                text_color="white"
            ).pack(pady=30)

    def create_movie_poster(self, parent, movie, index):
        """Create a movie poster card"""
        # Define colors for genre-based backgrounds (for when no image is available)
        genre_colors = {
            "Action": "#e63946",
            "Drama": "#457b9d",
            "Comedy": "#f4a261",
            "Sci-Fi": "#2a9d8f",
            "Crime": "#6a5acd",
            "Adventure": "#e76f51",
            "Romance": "#ff758f",
            "Horror": "#343a40",
            "Fantasy": "#4cc9f0",
            "Thriller": "#5e548e"
        }

        # Get genre for determining color
        genre = movie['movieGenre']
        # Choose a color based on genre, or default to dark gray
        bg_color = genre_colors.get(genre, "#333333")
        
        # Movie frame
        movie_frame = ctk.CTkFrame(parent, fg_color="black", corner_radius=10, width=200)
        movie_frame.grid(row=0, column=index, padx=15, pady=10, sticky="nw")

        # Try to load movie poster image
        image_path = f"images/{movie['movieID']}.jpg"
        poster_image = None
        
        try:
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img = img.resize((180, 250), Image.LANCZOS)
                poster_image = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image for {movie['movieTitle']}: {e}")
            poster_image = None

        # Create poster container - either image or colored placeholder
        if poster_image:
            poster = ctk.CTkLabel(movie_frame, image=poster_image, text="")
            poster.image = poster_image  # Keep a reference
            poster.pack(padx=0, pady=0)
        else:
            # Create a colored placeholder with movie title
            poster_placeholder = ctk.CTkFrame(
                movie_frame, 
                width=180, 
                height=250, 
                fg_color=bg_color,
                corner_radius=10
            )
            poster_placeholder.pack(padx=0, pady=0)
            poster_placeholder.pack_propagate(False)
            
            # Movie title in center of placeholder
            ctk.CTkLabel(
                poster_placeholder,
                text=movie['movieTitle'],
                font=("Arial", 16, "bold"),
                text_color="white",
                wraplength=160
            ).place(relx=0.5, rely=0.5, anchor="center")
            
            # Genre badge at bottom
            genre_badge = ctk.CTkFrame(
                poster_placeholder,
                fg_color="#333333",
                corner_radius=5,
                height=30
            )
            genre_badge.place(relx=0.5, rely=0.9, anchor="center")
            genre_badge.pack_propagate(False)
            
            ctk.CTkLabel(
                genre_badge,
                text=genre,
                font=("Arial", 12),
                text_color="white"
            ).pack(padx=10, pady=3)
            
            # Reference to use for click events
            poster = poster_placeholder
        
        # Movie title label
        title_label = ctk.CTkLabel(
            movie_frame,
            text=movie['movieTitle'],
            font=("Arial", 14, "bold"),
            text_color="white",
            wraplength=170
        )
        title_label.pack(pady=(5, 0))
        
        # Rating label
        rating_frame = ctk.CTkFrame(movie_frame, fg_color="#FFD700", corner_radius=5)  # Gold color without transparency
        rating_frame.pack(pady=(5, 0))
        
        ctk.CTkLabel(
            rating_frame,
            text=f"★ {movie['movieRating']}/10",
            font=("Arial", 12, "bold"),
            text_color="black"
        ).pack(padx=5, pady=2)
        
        # Book button
        book_btn = ctk.CTkButton(
            movie_frame,
            text="Book",
            font=("Arial", 12),
            fg_color="#d92525",
            hover_color="#b71c1c",
            height=30,
            width=80,
            command=lambda m_id=movie['movieID'], m_title=movie['movieTitle']: self.show_movie_details(m_id, m_title)
        )
        book_btn.pack(pady=10)
        
        # Movie selection - make entire poster clickable
        def on_movie_select(e):
            self.show_movie_details(movie['movieID'], movie['movieTitle'])
        
        poster.bind("<Button-1>", on_movie_select)
        title_label.bind("<Button-1>", on_movie_select)
        
        return movie_frame

    def create_featured_theaters(self, parent):
        # Featured Theaters Title
        ctk.CTkLabel(
            parent, 
            text="Featured Theaters", 
            font=("Arial", 24, "bold"), 
            text_color="white"
        ).pack(anchor="w", pady=(0, 20))

        # Get theaters from database
        theaters = self.get_featured_theaters()

        # Theater container
        theater_container = ctk.CTkFrame(parent, fg_color="black")
        theater_container.pack(fill="x")

        # Create theater items
        if theaters:
            for i, theater in enumerate(theaters):
                self.create_theater_item(
                    theater_container, 
                    theater['theaterName'], 
                    theater['theaterLocation'],
                    theater['theaterID'],
                    i
                )
        else:
            # Display message if no theaters found
            ctk.CTkLabel(
                theater_container,
                text="No theaters available at the moment.",
                font=("Arial", 16),
                text_color="white"
            ).pack(pady=30)

    def create_theater_item(self, parent, name, location, theater_id, index):
        # Theater item frame
        frame = ctk.CTkFrame(parent, fg_color="black")
        frame.grid(row=0, column=index, padx=30)
        
        # Circular background for icon
        circle = ctk.CTkFrame(frame, width=100, height=100, corner_radius=50, fg_color="#333333")
        circle.pack(pady=(0, 10))
        circle.pack_propagate(False)
        
        # Film icon
        icon = ctk.CTkLabel(circle, text="🎬", font=("Arial", 40), text_color="white")
        icon.place(relx=0.5, rely=0.5, anchor="center")
        
        # Theater name
        name_label = ctk.CTkLabel(frame, text=name, font=("Arial", 18, "bold"), text_color="white")
        name_label.pack()
        
        # Location
        location_label = ctk.CTkLabel(frame, text=f"Location: {location}", font=("Arial", 14), text_color="#cccccc")
        location_label.pack()
        
        # View shows button
        view_btn = ctk.CTkButton(
            frame,
            text="View Shows",
            font=("Arial", 12),
            fg_color="#d92525",
            hover_color="#b71c1c",
            height=30,
            width=100,
            command=lambda tid=theater_id, tname=name: self.show_theater_details(tid, tname)
        )
        view_btn.pack(pady=10)
        
        # Theater selection - make items clickable
        def on_theater_select(e):
            self.show_theater_details(theater_id, name)
        
        for widget in [circle, icon, name_label, location_label]:
            widget.bind("<Button-1>", on_theater_select)
        
        return frame

    def navigate_to(self, screen_name):
        """Handle navigation between different screens"""
        # Close current window
        self.root.withdraw()
        
        try:
            if screen_name == "Previous Bookings":
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
            elif screen_name == "Home":
                # Refresh the home page
                self.root.destroy()
                subprocess.Popen([sys.executable, "home.py"])
        except Exception as e:
            print(f"Navigation error: {e}")
            # Reopen current window if navigation fails
            self.root.deiconify()

    def show_movie_details(self, movie_id, movie_title):
        """Show details for a selected movie"""
        # First save the movie_id to a temporary file to pass it to book.py
        try:
            with open("selected_movie.txt", "w") as file:
                file.write(f"movie_id={movie_id}\n")
                file.write(f"movie_title={movie_title}\n")
                
            # Open the movie details/booking page
            subprocess.Popen([sys.executable, "book.py"])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open movie details: {e}")

    def show_theater_details(self, theater_id, theater_name):
        """Show details for a selected theater"""
        # Save theater ID to temporary file
        try:
            with open("selected_theater.txt", "w") as file:
                file.write(f"theater_id={theater_id}\n")
                file.write(f"theater_name={theater_name}\n")
                
            # Create popup window with shows for this theater
            self.show_theater_shows(theater_id, theater_name)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to show theater details: {e}")

    def show_theater_shows(self, theater_id, theater_name):
        """Show a popup with all shows for a theater"""
        # Get shows from database
        shows = self.get_shows_by_theater(theater_id)
        
        # Create popup window
        shows_window = ctk.CTkToplevel(self.root)
        shows_window.title(f"Shows at {theater_name}")
        shows_window.geometry("800x600")
        shows_window.grab_set()  # Make window modal
        
        # Title
        ctk.CTkLabel(
            shows_window,
            text=f"Upcoming Shows at {theater_name}",
            font=("Arial", 24, "bold"),
            text_color="white"
        ).pack(pady=(20, 30), padx=20)
        
        # Create scrollable frame for shows
        shows_frame = ctk.CTkScrollableFrame(shows_window, fg_color="#222222")
        shows_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Add shows
        if shows:
            for show in shows:
                # Get movie details
                movie = self.get_movie_by_id(show['movieID'])
                
                if movie:
                    self.create_show_item(shows_frame, show, movie, theater_name)
        else:
            ctk.CTkLabel(
                shows_frame,
                text="No upcoming shows scheduled for this theater.",
                font=("Arial", 16),
                text_color="white"
            ).pack(pady=30)

    def create_show_item(self, parent, show, movie, theater_name):
        """Create a show item for the theater details popup"""
        # Show item frame
        item_frame = ctk.CTkFrame(parent, fg_color="#333333", corner_radius=10, height=120)
        item_frame.pack(fill="x", pady=10, padx=10)
        
        # Left side - movie info
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        
        # Movie title
        ctk.CTkLabel(
            info_frame,
            text=movie['movieTitle'],
            font=("Arial", 18, "bold"),
            text_color="white"
        ).pack(anchor="w")
        
        # Movie details
        details = f"Genre: {movie['movieGenre']} | Duration: {movie['movieDuration']} mins | Rating: {movie['movieRating']}/10"
        ctk.CTkLabel(
            info_frame,
            text=details,
            font=("Arial", 12),
            text_color="#aaaaaa"
        ).pack(anchor="w", pady=(5, 0))
        
        # Show date and time
        show_time = f"Date: {show['showDate']} | Time: {show['showTime']}"
        ctk.CTkLabel(
            info_frame,
            text=show_time,
            font=("Arial", 14),
            text_color="white"
        ).pack(anchor="w", pady=(10, 0))
        
        # Right side - booking button
        book_btn = ctk.CTkButton(
            item_frame,
            text="Book Tickets",
            font=("Arial", 14, "bold"),
            fg_color="#d92525",
            text_color="white",
            hover_color="#b71c1c",
            corner_radius=5,
            height=40,
            width=120,
            command=lambda: self.book_show(show['showID'], movie['movieTitle'], theater_name)
        )
        book_btn.pack(side="right", padx=15)

    def book_show(self, show_id, movie_title, theater_name):
        """Handle booking for a specific show"""
        try:
            # Save show ID to file for seat selection page
            with open("selected_show.txt", "w") as file:
                file.write(f"show_id={show_id}\n")
                file.write(f"movie_title={movie_title}\n")
                file.write(f"theater_name={theater_name}\n")
                
            # Open seat selection page
            subprocess.Popen([sys.executable, "seat.py"])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to proceed to seat selection: {e}")

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

    # Database methods
    def get_now_showing_movies(self):
        """Get currently showing movies from database"""
        try:
            connection = mysql.connector.connect(**self.DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            # Get movies with upcoming shows
            query = """
            SELECT DISTINCT m.* FROM Movies m
            JOIN `Show` s ON m.movieID = s.movieID
            WHERE s.showDate >= CURDATE()
            ORDER BY s.showDate
            LIMIT 8
            """
            
            cursor.execute(query)
            movies = cursor.fetchall()
            
            if not movies:
                # If no movies found, get all movies as fallback
                cursor.execute("SELECT * FROM Movies LIMIT 8")
                movies = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return movies
        except Exception as e:
            print(f"Database error getting movies: {e}")
            # Return placeholder data in case of database error
            return self.get_placeholder_movies()

    def get_placeholder_movies(self):
        """Return placeholder movie data in case of database error"""
        return [
            {
                'movieID': 1,
                'movieTitle': 'The Shawshank Redemption',
                'movieGenre': 'Drama',
                'movieDuration': 142,
                'movieRating': 9.3
            },
            {
                'movieID': 2,
                'movieTitle': 'The Godfather',
                'movieGenre': 'Crime',
                'movieDuration': 175,
                'movieRating': 9.2
            },
            {
                'movieID': 3,
                'movieTitle': 'The Dark Knight',
                'movieGenre': 'Action',
                'movieDuration': 152,
                'movieRating': 9.0
            },
            {
                'movieID': 4,
                'movieTitle': 'Pulp Fiction',
                'movieGenre': 'Crime',
                'movieDuration': 154,
                'movieRating': 8.9
            }
        ]

    def get_featured_theaters(self):
        """Get featured theaters from database"""
        try:
            connection = mysql.connector.connect(**self.DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            # Get theaters with upcoming shows
            query = """
            SELECT DISTINCT t.* FROM Theaters t
            JOIN `Show` s ON t.theaterID = s.theaterID
            WHERE s.showDate >= CURDATE()
            LIMIT 4
            """
            
            cursor.execute(query)
            theaters = cursor.fetchall()
            
            if not theaters:
                # If no theaters found, get all theaters
                cursor.execute("SELECT * FROM Theaters LIMIT 4")
                theaters = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return theaters
        except Exception as e:
            print(f"Database error getting theaters: {e}")
            # Return placeholder data in case of database error
            return self.get_placeholder_theaters()

    def get_placeholder_theaters(self):
        """Return placeholder theater data in case of database error"""
        return [
            {
                'theaterID': 1,
                'theaterName': 'PVR Cinemas',
                'theaterLocation': 'City Center Mall, Main Street'
            },
            {
                'theaterID': 2,
                'theaterName': 'INOX Movies',
                'theaterLocation': 'Downtown Shopping Complex'
            },
            {
                'theaterID': 3,
                'theaterName': 'Cinepolis',
                'theaterLocation': 'West End Mall, Park Avenue'
            }
        ]

    def get_movies_by_search(self, search_term):
        """Search for movies in database"""
        try:
            connection = mysql.connector.connect(**self.DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            # Search by title or genre
            query = """
            SELECT * FROM Movies 
            WHERE movieTitle LIKE %s OR movieGenre LIKE %s
            """
            
            search_param = f"%{search_term}%"
            cursor.execute(query, (search_param, search_param))
            movies = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return movies
        except Exception as e:
            print(f"Database error searching movies: {e}")
            return []

    def get_shows_by_theater(self, theater_id):
        """Get shows for a specific theater"""
        try:
            connection = mysql.connector.connect(**self.DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            # Get upcoming shows for this theater
            query = """
            SELECT * FROM `Show` 
            WHERE theaterID = %s AND showDate >= CURDATE()
            ORDER BY showDate, showTime
            """
            
            cursor.execute(query, (theater_id,))
            shows = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return shows
        except Exception as e:
            print(f"Database error getting shows: {e}")
            # Generate placeholder shows
            return self.get_placeholder_shows(theater_id)

    def get_placeholder_shows(self, theater_id):
        """Generate placeholder show data"""
        # Get today's date
        today = datetime.now()
        
        # Generate 3 days of placeholder shows
        shows = []
        for day in range(3):
            show_date = (today + timedelta(days=day)).strftime("%Y-%m-%d")
            # Add 3 show times per day
            for time in ["14:30", "18:00", "21:15"]:
                shows.append({
                    'showID': random.randint(1, 1000),
                    'movieID': random.randint(1, 4),  # Random movie ID
                    'theaterID': theater_id,
                    'showDate': show_date,
                    'showTime': time
                })
        
        return shows

    def get_movie_by_id(self, movie_id):
        """Get movie details by ID"""
        try:
            connection = mysql.connector.connect(**self.DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM Movies WHERE movieID = %s"
            cursor.execute(query, (movie_id,))
            movie = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return movie
        except Exception as e:
            print(f"Database error getting movie details: {e}")
            # Try to find movie in placeholder data
            for movie in self.get_placeholder_movies():
                if movie['movieID'] == movie_id:
                    return movie
            return None

    def run(self):
        """Run the home page application"""
        # Ensure images directory exists
        if not os.path.exists("images"):
            os.makedirs("images")
            print("Created 'images' directory. Please add movie poster images.")
            
        # Attempt to create default movie posters if they don't exist
        self.create_default_movie_posters()
        
        self.root.mainloop()
        
    def create_default_movie_posters(self):
        """Create default movie posters if they don't exist"""
        try:
            # Define colors for genre-based backgrounds
            genre_colors = {
                "Action": (230, 57, 70),     # Red
                "Drama": (69, 123, 157),     # Blue
                "Comedy": (244, 162, 97),    # Orange
                "Sci-Fi": (42, 157, 143),    # Teal
                "Crime": (106, 90, 205),     # Purple
                "Adventure": (231, 111, 81), # Coral
                "Romance": (255, 117, 143),  # Pink
                "Horror": (52, 58, 64),      # Dark Gray
                "Fantasy": (76, 201, 240),   # Light Blue
                "Thriller": (94, 84, 142)    # Dark Purple
            }
            
            # Get movies from database
            try:
                connection = mysql.connector.connect(**self.DB_CONFIG)
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM Movies")
                movies = cursor.fetchall()
                cursor.close()
                connection.close()
            except Exception as e:
                print(f"Error fetching movies for posters: {e}")
                movies = self.get_placeholder_movies()
            
            # Create a simple colored image for each movie if poster doesn't exist
            for movie in movies:
                image_path = f"images/{movie['movieID']}.jpg"
                
                # Skip if poster already exists
                if os.path.exists(image_path):
                    continue
                
                # Get color based on genre, or default to gray
                genre = movie.get('movieGenre', 'Drama')
                color = genre_colors.get(genre, (51, 51, 51))  # Default dark gray
                
                # Create a new image with the genre color
                width, height = 180, 250
                img = Image.new('RGB', (width, height), color)
                
                # Save the image
                img.save(image_path)
                print(f"Created default poster for {movie['movieTitle']}")
        
        except Exception as e:
            print(f"Error creating default movie posters: {e}")

# Run the application
if __name__ == "__main__":
    home_page = HomePage()
    home_page.run()