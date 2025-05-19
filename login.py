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

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'new_password',  # Replace with your actual MySQL password
    'database': 'film_booking'
}

class LoginApp:
    def __init__(self):
        # Configure CustomTkinter
        ctk.set_appearance_mode("light")
        
        # Main Window
        self.root = ctk.CTk()
        self.root.title("Film Booking - Login")
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
        ctk.CTkLabel(form_frame, text="Manage your movie bookings seamlessly.",
                     font=("Arial", 14), 
                     text_color="white").pack(anchor="w", pady=(2, 25))

        # Email Entry
        ctk.CTkLabel(form_frame, text="Email", 
                     font=("Arial", 14), 
                     text_color="white").pack(anchor="w", pady=(10, 5))
        self.email_entry = ctk.CTkEntry(form_frame, 
                                        placeholder_text="Enter your email", 
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
                                          placeholder_text="Enter your password", 
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

        # Remember me checkbox
        self.remember_var = tk.IntVar()
        remember_check = ctk.CTkCheckBox(form_frame, 
                                         text="Remember me", 
                                         text_color="white",
                                         variable=self.remember_var,
                                         fg_color="black",
                                         hover_color="#333333")
        remember_check.pack(anchor="w", pady=(10, 5))

        # Login Button
        login_btn = ctk.CTkButton(form_frame, 
                                  text="Login", 
                                  font=("Arial", 14, "bold"), 
                                  fg_color="black", 
                                  text_color="white", 
                                  height=40, 
                                  hover_color="#333333", 
                                  corner_radius=5,
                                  command=self.login_user)
        login_btn.pack(fill="x", pady=(15, 10))
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login_user())

        # Signup Section
        signup_frame = ctk.CTkFrame(form_frame, fg_color="#d92525")
        signup_frame.pack(fill="x")

        ctk.CTkLabel(signup_frame, 
                     text="Don't have an account? ", 
                     font=("Arial", 12), 
                     text_color="white").pack(side="left")
        
        signup_link = ctk.CTkLabel(signup_frame, 
                                   text="Sign Up", 
                                   font=("Arial", 12, "bold"), 
                                   text_color="white", 
                                   cursor="hand2")
        signup_link.pack(side="left")
        signup_link.bind("<Button-1>", lambda e: self.open_signup())

        # Forgot Password
        forgot_password = ctk.CTkLabel(form_frame, 
                                       text="Forgot Password?", 
                                       font=("Arial", 12), 
                                       text_color="white", 
                                       cursor="hand2")
        forgot_password.pack(anchor="center", pady=(10, 0))
        forgot_password.bind("<Button-1>", lambda e: self.forgot_password())

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
            # Check if image exists
            if not os.path.exists("cinema.png"):
                raise FileNotFoundError("cinema.png not found")
                
            # Open the original image
            original_image = Image.open("cinema.png")
            
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
            placeholder = ctk.CTkLabel(image_frame, 
                                       text="[Cinema Image]", 
                                       font=("Arial", 20), 
                                       text_color="white")
            placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def login_user(self):
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
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor(dictionary=True)
            
            # Check user credentials
            cursor.execute(
                "SELECT userID, first_name, last_name, role FROM Users WHERE email = %s AND password = %s",
                (email, hashed_password)
            )
            
            user = cursor.fetchone()
            
            if user:
                # Save user info for the session
                self.save_user_session(user)
                
                # Show welcome message
                messagebox.showinfo("Success", f"Welcome {user['first_name']} {user['last_name']}!")
                
                # Close login window
                self.root.destroy()
                
                # Open home page
                self.open_home_page()
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

    def save_user_session(self, user):
        """Save user session data to file"""
        if self.remember_var.get():
            # If you want to implement remember me functionality,
            # you could save session info to a file here
            pass
            
        # Create a session file with user data
        try:
            with open("session.txt", "w") as file:
                file.write(f"userID={user['userID']}\n")
                file.write(f"name={user['first_name']} {user['last_name']}\n")
                file.write(f"role={user['role']}\n")
        except Exception as e:
            print(f"Error saving session: {e}")

    def forgot_password(self):
        """Handle forgot password functionality"""
        email = self.email_entry.get().strip()
        
        if not email:
            messagebox.showinfo("Info", "Please enter your email address in the email field.")
            return
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return
            
        # Here you would implement the password reset functionality
        # For now, just show a message
        messagebox.showinfo("Password Reset", 
                           f"Password reset instructions have been sent to {email} if an account exists.")

    def open_signup(self):
        try:
            # Close current window
            self.root.destroy()
            
            # Run signup script
            subprocess.Popen([sys.executable, "signup.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open signup page: {e}")

    def open_home_page(self):
        try:
            # Run home page script
            subprocess.Popen([sys.executable, "home.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open home page: {e}")

    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def run(self):
        """Run the login application"""
        self.root.mainloop()

# Run the login application
if __name__ == "__main__":
    login_app = LoginApp()
    login_app.run()