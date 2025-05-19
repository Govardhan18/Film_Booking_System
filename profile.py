import customtkinter as ctk
from PIL import Image, ImageTk
import mysql.connector
import hashlib
import sys
import subprocess
import os
import re
from tkinter import messagebox

class ProfilePage:
    def __init__(self):
        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("Film Booking - User Profile")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)

        # Set appearance mode
        ctk.set_appearance_mode("dark")
        
        # Database configuration
        self.DB_CONFIG = {
            'host': 'localhost',
            'user': 'root',
            'password': 'new_password',  # Replace with your actual MySQL password
            'database': 'film_booking'
        }

        # Load user session
        self.user_id = None
        self.user_name = None
        self.user_role = None
        self.user_data = None
        self.load_user_session()
        
        # Get user data from database
        if self.user_id:
            self.user_data = self.get_user_data()
            
            if not self.user_data:
                messagebox.showerror("Error", "Could not retrieve user data. Returning to login.")
                self.logout()
                return
        else:
            messagebox.showerror("Error", "No user logged in. Returning to login.")
            self.logout()
            return

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

    def get_user_data(self):
        """Get user data from database"""
        try:
            connection = mysql.connector.connect(**self.DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM Users WHERE userID = %s"
            cursor.execute(query, (self.user_id,))
            user_data = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return user_data
        except Exception as e:
            print(f"Database error: {e}")
            return None

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
            "Profile": self.create_sidebar_button("👤", "Profile", is_active=True),
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

        # Main Title
        title_label = ctk.CTkLabel(
            content_container,
            text="Your Profile",
            font=("Arial", 32, "bold"),
            text_color="white"
        )
        title_label.pack(anchor="w", pady=(0, 30))

        # Create two columns
        columns_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True)
        
        # Left column - Profile picture and basic info
        left_column = ctk.CTkFrame(columns_frame, fg_color="transparent", width=300)
        left_column.pack(side="left", fill="y", padx=(0, 20))
        left_column.pack_propagate(False)
        
        # Profile picture frame
        profile_pic_frame = ctk.CTkFrame(left_column, fg_color="#333333", width=200, height=200, corner_radius=100)
        profile_pic_frame.pack(pady=(0, 20))
        profile_pic_frame.pack_propagate(False)
        
        # Profile picture or initials
        if self.user_data:
            initials = self.user_data['first_name'][0] + self.user_data['last_name'][0]
            ctk.CTkLabel(
                profile_pic_frame,
                text=initials,
                font=("Arial", 64, "bold"),
                text_color="white"
            ).place(relx=0.5, rely=0.5, anchor="center")
        
        # User role badge
        role_badge = ctk.CTkFrame(left_column, fg_color="#d92525" if self.user_role == "admin" else "#333333", corner_radius=15, height=30)
        role_badge.pack(pady=(0, 20))
        role_badge.pack_propagate(False)
        
        ctk.CTkLabel(
            role_badge,
            text=f"{self.user_role.capitalize()} Account",
            font=("Arial", 12, "bold"),
            text_color="white"
        ).pack(padx=20, pady=5)
        
        # Member since info
        if self.user_data and 'created_at' in self.user_data:
            # Format the date string
            try:
                from datetime import datetime
                date_obj = datetime.strptime(str(self.user_data['created_at']), "%Y-%m-%d %H:%M:%S")
                formatted_date = date_obj.strftime("%B %d, %Y")
                
                ctk.CTkLabel(
                    left_column,
                    text=f"Member since",
                    font=("Arial", 12),
                    text_color="#aaaaaa"
                ).pack()
                
                ctk.CTkLabel(
                    left_column,
                    text=formatted_date,
                    font=("Arial", 14, "bold"),
                    text_color="white"
                ).pack()
            except Exception as e:
                print(f"Error formatting date: {e}")
        
        # Right column - Edit profile form
        right_column = ctk.CTkFrame(columns_frame, fg_color="#222222", corner_radius=10)
        right_column.pack(side="right", fill="both", expand=True)
        
        # Profile form
        self.create_profile_form(right_column)

    def create_profile_form(self, parent):
        # Form container with padding
        form_container = ctk.CTkFrame(parent, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Form title
        ctk.CTkLabel(
            form_container,
            text="Edit Profile Information",
            font=("Arial", 20, "bold"),
            text_color="white"
        ).pack(anchor="w", pady=(0, 20))
        
        # Create form fields
        # First Name
        ctk.CTkLabel(
            form_container,
            text="First Name",
            font=("Arial", 14),
            text_color="white"
        ).pack(anchor="w", pady=(10, 5))
        
        self.first_name_entry = ctk.CTkEntry(
            form_container,
            height=40,
            fg_color="#333333",
            text_color="white",
            border_width=0
        )
        self.first_name_entry.pack(fill="x", pady=(0, 10))
        if self.user_data:
            self.first_name_entry.insert(0, self.user_data['first_name'])
        
        # Last Name
        ctk.CTkLabel(
            form_container,
            text="Last Name",
            font=("Arial", 14),
            text_color="white"
        ).pack(anchor="w", pady=(10, 5))
        
        self.last_name_entry = ctk.CTkEntry(
            form_container,
            height=40,
            fg_color="#333333",
            text_color="white",
            border_width=0
        )
        self.last_name_entry.pack(fill="x", pady=(0, 10))
        if self.user_data:
            self.last_name_entry.insert(0, self.user_data['last_name'])
        
        # Email
        ctk.CTkLabel(
            form_container,
            text="Email",
            font=("Arial", 14),
            text_color="white"
        ).pack(anchor="w", pady=(10, 5))
        
        self.email_entry = ctk.CTkEntry(
            form_container,
            height=40,
            fg_color="#333333",
            text_color="white",
            border_width=0
        )
        self.email_entry.pack(fill="x", pady=(0, 10))
        if self.user_data:
            self.email_entry.insert(0, self.user_data['email'])
        
        # Change Password section
        password_frame = ctk.CTkFrame(form_container, fg_color="#333333", corner_radius=10)
        password_frame.pack(fill="x", pady=20)
        
        # Password section title
        ctk.CTkLabel(
            password_frame,
            text="Change Password",
            font=("Arial", 16, "bold"),
            text_color="white"
        ).pack(anchor="w", padx=20, pady=10)
        
        # Current Password
        password_inner_frame = ctk.CTkFrame(password_frame, fg_color="transparent")
        password_inner_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            password_inner_frame,
            text="Current Password",
            font=("Arial", 14),
            text_color="white"
        ).pack(anchor="w", pady=(10, 5))
        
        self.current_password_entry = ctk.CTkEntry(
            password_inner_frame,
            height=40,
            fg_color="#222222",
            text_color="white",
            border_width=0,
            show="*"
        )
        self.current_password_entry.pack(fill="x", pady=(0, 10))
        
        # New Password
        ctk.CTkLabel(
            password_inner_frame,
            text="New Password",
            font=("Arial", 14),
            text_color="white"
        ).pack(anchor="w", pady=(10, 5))
        
        self.new_password_entry = ctk.CTkEntry(
            password_inner_frame,
            height=40,
            fg_color="#222222",
            text_color="white",
            border_width=0,
            show="*"
        )
        self.new_password_entry.pack(fill="x", pady=(0, 10))
        
        # Confirm New Password
        ctk.CTkLabel(
            password_inner_frame,
            text="Confirm New Password",
            font=("Arial", 14),
            text_color="white"
        ).pack(anchor="w", pady=(10, 5))
        
        self.confirm_password_entry = ctk.CTkEntry(
            password_inner_frame,
            height=40,
            fg_color="#222222",
            text_color="white",
            border_width=0,
            show="*"
        )
        self.confirm_password_entry.pack(fill="x", pady=(0, 10))
        
        # Save Button
        save_btn = ctk.CTkButton(
            form_container,
            text="Save Changes",
            font=("Arial", 16, "bold"),
            fg_color="#d92525",
            text_color="white",
            hover_color="#b71c1c",
            height=50,
            corner_radius=5,
            command=self.save_profile
        )
        save_btn.pack(fill="x", pady=(20, 0))

    def save_profile(self):
        """Save profile changes to the database"""
        # Get input values
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip()
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Basic validation
        if not first_name or not last_name or not email:
            messagebox.showwarning("Input Error", "Name and email fields are required.")
            return
        
        # Email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return
        
        try:
            connection = mysql.connector.connect(**self.DB_CONFIG)
            cursor = connection.cursor()
            
            # Check if email already exists for a different user
            if email != self.user_data['email']:
                cursor.execute("SELECT email FROM Users WHERE email = %s AND userID != %s", (email, self.user_id))
                if cursor.fetchone():
                    messagebox.showerror("Email Error", "This email is already in use by another account.")
                    return
            
            # Update user information
            if current_password:
                # If password is provided, verify current password and update with new password
                hashed_current = hashlib.sha256(current_password.encode()).hexdigest()
                
                # Verify current password
                cursor.execute("SELECT password FROM Users WHERE userID = %s", (self.user_id,))
                stored_password = cursor.fetchone()[0]
                
                if hashed_current != stored_password:
                    messagebox.showerror("Password Error", "Current password is incorrect.")
                    return
                
                # Validate new password
                if not new_password:
                    messagebox.showwarning("Password Error", "New password cannot be empty.")
                    return
                
                if new_password != confirm_password:
                    messagebox.showwarning("Password Error", "New passwords do not match.")
                    return
                
                if len(new_password) < 6:
                    messagebox.showwarning("Password Error", "New password must be at least 6 characters long.")
                    return
                
                # Hash the new password
                hashed_new = hashlib.sha256(new_password.encode()).hexdigest()
                
                # Update user with new password
                cursor.execute(
                    "UPDATE Users SET first_name = %s, last_name = %s, email = %s, password = %s WHERE userID = %s",
                    (first_name, last_name, email, hashed_new, self.user_id)
                )
            else:
                # Update user without changing password
                cursor.execute(
                    "UPDATE Users SET first_name = %s, last_name = %s, email = %s WHERE userID = %s",
                    (first_name, last_name, email, self.user_id)
                )
            
            connection.commit()
            messagebox.showinfo("Success", "Profile updated successfully!")
            
            # Update user name in session file
            self.update_session_name(f"{first_name} {last_name}")
            
            # Refresh user data
            self.user_data = self.get_user_data()
            self.user_name = f"{first_name} {last_name}"
            
            # Clear password fields
            self.current_password_entry.delete(0, 'end')
            self.new_password_entry.delete(0, 'end')
            self.confirm_password_entry.delete(0, 'end')
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def update_session_name(self, new_name):
        """Update the user name in the session file"""
        try:
            with open("session.txt", "r") as file:
                lines = file.readlines()
            
            with open("session.txt", "w") as file:
                for line in lines:
                    if line.startswith("name="):
                        file.write(f"name={new_name}\n")
                    else:
                        file.write(line)
        except Exception as e:
            print(f"Error updating session: {e}")

    def navigate_to(self, screen_name):
        """Handle navigation between different screens"""
        # Close current window
        self.root.withdraw()
        
        try:
            if screen_name == "Home":
                # Open Home page
                subprocess.Popen([sys.executable, "home.py"])
                self.root.destroy()
            elif screen_name == "Previous Bookings":
                # Open Bookings page
                subprocess.Popen([sys.executable, "prevbook.py"])
                self.root.destroy()
            elif screen_name == "Profile":
                # Refresh current page
                self.root.deiconify()
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

    def run(self):
        """Run the profile page application"""
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    profile_page = ProfilePage()
    profile_page.run()