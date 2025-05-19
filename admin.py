import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys
import subprocess
import mysql.connector
from datetime import datetime, timedelta
from tkinter import messagebox
from PIL import Image, ImageTk

class AdminDashboard:
    def __init__(self):
        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("Film Booking - Admin Dashboard")
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

        # Verify admin role
        if self.user_role != "admin":
            messagebox.showerror("Access Denied", "You do not have permission to access the admin dashboard.")
            self.open_home_page()
            return

        # Dashboard data
        self.stats = self.get_dashboard_stats()
        self.ticket_data = self.get_ticket_sales_data()
        self.genre_data = self.get_genre_data()

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
            
            # If no user ID, redirect to login
            if not self.user_id:
                raise Exception("No user ID found in session")
        except Exception as e:
            print(f"Error loading session: {e}")
            # Redirect to login if session can't be loaded
            self.logout()

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
        self.create_sidebar_button("📊", "Admin Dashboard", is_active=True)
        self.create_sidebar_button("🎟️", "Manage Bookings")
        self.create_sidebar_button("🎬", "Manage Movies")
        self.create_sidebar_button("🏢", "Manage Theaters")
        self.create_sidebar_button("👤", "Manage Users")
        self.create_sidebar_button("🏠", "Home")

        # Logout button
        self.create_logout_button()

    def create_sidebar_button(self, icon, text, is_active=False):
        button_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=40)
        button_frame.pack(fill="x", pady=3)
        button_frame.pack_propagate(False)

        # Active indicator (white bar on the left)
        if is_active:
            active_indicator = ctk.CTkFrame(button_frame, fg_color="white", width=5, height=40, corner_radius=0)
            active_indicator.place(x=0, y=0)

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

        # Title with current date
        current_date = datetime.now().strftime("%B %d, %Y")
        title_label = ctk.CTkLabel(
            content_container, 
            text=f"Admin Dashboard Overview - {current_date}", 
            font=("Arial", 28, "bold"), 
            text_color="white"
        )
        title_label.pack(anchor="w", pady=(0, 30))

        # Create top stats cards
        self.create_stats_cards(content_container)

        # Create charts section
        self.create_charts_section(content_container)

    def create_stats_cards(self, parent):
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 30))

        # Create three stat cards
        tickets_card = self.create_stat_card(
            stats_frame, 
            "Total Tickets Sold", 
            f"{self.stats['total_tickets']:,}", 
            "#ff5252", 
            "Last 30 Days"
        )
        
        movie_card = self.create_stat_card(
            stats_frame, 
            "Best Rated Movie", 
            f"{self.stats['best_movie']} ({self.stats['best_rating']}/10)", 
            "#ffd700"
        )
        
        revenue_card = self.create_stat_card(
            stats_frame, 
            "Revenue Generated", 
            f"${self.stats['total_revenue']:,.2f}", 
            "#4caf50", 
            "Last 30 Days"
        )

    def create_stat_card(self, parent, title, value, value_color, subtitle=None):
        card = ctk.CTkFrame(parent, fg_color="#2a2a2a", corner_radius=10, height=120)
        card.pack(side="left", fill="both", expand=True, padx=10)
        card.pack_propagate(False)  # Keep fixed height
        
        # Center the content vertically
        center_frame = ctk.CTkFrame(card, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1)
        
        # Title
        title_label = ctk.CTkLabel(
            center_frame, 
            text=title, 
            font=("Arial", 16), 
            text_color="white"
        )
        title_label.pack(anchor="center")
        
        # Value with color
        value_label = ctk.CTkLabel(
            center_frame, 
            text=value, 
            font=("Arial", 28, "bold"), 
            text_color=value_color
        )
        value_label.pack(anchor="center", pady=(5, 0))
        
        # Optional subtitle (like "Last 30 Days")
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                center_frame, 
                text=subtitle, 
                font=("Arial", 12), 
                text_color="#aaaaaa"
            )
            subtitle_label.pack(anchor="center", pady=(5, 0))
        
        return card

    def create_charts_section(self, parent):
        charts_frame = ctk.CTkFrame(parent, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, pady=(0, 0))

        # Create two chart cards
        sales_card, sales_chart_frame = self.create_chart_card(charts_frame, "Ticket Sales Over Time")
        genres_card, genres_chart_frame = self.create_chart_card(charts_frame, "Most Watched Genres")

        # Create the actual charts
        self.create_sales_chart(sales_chart_frame)
        self.create_genres_chart(genres_chart_frame)

    def create_chart_card(self, parent, title, width_ratio=0.5):
        card = ctk.CTkFrame(parent, fg_color="#2a2a2a", corner_radius=10)
        card.pack(side="left", fill="both", expand=True, padx=10)
        
        # Title
        title_label = ctk.CTkLabel(
            card, 
            text=title, 
            font=("Arial", 18, "bold"), 
            text_color="white"
        )
        title_label.pack(anchor="w", padx=20, pady=15)
        
        # Chart placeholder frame
        chart_frame = ctk.CTkFrame(card, fg_color="#222222", corner_radius=5)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        return card, chart_frame

    def create_sales_chart(self, parent):
        # Get data for chart
        weeks = [f"Week {i}" for i in range(1, len(self.ticket_data) + 1)]
        tickets = self.ticket_data
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        fig.patch.set_facecolor('#222222')
        ax.set_facecolor('#222222')
        
        # Create bar chart
        bars = ax.bar(weeks, tickets, color='#d92525', width=0.6)
        
        # Customize appearance
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#555555')
        ax.spines['left'].set_color('#555555')
        
        ax.tick_params(colors='white', which='both')
        ax.set_ylabel('Tickets Sold', color='white')
        
        # Add data labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                    f'{int(height)}', ha='center', va='bottom', color='white')
        
        # Remove any existing widgets
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Add the chart to the frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        return canvas

    def create_genres_chart(self, parent):
        # Get data for chart
        genres = list(self.genre_data.keys())
        views = list(self.genre_data.values())
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        fig.patch.set_facecolor('#222222')
        ax.set_facecolor('#222222')
        
        # Create bar chart with a different color
        bars = ax.bar(genres, views, color='#ffd700', width=0.6)
        
        # Customize appearance
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#555555')
        ax.spines['left'].set_color('#555555')
        
        ax.tick_params(colors='white', which='both')
        ax.set_ylabel('Total Views', color='white')
        
        # Add data labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 100,
                    f'{int(height)}', ha='center', va='bottom', color='white')
        
        # Remove any existing widgets
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Add the chart to the frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        return canvas

    def navigate_to(self, screen_name):
        """Handle navigation between different screens"""
        # Close current window
        self.root.withdraw()
        
        try:
            if screen_name == "Home":
                # Open Home page
                self.open_home_page()
            elif screen_name == "Manage Bookings":
                # Open Manage Bookings page (you would create this file)
                subprocess.Popen([sys.executable, "admin_bookings.py"])
                self.root.destroy()
            elif screen_name == "Manage Movies":
                # Open Manage Movies page (you would create this file)
                subprocess.Popen([sys.executable, "admin_movies.py"])
                self.root.destroy()
            elif screen_name == "Manage Theaters":
                # Open Manage Theaters page (you would create this file)
                subprocess.Popen([sys.executable, "admin_theaters.py"])
                self.root.destroy()
            elif screen_name == "Manage Users":
                # Open Manage Users page (you would create this file)
                subprocess.Popen([sys.executable, "admin_users.py"])
                self.root.destroy()
            elif screen_name == "Admin Dashboard":
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

    # Database methods
    def get_dashboard_stats(self):
        """Get statistics for the dashboard"""
        # In a real implementation, you would query the database for these statistics
        # For demonstration, we'll return sample data
        try:
            # You would replace this with actual database queries
            # Example queries would look like:
            #
            # connection = mysql.connector.connect(**self.DB_CONFIG)
            # cursor = connection.cursor()
            #
            # # Get total tickets sold in last 30 days
            # thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            # cursor.execute("""
            #    SELECT SUM(numTickets) FROM Bookings
            #    JOIN Show ON Bookings.showID = Show.showID
            #    WHERE Show.showDate >= %s
            # """, (thirty_days_ago,))
            # total_tickets = cursor.fetchone()[0] or 0
            
            return {
                'total_tickets': 12450,
                'best_movie': 'Interstellar',
                'best_rating': 9.2,
                'total_revenue': 125800.00
            }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {
                'total_tickets': 0,
                'best_movie': 'None',
                'best_rating': 0,
                'total_revenue': 0.00
            }

    def get_ticket_sales_data(self):
        """Get ticket sales data for the chart"""
        # In a real implementation, you would query the database for this data
        # For demonstration, we'll return sample data
        try:
            # Sample data - in a real implementation, you would get this from the database
            return [1200, 1500, 1300, 1800]
        except Exception as e:
            print(f"Error getting ticket sales data: {e}")
            return [0, 0, 0, 0]

    def get_genre_data(self):
        """Get genre popularity data for the chart"""
        # In a real implementation, you would query the database for this data
        # For demonstration, we'll return sample data
        try:
            # Sample data - in a real implementation, you would get this from the database
            return {
                'Action': 3400,
                'Drama': 2900,
                'Comedy': 2500,
                'Sci-Fi': 2700
            }
        except Exception as e:
            print(f"Error getting genre data: {e}")
            return {}

    def run(self):
        """Run the admin dashboard application"""
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    admin_dashboard = AdminDashboard()
    admin_dashboard.run()