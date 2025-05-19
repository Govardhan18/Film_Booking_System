import customtkinter as ctk
from PIL import Image, ImageTk
import mysql.connector
import subprocess
import sys
import os
import hashlib
import threading
import time
from tkinter import messagebox
from datetime import datetime, timedelta
import random

class FilmBookingApp:
    def __init__(self):
        # Configure initial settings
        self.DB_CONFIG = {
            'host': 'localhost',
            'user': 'root',
            'password': 'new_password',  # Replace with your actual MySQL password
        }
        
        # Database name
        self.DB_NAME = 'film_booking'
        
        # Set appearance mode
        ctk.set_appearance_mode("dark")

        # Create main window
        self.root = ctk.CTk()
        self.root.title("Film Booking System")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        # Try to set window icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        # Create database and tables if they don't exist
        success = self.setup_database()
        
        # If database setup failed, show error message
        if not success:
            self.status_label = ctk.CTkLabel(
                self.root,
                text="Database setup failed. Please check your MySQL connection and credentials.",
                font=("Arial", 14, "bold"),
                text_color="red"
            )
            self.status_label.pack(pady=50)
            return
            
        # Create UI components
        self.create_main_interface()

    def setup_database(self):
        """Create database and tables if they don't exist"""
        connection = None
        cursor = None
        
        try:
            print("Attempting to connect to MySQL...")
            # First, connect without specifying a database
            connection = mysql.connector.connect(
                host=self.DB_CONFIG['host'],
                user=self.DB_CONFIG['user'],
                password=self.DB_CONFIG['password']
            )
            
            if not connection.is_connected():
                print("Failed to connect to MySQL")
                messagebox.showerror("Database Error", "Could not connect to MySQL. Please check if MySQL is running.")
                return False
                
            cursor = connection.cursor()
            print("Connected to MySQL successfully")

            # Drop database if it exists and create a new one (clean start)
            print("Creating fresh database...")
            cursor.execute(f"DROP DATABASE IF EXISTS {self.DB_NAME}")
            cursor.execute(f"CREATE DATABASE {self.DB_NAME}")
            cursor.execute(f"USE {self.DB_NAME}")
            print(f"Database '{self.DB_NAME}' created successfully")

            # Create Users table
            print("Creating Users table...")
            cursor.execute("""
            CREATE TABLE Users (
                userID INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
            """)
            print("Users table created")

            # Create Theaters table
            print("Creating Theaters table...")
            cursor.execute("""
            CREATE TABLE Theaters (
                theaterID INT AUTO_INCREMENT PRIMARY KEY,
                theaterName VARCHAR(100) NOT NULL,
                theaterLocation VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB;
            """)
            print("Theaters table created")

            # Create Movies table
            print("Creating Movies table...")
            cursor.execute("""
            CREATE TABLE Movies (
                movieID INT AUTO_INCREMENT PRIMARY KEY,
                movieTitle VARCHAR(255) NOT NULL,
                movieGenre VARCHAR(100) NOT NULL,
                movieDuration INT NOT NULL,
                movieRating DECIMAL(3,1) DEFAULT 0.0,
                description TEXT
            ) ENGINE=InnoDB;
            """)
            print("Movies table created")

            # Create Show table
            print("Creating Show table...")
            cursor.execute("""
            CREATE TABLE `Show` (
                showID INT AUTO_INCREMENT PRIMARY KEY,
                movieID INT,
                theaterID INT,
                showDate DATE NOT NULL,
                showTime VARCHAR(20) NOT NULL,
                FOREIGN KEY (movieID) REFERENCES Movies(movieID) ON DELETE CASCADE,
                FOREIGN KEY (theaterID) REFERENCES Theaters(theaterID) ON DELETE CASCADE
            ) ENGINE=InnoDB;
            """)
            print("Show table created")

            # Create Bookings table
            print("Creating Bookings table...")
            cursor.execute("""
            CREATE TABLE Bookings (
                bookingID INT AUTO_INCREMENT PRIMARY KEY,
                userID INT,
                showID INT,
                numTickets INT NOT NULL,
                totalPrice DECIMAL(10,2) NOT NULL,
                bookingDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (userID) REFERENCES Users(userID) ON DELETE CASCADE,
                FOREIGN KEY (showID) REFERENCES `Show`(showID) ON DELETE CASCADE
            ) ENGINE=InnoDB;
            """)
            print("Bookings table created")

            # Create Booking_Seats table (to track which seats are booked)
            print("Creating Booking_Seats table...")
            cursor.execute("""
            CREATE TABLE Booking_Seats (
                seatID INT AUTO_INCREMENT PRIMARY KEY,
                bookingID INT,
                seatNumber VARCHAR(10) NOT NULL,
                FOREIGN KEY (bookingID) REFERENCES Bookings(bookingID) ON DELETE CASCADE
            ) ENGINE=InnoDB;
            """)
            print("Booking_Seats table created")

            # Create Reports table
            print("Creating Report table...")
            cursor.execute("""
            CREATE TABLE Report (
                reportID INT AUTO_INCREMENT PRIMARY KEY,
                userID INT,
                date_generated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                path_stored VARCHAR(255),
                FOREIGN KEY (userID) REFERENCES Users(userID) ON DELETE CASCADE
            ) ENGINE=InnoDB;
            """)
            print("Report table created")

            print("Adding default data...")
            self.add_default_data(cursor)

            # Commit all changes
            connection.commit()
            print("Database setup completed successfully!")
            
            # Create or update a login.py configuration file to match the database schema
            self.update_login_file()
            
            return True
            
        except mysql.connector.Error as err:
            print(f"MySQL Error: {err}")
            messagebox.showerror("Database Error", f"Error setting up database: {err}")
            return False
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            return False
        finally:
            # Close cursor and connection if they exist
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
                print("MySQL connection closed")

    def update_login_file(self):
        """Update login.py file to match database schema"""
        try:
            # Create a backup of the original file if it exists
            if os.path.exists("login.py"):
                print("Creating backup of login.py...")
                with open("login.py", "r") as original:
                    with open("login.py.backup", "w") as backup:
                        backup.write(original.read())
                
                # Read the content of the file
                with open("login.py", "r") as file:
                    content = file.read()
                
                # Replace 'user_id' with 'userID' in the file
                content = content.replace("user_id", "userID")
                
                # Write the modified content back to the file
                with open("login.py", "w") as file:
                    file.write(content)
                
                print("Updated login.py to match database schema")
        except Exception as e:
            print(f"Error updating login.py: {e}")

    def add_default_data(self, cursor):
        """Add default data to the database"""
        try:
            print("Adding admin user...")
            # Add default admin user
            admin_password = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute("""
            INSERT INTO Users (first_name, last_name, email, password, role)
            VALUES ('Admin', 'User', 'admin@filmbook.com', %s, 'admin')
            """, (admin_password,))

            print("Adding regular user...")
            # Add default regular user
            user_password = hashlib.sha256("user123".encode()).hexdigest()
            cursor.execute("""
            INSERT INTO Users (first_name, last_name, email, password, role)
            VALUES ('Regular', 'User', 'user@filmbook.com', %s, 'user')
            """, (user_password,))

            print("Adding theaters...")
            # Add theaters
            theaters = [
                ('PVR Cinemas', 'City Center Mall, Main Street'),
                ('INOX Movies', 'Downtown Shopping Complex'),
                ('Cinepolis', 'West End Mall, Park Avenue')
            ]
            for theater in theaters:
                cursor.execute("INSERT INTO Theaters (theaterName, theaterLocation) VALUES (%s, %s)", theater)

            print("Adding movies...")
            # Add movies
            movies = [
                ('Interstellar', 'Sci-Fi', 169, 9.2, 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.'),
                ('The Shawshank Redemption', 'Drama', 142, 9.3, 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.'),
                ('The Dark Knight', 'Action', 152, 9.0, 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.'),
                ('Pulp Fiction', 'Crime', 154, 8.9, 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.'),
                ('Forrest Gump', 'Drama', 142, 8.8, 'The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.'),
                ('Inception', 'Sci-Fi', 148, 8.8, 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.')
            ]
            for movie in movies:
                cursor.execute("""
                INSERT INTO Movies (movieTitle, movieGenre, movieDuration, movieRating, description)
                VALUES (%s, %s, %s, %s, %s)
                """, movie)

            print("Adding shows...")
            # Add shows (for the next 14 days)
            # Get movie and theater IDs
            cursor.execute("SELECT movieID FROM Movies")
            movie_ids = [row[0] for row in cursor.fetchall()]

            cursor.execute("SELECT theaterID FROM Theaters")
            theater_ids = [row[0] for row in cursor.fetchall()]

            # Generate shows for each movie in each theater for the next 14 days
            show_times = ['10:00 AM', '1:30 PM', '4:00 PM', '7:30 PM', '10:00 PM']
            
            today = datetime.now()
            
            for movie_id in movie_ids:
                for theater_id in theater_ids:
                    for day in range(14):  # Next 14 days
                        show_date = (today + timedelta(days=day)).strftime('%Y-%m-%d')
                        # Randomly select 2-3 showtimes per day
                        daily_times = random.sample(show_times, k=random.randint(2, 3))
                        for show_time in daily_times:
                            cursor.execute("""
                            INSERT INTO `Show` (movieID, theaterID, showDate, showTime)
                            VALUES (%s, %s, %s, %s)
                            """, (movie_id, theater_id, show_date, show_time))

            print("Default data added successfully!")
        
        except Exception as e:
            print(f"Error adding default data: {e}")
            raise

    def create_main_interface(self):
        """Create the main application interface"""
        # Main container
        container = ctk.CTkFrame(self.root, fg_color="#d92525")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        # Application title
        title_frame = ctk.CTkFrame(container, fg_color="transparent")
        title_frame.pack(pady=(20, 30))

        ctk.CTkLabel(
            title_frame,
            text="FILM BOOKING SYSTEM",
            font=("Arial", 36, "bold"),
            text_color="white"
        ).pack()

        ctk.CTkLabel(
            title_frame,
            text="Your premier destination for movie tickets",
            font=("Arial", 14),
            text_color="white"
        ).pack(pady=(5, 0))

        # Loading the application logo if available
        try:
            if os.path.exists("logo.png"):
                img = Image.open("logo.png")
                img = img.resize((200, 200), Image.LANCZOS)
                logo_img = ImageTk.PhotoImage(img)
                
                logo_label = ctk.CTkLabel(container, image=logo_img, text="")
                logo_label.image = logo_img  # Keep a reference
                logo_label.pack(pady=(0, 30))
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Placeholder or no image if logo not available

        # Buttons container
        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.pack(pady=20)

        # Login button
        login_btn = ctk.CTkButton(
            buttons_frame,
            text="User Login",
            font=("Arial", 16, "bold"),
            fg_color="black",
            text_color="white",
            hover_color="#333333",
            width=200,
            height=50,
            corner_radius=10,
            command=self.open_login
        )
        login_btn.pack(pady=10)

        # Sign Up button
        signup_btn = ctk.CTkButton(
            buttons_frame,
            text="Sign Up",
            font=("Arial", 16, "bold"),
            fg_color="black",
            text_color="white",
            hover_color="#333333",
            width=200,
            height=50,
            corner_radius=10,
            command=self.open_signup
        )
        signup_btn.pack(pady=10)

        # Admin Login button
        admin_btn = ctk.CTkButton(
            buttons_frame,
            text="Admin Login",
            font=("Arial", 16, "bold"),
            fg_color="#333333",
            text_color="white",
            hover_color="#4d4d4d",
            width=200,
            height=50,
            corner_radius=10,
            command=self.open_admin_login
        )
        admin_btn.pack(pady=10)

        # Login credentials info
        credentials_frame = ctk.CTkFrame(container, fg_color="transparent")
        credentials_frame.pack(pady=(20, 0))
        
        ctk.CTkLabel(
            credentials_frame,
            text="Default Credentials:",
            font=("Arial", 12, "bold"),
            text_color="white"
        ).pack()
        
        ctk.CTkLabel(
            credentials_frame,
            text="Admin: admin@filmbook.com / admin123",
            font=("Arial", 12),
            text_color="white"
        ).pack()
        
        ctk.CTkLabel(
            credentials_frame,
            text="User: user@filmbook.com / user123",
            font=("Arial", 12),
            text_color="white"
        ).pack()

        # Footer with version information
        footer_frame = ctk.CTkFrame(container, fg_color="transparent", height=30)
        footer_frame.pack(side="bottom", fill="x")
        footer_frame.pack_propagate(False)

        ctk.CTkLabel(
            footer_frame,
            text="Film Booking System v1.0",
            font=("Arial", 10),
            text_color="white"
        ).pack(side="right")

        # Show a database status indicator
        self.status_label = ctk.CTkLabel(
            footer_frame,
            text="⚫ Checking database...",
            font=("Arial", 10),
            text_color="yellow"
        )
        self.status_label.pack(side="left")

        # Start a thread to check database connection
        threading.Thread(target=self.check_database_connection, daemon=True).start()

    def check_database_connection(self):
        """Check database connection and update status indicator"""
        try:
            connection = mysql.connector.connect(
                host=self.DB_CONFIG['host'],
                user=self.DB_CONFIG['user'],
                password=self.DB_CONFIG['password'],
                database=self.DB_NAME
            )
            if connection.is_connected():
                time.sleep(1)  # Short delay for visual effect
                self.status_label.configure(text="🟢 Database connected", text_color="#00FF00")
            else:
                self.status_label.configure(text="🔴 Database disconnected", text_color="#FF0000")
            connection.close()
        except Exception as e:
            print(f"Database connection error: {e}")
            self.status_label.configure(text="🔴 Database error", text_color="#FF0000")

    def open_login(self):
        """Open the login page"""
        try:
            # First, let's check if login.py exists and update it if needed
            if os.path.exists("login.py"):
                print("Updating login.py to ensure compatibility...")
                self.update_login_file()
                
            # Now open login.py
            subprocess.Popen([sys.executable, "login.py"])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open login page: {e}")

    def open_signup(self):
        """Open the signup page"""
        try:
            # First, let's check if signup.py exists and update it if needed
            if os.path.exists("signup.py"):
                print("Updating signup.py to ensure compatibility...")
                with open("signup.py", "r") as file:
                    content = file.read()
                
                # Replace 'user_id' with 'userID' in the file
                content = content.replace("user_id", "userID")
                
                # Write the modified content back to the file
                with open("signup.py", "w") as file:
                    file.write(content)
                
            # Now open signup.py
            subprocess.Popen([sys.executable, "signup.py"])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open signup page: {e}")

    def open_admin_login(self):
        """Open the admin login page"""
        try:
            # Check if admin_login.py exists, otherwise use login.py
            if os.path.exists("admin_login.py"):
                # Update admin_login.py to ensure compatibility
                with open("admin_login.py", "r") as file:
                    content = file.read()
                
                # Replace 'user_id' with 'userID' in the file
                content = content.replace("user_id", "userID")
                
                # Write the modified content back to the file
                with open("admin_login.py", "w") as file:
                    file.write(content)
                
                subprocess.Popen([sys.executable, "admin_login.py"])
            else:
                messagebox.showinfo("Admin Login", "Use email: admin@filmbook.com / password: admin123")
                subprocess.Popen([sys.executable, "login.py"])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open admin login page: {e}")

    def run(self):
        """Run the application"""
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    app = FilmBookingApp()
    app.run()