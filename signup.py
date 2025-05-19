import customtkinter as ctk
from PIL import Image, ImageTk
import mysql.connector
import hashlib
import sys
import re
from tkinter import messagebox
import subprocess
import os

# Database Configuration - Consider moving this to a shared config file
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'new_password',  # Replace with your actual MySQL password
    'database': 'film_booking'
}

# Environment setup for Tkinter libraries - Consider making this conditional
# Only set if these paths don't exist in the environment already
if 'TCL_LIBRARY' not in os.environ:
    os.environ['TCL_LIBRARY'] = r"C:\Users\buvan\AppData\Local\Programs\Python\Python39\tcl\tcl8.6"
if 'TK_LIBRARY' not in os.environ:
    os.environ['TK_LIBRARY'] = r"C:\Users\buvan\AppData\Local\Programs\Python\Python39\tcl\tk8.6"

class SignupApplication:
    def __init__(self):
        # Configure CustomTkinter
        ctk.set_appearance_mode("light")

        # Main Window
        self.root = ctk.CTk()
        self.root.title("Film Booking - Sign Up")
        self.root.geometry("1000x1000")
        self.root.resizable(False, False)
        self.root.configure(fg_color="#d92525")
        
        # Try to set window icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        # Create UI Components
        self.create_signup_form()
        self.create_right_side_image()
        
        # Bind Enter key to signup
        self.root.bind('<Return>', lambda event: self.register_user())

    def create_signup_form(self):
        # Left Frame for Signup Form
        left_frame = ctk.CTkFrame(self.root, fg_color="#d92525", corner_radius=0)
        left_frame.pack(side="left", fill="both", expand=True, padx=(50, 20), pady=50)

        # Title
        ctk.CTkLabel(left_frame, text="Film Booking", 
                     font=("Arial", 32, "bold"), 
                     text_color="white").pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(left_frame, 
                     text="Manage your movie bookings seamlessly.",
                     font=("Arial", 14), 
                     text_color="white").pack(anchor="w", pady=(0, 30))

        # First Name Entry
        self.first_name_label = ctk.CTkLabel(left_frame, text="First Name", 
                                             font=("Arial", 12), 
                                             text_color="white")
        self.first_name_label.pack(anchor="w", pady=(0, 5))
        self.first_name_entry = self.create_entry(left_frame, "Enter your First Name")
        self.first_name_entry.pack(fill="x", pady=(0, 15))

        # Last Name Entry
        self.last_name_label = ctk.CTkLabel(left_frame, text="Last Name", 
                                            font=("Arial", 12), 
                                            text_color="white")
        self.last_name_label.pack(anchor="w", pady=(0, 5))
        self.last_name_entry = self.create_entry(left_frame, "Enter your Last Name")
        self.last_name_entry.pack(fill="x", pady=(0, 15))

        # Email Entry
        self.email_label = ctk.CTkLabel(left_frame, text="Email", 
                                        font=("Arial", 12), 
                                        text_color="white")
        self.email_label.pack(anchor="w", pady=(0, 5))
        self.email_entry = self.create_entry(left_frame, "Enter your email")
        self.email_entry.pack(fill="x", pady=(0, 15))

        # Password Entry with visibility toggle
        self.password_label = ctk.CTkLabel(left_frame, text="Password", 
                                           font=("Arial", 12), 
                                           text_color="white")
        self.password_label.pack(anchor="w", pady=(0, 5))
        
        # Password frame with entry and toggle button
        password_frame = ctk.CTkFrame(left_frame, fg_color="#d92525")
        password_frame.pack(fill="x", pady=(0, 5))
        
        self.password_entry = self.create_entry(password_frame, "Enter your password", is_password=True)
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
        
        # Password strength indicator
        self.password_strength_label = ctk.CTkLabel(left_frame, 
                                                   text="Password must be at least 8 characters", 
                                                   font=("Arial", 10), 
                                                   text_color="white")
        self.password_strength_label.pack(anchor="w", pady=(0, 15))
        
        # Add event to check password strength as user types
        self.password_entry.bind("<KeyRelease>", self.check_password_strength)

        # Confirm Password Entry
        self.confirm_password_label = ctk.CTkLabel(left_frame, text="Confirm Password", 
                                                 font=("Arial", 12), 
                                                 text_color="white")
        self.confirm_password_label.pack(anchor="w", pady=(0, 5))
        self.confirm_password_entry = self.create_entry(left_frame, "Confirm your password", is_password=True)
        self.confirm_password_entry.pack(fill="x", pady=(0, 25))

        # Terms and Conditions Checkbox
        self.terms_var = ctk.IntVar()
        terms_check = ctk.CTkCheckBox(left_frame, 
                                     text="I agree to the Terms and Conditions", 
                                     variable=self.terms_var,
                                     text_color="white",
                                     fg_color="black",
                                     hover_color="#333333")
        terms_check.pack(anchor="w", pady=(0, 15))

        # Signup Button
        signup_btn = ctk.CTkButton(left_frame, 
                                   text="Sign Up", 
                                   font=("Arial", 14, "bold"),
                                   fg_color="black", 
                                   text_color="white", 
                                   height=40, 
                                   hover_color="#333333", 
                                   corner_radius=5, 
                                   command=self.register_user)
        signup_btn.pack(fill="x", pady=(5, 15))

        # Login Link
        login_frame = ctk.CTkFrame(left_frame, fg_color="#d92525")
        login_frame.pack(fill="x")

        ctk.CTkLabel(login_frame, 
                     text="Already have an account?  ", 
                     font=("Arial", 12), 
                     text_color="white").pack(side="left")
        
        login_link = ctk.CTkLabel(login_frame, 
                                  text="Log In", 
                                  font=("Arial", 12, "bold"), 
                                  text_color="white", 
                                  cursor="hand2")
        login_link.pack(side="left")
        login_link.bind("<Button-1>", lambda e: self.open_login())

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_visible:
            self.password_entry.configure(show="*")
            self.confirm_password_entry.configure(show="*")
            self.toggle_btn.configure(text="Show")
            self.password_visible = False
        else:
            self.password_entry.configure(show="")
            self.confirm_password_entry.configure(show="")
            self.toggle_btn.configure(text="Hide")
            self.password_visible = True
    
    def check_password_strength(self, event=None):
        """Check password strength as user types"""
        password = self.password_entry.get()
        
        if not password:
            self.password_strength_label.configure(text="Password must be at least 8 characters", text_color="white")
            return
            
        # Basic strength check
        if len(password) < 8:
            self.password_strength_label.configure(text="Too short (min 8 characters)", text_color="#ffcc00")
            return
            
        # Check for complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        strength_score = sum([has_upper, has_lower, has_digit, has_special])
        
        if strength_score <= 2:
            self.password_strength_label.configure(text="Weak password", text_color="#ffcc00")
        elif strength_score == 3:
            self.password_strength_label.configure(text="Medium strength password", text_color="#ffaa00")
        else:
            self.password_strength_label.configure(text="Strong password", text_color="#00cc00")

    def create_right_side_image(self):
        # Right Frame for Image
        right_frame = ctk.CTkFrame(self.root, fg_color="#d92525", corner_radius=0)
        right_frame.pack(side="right", fill="both", expand=True, padx=30, pady=50)

        # Image Loading with Error Handling
        try:
            # Check if file exists
            if not os.path.exists("movie_viewer.png"):
                raise FileNotFoundError("movie_viewer.png not found")
                
            # Open and resize the image
            original_image = Image.open("movie_viewer.png")
            
            # Calculate resize dimensions
            original_width, original_height = original_image.size
            aspect_ratio = original_width / original_height
            
            # Resize with maintained aspect ratio
            new_width = 400
            new_height = int(new_width / aspect_ratio)
            
            resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
            movie_img = ImageTk.PhotoImage(resized_image)
            
            img_label = ctk.CTkLabel(right_frame, image=movie_img, text="")
            img_label.image = movie_img  # Keep a reference
            img_label.place(relx=0.5, rely=0.5, anchor="center")
        
        except Exception as e:
            # Placeholder if image loading fails
            placeholder = ctk.CTkLabel(right_frame, 
                                       text="Movie Viewer Image\n(Place movie_viewer.png)", 
                                       font=("Arial", 14), 
                                       text_color="white")
            placeholder.place(relx=0.5, rely=0.5, anchor="center")
            print(f"Image loading error: {e}")

    def create_entry(self, parent, placeholder, is_password=False):
        """Create a styled entry widget"""
        entry = ctk.CTkEntry(
            parent, 
            placeholder_text=placeholder, 
            height=40, 
            fg_color="white", 
            text_color="black",
            border_width=0, 
            corner_radius=5
        )
        
        if is_password:
            entry.configure(show="*")
        
        return entry

    def validate_input(self, first_name, last_name, email, password, confirm_password):
        """Validate user input"""
        # Check if all fields are filled
        if not all([first_name, last_name, email, password, confirm_password]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return False
            
        # Check if terms are accepted
        if not self.terms_var.get():
            messagebox.showwarning("Terms and Conditions", "You must accept the Terms and Conditions.")
            return False

        # Email validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return False

        # Password strength check
        if len(password) < 8:
            messagebox.showwarning("Weak Password", "Password must be at least 8 characters long.")
            return False
            
        # Check if passwords match
        if password != confirm_password:
            messagebox.showwarning("Password Mismatch", "Passwords do not match.")
            return False

        return True

    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self):
        """Register user in the database"""
        # Get input values
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Validate input
        if not self.validate_input(first_name, last_name, email, password, confirm_password):
            return

        # Hash the password
        hashed_password = self.hash_password(password)

        try:
            # Establish database connection
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            
            try:
                # First check if email already exists
                cursor.execute("SELECT email FROM Users WHERE email = %s", (email,))
                if cursor.fetchone():
                    messagebox.showerror("Registration Failed", "Email already exists. Please use a different email.")
                    return
                
                # Insert user into database
                cursor.execute(
                    "INSERT INTO Users (first_name, last_name, email, password, role, created_at) VALUES (%s, %s, %s, %s, %s, NOW())",
                    (first_name, last_name, email, hashed_password, "user")
                )
                
                connection.commit()
                messagebox.showinfo("Success", "User registered successfully! You can now log in.")
                
                # Redirect to login page
                self.open_login()
            
            except mysql.connector.IntegrityError:
                messagebox.showerror("Registration Failed", "Email already exists. Please use a different email.")
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Database error: {str(err)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def open_login(self):
        """Open login page"""
        try:
            subprocess.Popen([sys.executable, "login.py"])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open login page: {e}")

    def run(self):
        """Run the signup application"""
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    signup_app = SignupApplication()
    signup_app.run()