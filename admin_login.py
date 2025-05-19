import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import mysql.connector
import hashlib
from tkinter import messagebox
import sys
import subprocess
import os
import re

class AdminLoginApp:
    def __init__(self):
        # Database Configuration
        self.DB_CONFIG = {
            'host': 'localhost',
            'user': 'root',
            'password': 'new_password',  # Replace with your actual MySQL password
            'database': 'film_booking'
        }

        # Configure CustomTkinter
        ctk.set_appearance_mode("dark")
        
        # Main Window
        self.root = ctk.CTk()
        self.root.title("Film Booking - Admin Login")
        self.root.geometry("900x500")
        self.root.resizable(False, False)
        
        # Set window icon if available
        try:
            self.root.iconbitmap("icon.ico")  # Add your icon file if available
        except:
            pass

        # Main Container Frame
        self.container = ctk.CTkFrame(self.root, fg_color="#d92525")
        self.container.pack(fill="both", expand=True)

        # Create Login Form
        self.create_login_form()

    def create_login_form(self):
        # Left Side - Login Form
        form_frame = ctk.CTkFrame(self.container, fg_color="#d92525", width=450)
        form_frame.pack(side="left", fill="both", padx=40, pady=40)

        # Title
        ctk.CTkLabel(form_frame, text="Film Booking", 
                     font=("Arial", 28, "bold"), 
                     text_color="white").pack(anchor="w")
        ctk.CTkLabel(form_frame, text="Admin Panel Access",
                     font=("Arial", 14), 
                     text_color="white").pack(anchor="w", pady=(2, 25))

        # Warning/Info text
        ctk.CTkLabel(form_frame, 
                    text="⚠️ Restricted Area - Admin Access Only", 
                    font=("Arial", 14, "bold"), 
                    text_color="#FFD700").pack(anchor="w", pady=(0, 20))

        # Email Entry
        ctk.CTkLabel(form_frame, text="Email", 
                     font=("Arial", 14), 
                     text_color="white").pack(anchor="w", pady=(10, 5))
        self.email_entry = ctk.CTkEntry(form_frame, 
                                        placeholder_text="Enter admin email", 
                                        height=40, 
                                        fg_color="white", 
                                        text_color="black", 
                                        corner_radius=5)
        self.email_entry.pack(fill="x", pady=2)

        # Password Entry
        ctk.CTkLabel(form_frame, text="Password", 
                     font=("Arial", 14), 
                     text_color="white").pack(anchor="w", pady=(15, 5))
        
        # Password entry frame with show/hide functionality
        password_frame = ctk.CTkFrame(form_frame, fg_color="#d92525")
        password_frame.pack(fill="x", pady=2)
        
        self.password_entry = ctk.CTkEntry(password_frame, 
                                          placeholder_text="Enter admin password", 
                                          show="*", 
                                          height=40,
                                          fg_color="white", 
                                          text_color="black", 
                                          corner_radius=5)
        self.password_entry.pack(side="left", fill="x", expand=True)
        
        # Password visibility toggle
        self.password_visible = False
        self.toggle_btn = ctk.CTkButton(password_frame, 
                                        text="Show", 
                                        width=60, 
                                        height=40,
                                        fg_color="black", 
                                        hover_color="#333333",
                                        command=self.toggle_password_visibility)
        self.toggle_btn.pack(side="right", padx=(5, 0))

        # Login Button
        login_btn = ctk.CTkButton(form_frame, 
                                  text="Admin Login", 
                                  font=("Arial", 14, "bold"), 
                                  fg_color="black", 
                                  text_color="white", 
                                  height=40, 
                                  hover_color="#333333", 
                                  corner_radius=5,
                                  command=self.login_admin)
        login_btn.pack(fill="x", pady=(25, 15))
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login_admin())

        # Back to user login
        back_frame = ctk.CTkFrame(form_frame, fg_color="#d92525")
        back_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkLabel(back_frame, 
                     text="Not an admin? ", 
                     font=("Arial", 12), 
                     text_color="white").pack(side="left")
        
        user_login_link = ctk.CTkLabel(back_frame, 
                                   text="User Login", 
                                   font=("Arial", 12, "bold"), 
                                   text_color="white", 
                                   cursor="hand2")
        user_login_link.pack(side="left")
        user_login_link.bind("<Button-1>", lambda e: self.open_user_login())

        # Right Side - Image
        self.create_image_side()

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_visible:
            self.password_entry.configure(show="*")
            self.toggle_btn.configure(text="Show")
            self.password_visible = False
        else:
            self.password_entry.configure(show="")
            self.toggle_btn.configure(text="Hide")
            self.password_visible = True

    def create_image_side(self):
        # Image Frame
        image_frame = ctk.CTkFrame(self.container, fg_color="#d92525")
        image_frame.pack(side="right", fill="both", expand=True)

        # Try to load and resize image
        try:
            # Check if image exists (using admin-specific image if available)
            image_path = "admin_login.png" if os.path.exists("admin_login.png") else "cinema.png"
            
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"{image_path} not found")
                
            # Open the original image
            original_image = Image.open(image_path)
            
            # Get the frame dimensions
            frame_width = 300  # Matches the form frame width
            frame_height = 400  # Matches the window height
            
            # Calculate the resize dimensions while maintaining aspect ratio
            original_width, original_height = original_image.size
            aspect_ratio = original_width / original_height
            
            # Determine resize strategy
            if original_width / original_height > frame_width / frame_height:
                # Image is wider relative to frame
                new_width = frame_width
                new_height = int(new_width / aspect_ratio)
            else:
                # Image is taller relative to frame
                new_height = frame_height
                new_width = int(new_height * aspect_ratio)
            
            # Resize the image
            resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(resized_image)
            
            # Create label with the resized image
            image_label = ctk.CTkLabel(image_frame, image=photo, text="")
            image_label.image = photo  # Keep a reference
            image_label.place(relx=0.5, rely=0.5, anchor="center")
        
        except Exception as e:
            print(f"Image processing error: {e}")
            # Admin badge placeholder
            admin_badge = ctk.CTkLabel(image_frame, 
                                     text="ADMIN\nACCESS", 
                                     font=("Arial", 32, "bold"), 
                                     text_color="white")
            admin_badge.place(relx=0.5, rely=0.5, anchor="center")

    def login_admin(self):
        """Handle admin login process"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        # Basic validation
        if not email or not password:
            messagebox.showwarning("Input Error", "Please enter both email and password.")
            return

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return

        # Hash the password
        hashed_password = self.hash_password(password)

        try:
            # Establish database connection
            connection = mysql.connector.connect(**self.DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            # Check admin credentials - specifically looking for admin role
            cursor.execute(
                "SELECT user_id, first_name, last_name FROM Users WHERE email = %s AND password = %s AND role = 'admin'",
                (email, hashed_password)
            )
            
            admin = cursor.fetchone()
            
            if admin:
                # Save admin info for the session
                self.save_admin_session(admin)
                
                # Show welcome message
                messagebox.showinfo("Admin Access Granted", f"Welcome Admin {admin['first_name']} {admin['last_name']}!")
                
                # Close login window
                self.root.destroy()
                
                # Open admin dashboard
                self.open_admin_dashboard()
            else:
                # Check if the user exists but is not an admin
                cursor.execute(
                    "SELECT role FROM Users WHERE email = %s",
                    (email,)
                )
                user = cursor.fetchone()
                
                if user and user['role'] != 'admin':
                    messagebox.showerror("Access Denied", "You don't have admin privileges. Please use the regular user login.")
                else:
                    messagebox.showerror("Login Failed", "Invalid email or password.")
        
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Database connection error: {str(err)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def save_admin_session(self, admin):
        """Save admin session data to file"""
        try:
            with open("session.txt", "w") as file:
                file.write(f"user_id={admin['user_id']}\n")
                file.write(f"name={admin['first_name']} {admin['last_name']}\n")
                file.write(f"role=admin\n")
        except Exception as e:
            print(f"Error saving session: {e}")

    def open_user_login(self):
        """Open regular user login page"""
        try:
            # Close current window
            self.root.destroy()
            
            # Run login script
            subprocess.Popen([sys.executable, "login.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open user login page: {e}")

    def open_admin_dashboard(self):
        """Open admin dashboard"""
        try:
            # Run admin dashboard script
            subprocess.Popen([sys.executable, "admin.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open admin dashboard: {e}")

    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def run(self):
        """Run the admin login application"""
        self.root.mainloop()

# Run the admin login application
if __name__ == "__main__":
    admin_login = AdminLoginApp()
    admin_login.run()