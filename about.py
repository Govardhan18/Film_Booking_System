import customtkinter as ctk
from PIL import Image, ImageTk
import subprocess
import sys
import os
from tkinter import messagebox
import webbrowser

class AboutPage:
    def __init__(self):
        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("Film Booking - About")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)

        # Set appearance mode
        ctk.set_appearance_mode("dark")
        
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
            "Home": self.create_sidebar_button("🏠", "Home"),
            "Bookings": self.create_sidebar_button("📅", "Previous Bookings"),
            "Profile": self.create_sidebar_button("👤", "Profile"),
            "About": self.create_sidebar_button("ℹ️", "About", is_active=True)
        }
        
        # Add admin button if user has admin role
        if self.user_role == "admin":
            self.buttons["Admin"] = self.create_sidebar_button("⚙️", "Admin Dashboard")

        # Conditionally show logout button if user is logged in, otherwise show login button
        if self.user_id:
            self.create_logout_button()
        else:
            self.create_login_button()

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

    def create_login_button(self):
        login_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=40)
        login_frame.pack(side="bottom", fill="x", pady=(0, 30))
        login_frame.pack_propagate(False)

        login_icon = ctk.CTkLabel(login_frame, text="📥", 
                                font=("Arial", 16), 
                                text_color="white", 
                                width=30)
        login_icon.pack(side="left", padx=(20, 10))

        login_text = ctk.CTkLabel(login_frame, text="Login", 
                                font=("Arial", 16), 
                                text_color="white", 
                                anchor="w")
        login_text.pack(side="left")

        # Hover and click effects
        def on_enter(e):
            login_frame.configure(fg_color="#b71c1c")
        def on_leave(e):
            login_frame.configure(fg_color="transparent")
        def on_login(e):
            self.open_login()

        for widget in [login_frame, login_icon, login_text]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_login)

    def create_main_content(self):
        # Main Content Frame
        main_content = ctk.CTkFrame(self.root, fg_color="black", corner_radius=0)
        main_content.pack(side="right", fill="both", expand=True)

        # Content container with padding
        content_container = ctk.CTkFrame(main_content, fg_color="black")
        content_container.pack(fill="both", expand=True, padx=40, pady=40)

        # Main Title
        title_label = ctk.CTkLabel(
            content_container,
            text="About Film Booking System",
            font=("Arial", 32, "bold"),
            text_color="white"
        )
        title_label.pack(anchor="w", pady=(0, 20))

        # App description
        description_frame = ctk.CTkFrame(content_container, fg_color="#222222", corner_radius=10)
        description_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            description_frame,
            text="Film Booking System - Your Premier Movie Booking Platform",
            font=("Arial", 18, "bold"),
            text_color="white"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        description_text = """Film Booking System is a comprehensive application designed to streamline the movie booking experience. 
With our platform, users can browse movies, view showtimes, select seats, and manage their bookings all in one place.

This system provides a user-friendly interface for moviegoers and a powerful management tool for theater administrators.
Whether you're booking tickets for the latest blockbuster or managing theater operations, our system has you covered."""

        ctk.CTkLabel(
            description_frame,
            text=description_text,
            font=("Arial", 14),
            text_color="#cccccc",
            wraplength=800,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 20))

        # Create scrollable frame for all other content
        scroll_frame = ctk.CTkScrollableFrame(content_container, fg_color="transparent", height=400)
        scroll_frame.pack(fill="x", expand=True)

        # Features section
        self.create_features_section(scroll_frame)
        
        # Technologies section
        self.create_technologies_section(scroll_frame)
        
        # Developer section
        self.create_developer_section(scroll_frame)
        
        # Version info
        version_label = ctk.CTkLabel(
            content_container,
            text="Version 1.0 - Released April 2025",
            font=("Arial", 12),
            text_color="#888888"
        )
        version_label.pack(side="bottom", anchor="e")

    def create_features_section(self, parent):
        features_frame = ctk.CTkFrame(parent, fg_color="#222222", corner_radius=10)
        features_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            features_frame,
            text="Key Features",
            font=("Arial", 18, "bold"),
            text_color="white"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Feature cards container
        feature_cards = ctk.CTkFrame(features_frame, fg_color="transparent")
        feature_cards.pack(fill="x", padx=20, pady=(0, 20))
        
        # Create feature cards
        features = [
            {
                "icon": "🎬",
                "title": "Movie Browsing",
                "description": "Browse the latest movies with details including genre, duration, and ratings."
            },
            {
                "icon": "🎟️",
                "title": "Ticket Booking",
                "description": "Select your preferred showtime and seats with an interactive seat selection interface."
            },
            {
                "icon": "👤",
                "title": "User Profiles",
                "description": "Manage your personal information and view your booking history."
            },
            {
                "icon": "⚙️",
                "title": "Admin Dashboard",
                "description": "Comprehensive management tools for administrators to manage movies, shows, and users."
            }
        ]
        
        for i, feature in enumerate(features):
            # Create card
            card = ctk.CTkFrame(feature_cards, fg_color="#333333", corner_radius=10)
            if i % 2 == 0:
                card.grid(row=i//2, column=0, padx=(0, 10), pady=10, sticky="nsew")
            else:
                card.grid(row=i//2, column=1, padx=(10, 0), pady=10, sticky="nsew")
            
            # Card content
            # Icon
            ctk.CTkLabel(
                card,
                text=feature["icon"],
                font=("Arial", 30),
                text_color="white"
            ).pack(anchor="w", padx=20, pady=(20, 10))
            
            # Title
            ctk.CTkLabel(
                card,
                text=feature["title"],
                font=("Arial", 16, "bold"),
                text_color="white"
            ).pack(anchor="w", padx=20, pady=(0, 10))
            
            # Description
            ctk.CTkLabel(
                card,
                text=feature["description"],
                font=("Arial", 14),
                text_color="#cccccc",
                wraplength=350,
                justify="left"
            ).pack(anchor="w", padx=20, pady=(0, 20))
        
        # Configure grid columns to expand
        feature_cards.grid_columnconfigure(0, weight=1)
        feature_cards.grid_columnconfigure(1, weight=1)

    def create_technologies_section(self, parent):
        tech_frame = ctk.CTkFrame(parent, fg_color="#222222", corner_radius=10)
        tech_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            tech_frame,
            text="Technologies Used",
            font=("Arial", 18, "bold"),
            text_color="white"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Technologies list
        technologies = [
            {"name": "Python", "description": "Core programming language"},
            {"name": "CustomTkinter", "description": "Modern UI framework for desktop applications"},
            {"name": "MySQL", "description": "Database management system"},
            {"name": "PIL (Pillow)", "description": "Image processing library"},
            {"name": "Matplotlib", "description": "Data visualization library for analytics"}
        ]
        
        for tech in technologies:
            tech_item = ctk.CTkFrame(tech_frame, fg_color="transparent")
            tech_item.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(
                tech_item,
                text=tech["name"],
                font=("Arial", 16, "bold"),
                text_color="white",
                width=150
            ).pack(side="left")
            
            ctk.CTkLabel(
                tech_item,
                text=tech["description"],
                font=("Arial", 14),
                text_color="#cccccc"
            ).pack(side="left")
        
        # Add some padding at the bottom
        ctk.CTkFrame(tech_frame, height=10, fg_color="transparent").pack()

    def create_developer_section(self, parent):
        dev_frame = ctk.CTkFrame(parent, fg_color="#222222", corner_radius=10)
        dev_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            dev_frame,
            text="Contact & Support",
            font=("Arial", 18, "bold"),
            text_color="white"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Contact information
        contact_frame = ctk.CTkFrame(dev_frame, fg_color="transparent")
        contact_frame.pack(fill="x", padx=20, pady=10)
        
        # Email
        email_frame = ctk.CTkFrame(contact_frame, fg_color="transparent")
        email_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            email_frame,
            text="Email:",
            font=("Arial", 14, "bold"),
            text_color="white",
            width=100
        ).pack(side="left")
        
        email_link = ctk.CTkLabel(
            email_frame,
            text="support@filmbooking.com",
            font=("Arial", 14),
            text_color="#4a90e2",
            cursor="hand2"
        )
        email_link.pack(side="left")
        email_link.bind("<Button-1>", lambda e: self.open_email("support@filmbooking.com"))
        
        # Website
        website_frame = ctk.CTkFrame(contact_frame, fg_color="transparent")
        website_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            website_frame,
            text="Website:",
            font=("Arial", 14, "bold"),
            text_color="white",
            width=100
        ).pack(side="left")
        
        website_link = ctk.CTkLabel(
            website_frame,
            text="www.filmbooking.com",
            font=("Arial", 14),
            text_color="#4a90e2",
            cursor="hand2"
        )
        website_link.pack(side="left")
        website_link.bind("<Button-1>", lambda e: self.open_website("https://www.filmbooking.com"))
        
        # Support hours
        ctk.CTkLabel(
            contact_frame,
            text="Support Hours: Monday to Friday, 9 AM - 6 PM",
            font=("Arial", 14),
            text_color="#cccccc"
        ).pack(anchor="w", pady=(10, 0))
        
        # Developer information
        ctk.CTkLabel(
            dev_frame,
            text="Developed by: Your Name",
            font=("Arial", 14),
            text_color="#cccccc"
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        ctk.CTkLabel(
            dev_frame,
            text="© 2025 Film Booking System. All rights reserved.",
            font=("Arial", 12),
            text_color="#888888"
        ).pack(anchor="w", padx=20, pady=(0, 20))

    def open_email(self, email):
        """Open default email client with the given email address"""
        try:
            webbrowser.open(f"mailto:{email}")
        except Exception as e:
            print(f"Error opening email: {e}")

    def open_website(self, url):
        """Open website in default browser"""
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening website: {e}")

    def navigate_to(self, screen_name):
        """Handle navigation between different screens"""
        # Skip if user not logged in and trying to access restricted areas
        if not self.user_id and screen_name not in ["About", "Home"]:
            messagebox.showinfo("Login Required", "Please log in to access this feature.")
            return
            
        # Close current window
        self.root.withdraw()
        
        try:
            if screen_name == "Home":
                # Open Home page
                if self.user_id:
                    subprocess.Popen([sys.executable, "home.py"])
                else:
                    subprocess.Popen([sys.executable, "main.py"])
                self.root.destroy()
            elif screen_name == "Previous Bookings":
                # Open Bookings page
                subprocess.Popen([sys.executable, "prevbook.py"])
                self.root.destroy()
            elif screen_name == "Profile":
                # Open Profile page
                subprocess.Popen([sys.executable, "profile.py"])
                self.root.destroy()
            elif screen_name == "About":
                # Refresh current page
                self.root.deiconify()
            elif screen_name == "Admin Dashboard" and self.user_role == "admin":
                # Open Admin page
                subprocess.Popen([sys.executable, "admin.py"])
                self.root.destroy()
        except Exception as e:
            print(f"Navigation error: {e}")
            # Reopen current window if navigation fails
            self.root.deiconify()

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

    def open_login(self):
        """Open login page"""
        try:
            # Close current window
            self.root.destroy()
            
            # Open login page
            subprocess.Popen([sys.executable, "login.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open login page: {e}")

    def run(self):
        """Run the about page application"""
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    about_page = AboutPage()
    about_page.run()