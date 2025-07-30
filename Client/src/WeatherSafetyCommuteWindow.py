import customtkinter as ctk
import re  # regex
from GlobalDormFunctions import httpJsonWeatherData, httpJsonCrimeData, httpJsonDistanceData
from GlobalVariables import weather_url, crime_url, distance_url
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import mplcyberpunk


postcode_pattern = r"^[A-Z]{1,2}\d[A-Z\d]?\d[A-Z]{2}$"


crime = "http://localhost:8080/GlobalDorm/webresources/globaldorm/crime?crime=all-crime&postcode="
distance = "http://localhost:8080/GlobalDorm/webresources/globaldorm/route?mode=driving&"


class WeatherSafetyCommuteWindow:
    """
    Manages the 'Weather - Safety - Commute' window, providing functionalities
    to fetch and display weather, crime, and commute information based on postcodes.
    It includes a dynamic chart for crime data.
    """
    def __init__(self, parent_app):
        """Initialises the weather, safety, and commute information window."""
        self.window = ctk.CTkToplevel(parent_app.window)
        self.window.title("Global Dorm: Weather - Safety - Commute")
        self.parent = parent_app

        parent_x = self.parent.window.winfo_x()  # for clarity
        parent_y = self.parent.window.winfo_y()
        self.grid_width = self.parent.width * 2

        self.window.geometry(f"{self.grid_width}x{self.parent.height}+{parent_x}+{parent_y}")
        self.window.resizable(False, False)

        self.grid_container = ctk.CTkFrame(self.window, width=self.grid_width, height=self.parent.height, fg_color="#27374D")
        self.grid_container.grid(row=0, column=0, sticky="nsew")

        self.left_frame = ctk.CTkFrame(self.grid_container, width=self.parent.width, height=self.parent.height, fg_color="#33495F")
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.add_image_to_left()

        self.right_frame = ctk.CTkFrame(self.grid_container, width=self.parent.width, height=self.parent.height, fg_color='#27374D')
        self.right_frame.grid(row=0, column=1, sticky="nsew")

#        self.frame = ctk.CTkFrame(self.window, width=window_width, height=window_height, fg_color='#27374D')
#        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        self.create_title()
        self.create_input_fields()
        self.create_buttons()
        self.canvas = None
        self.update_chart() # Initialises chart with no data, effectively clearing it
        self.clear_chart() # Explicitly clears the chart after initialisation
        self.create_results_display()
        self.update_results("") # Sets initial empty text in results box
        self.window.lift()
        self.window.focus_force()
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

    def add_image_to_left(self):
        """Adds the background image to the left panel."""
        home_image = ctk.CTkImage(light_image=Image.open("images/pexels-abdullahalmallah-13185437.jpg"),
                                  dark_image=Image.open("images/pexels-abdullahalmallah-13185437.jpg"),
                                  size=(self.parent.width, self.parent.height))

        home_image_label = ctk.CTkLabel(self.left_frame, text="", image=home_image)
        home_image_label.place(relx=0.5, rely=0.5, anchor="center")

    def close_window(self):
        """Closes the current window and quits the parent application."""
        self.window.destroy()
        self.parent.window.quit()

    def show_main_window(self):
        """
        Closes the current window and re-displays the main application window.
        Repositions the main window if necessary.
        """
        self.window.destroy()
        self.parent.window.deiconify()

        parent_x = self.parent.window.winfo_x()
        parent_y = self.parent.window.winfo_y()

        # this worked without change, why?
        self.parent.window.geometry(f"{self.grid_width}x{self.parent.height}+{parent_x}+{parent_y}")

    def create_title(self):
        """Creates and places the title label for the window."""
        self.title_label = ctk.CTkLabel(self.right_frame, text="Weather - Safety - Commute", font=("Helvetica", 24, "bold"))
        self.title_label.place(relx=0.5, rely=0.05, anchor="center")

    def create_input_fields(self):
        """Creates input fields for starting and ending locations (postcodes)."""
        self.start_label = ctk.CTkLabel(self.right_frame, text="Starting Location:", font=("Helvetica", 18))
        self.start_label.place(relx=0.5, rely=0.15, anchor="center")

        self.start_entry = ctk.CTkEntry(self.right_frame, font=("Helvetica", 16))
        self.start_entry.place(relx=0.5, rely=0.2, relwidth=0.6, anchor="center")

        self.end_label = ctk.CTkLabel(self.right_frame, text="Ending Location:", font=("Helvetica", 18))
        self.end_label.place(relx=0.5, rely=0.29, anchor="center")

        self.end_entry = ctk.CTkEntry(self.right_frame, font=("Helvetica", 16))
        self.end_entry.place(relx=0.5, rely=0.34, relwidth=0.6, anchor="center")

    def create_buttons(self):
        """Creates buttons for fetching weather, safety, and commute information, plus a back button."""
        def get_weather_information():
            """Fetches and displays weather information for the ending location postcode."""
            selected_location = self.end_entry.get()
            self.clear_chart()

            if re.match(postcode_pattern, selected_location.upper()):
                results_message = httpJsonWeatherData(weather_url(), selected_location)
            else:
                results_message = "Invalid postcode"

            self.update_results(results_message)

        self.weather_information_button = ctk.CTkButton(self.right_frame, text="Weather", command=get_weather_information, font=("Helvetica", 16),
                                                        text_color="#DDE6ED", fg_color="#526D82", hover_color="#9DB2BF")
        self.weather_information_button.place(relx=0.5, rely=0.45, relwidth=0.6, anchor="center")

        def get_safety_information():
            """
            Fetches and displays crime safety information for the ending location postcode.
            Also updates a chart with crime categories.
            """
            selected_location = self.end_entry.get()

            if re.match(postcode_pattern, selected_location.upper()):
                results_message, crime_data = httpJsonCrimeData(crime_url(), selected_location)
            else:
                results_message, crime_data = "Invalid postcode", None

            self.update_results(results_message)

            if crime_data:
                self.update_chart(crime_data)

        self.safety_information_button = ctk.CTkButton(self.right_frame, text="Safety", command=get_safety_information, font=("Helvetica", 16),
                                                       text_color="#DDE6ED", fg_color="#526D82", hover_color="#9DB2BF")
        self.safety_information_button.place(relx=0.5, rely=0.52, relwidth=0.6, anchor="center")

        def get_commute_information():
            """Fetches and displays commute information between the starting and ending postcodes."""
            start_location = self.start_entry.get()
            end_location = self.end_entry.get()
            self.clear_chart()

            if start_location and end_location:
                if re.match(postcode_pattern, start_location.upper()) and re.match(postcode_pattern, end_location.upper()):
                    results_message = httpJsonDistanceData(distance_url(), start_location, end_location)
                else:
                    results_message = "Invalid postcode(s) entered.\nNo spaces allowed!"
            elif not start_location and not end_location:
                results_message = ":)\n"
            else:
                results_message = "One of the locations is missing. Please complete both fields.\n"

            self.update_results(results_message)

        self.commute_information_button = ctk.CTkButton(self.right_frame, text="Commute", command=get_commute_information, font=("Helvetica", 18),
                                                        text_color="#DDE6ED", fg_color="#526D82", hover_color="#9DB2BF")
        self.commute_information_button.place(relx=0.5, rely=0.59, relwidth=0.6, anchor="center")

        def show_main_window():
            """Returns to the main application window."""
            self.window.destroy()
            self.parent.window.deiconify()

            parent_x = self.parent.window.winfo_x()
            parent_y = self.parent.window.winfo_y()

            self.parent.window.geometry(f"{self.grid_width}x{self.parent.height}+{parent_x}+{parent_y}")

        self.back_button = ctk.CTkButton(self.right_frame, text="Home", command=show_main_window, font=("Helvetica", 18),
                                         text_color="#DDE6ED", fg_color="#526D82", hover_color="#9DB2BF")
        self.back_button.place(relx=0.5, rely=0.92, relwidth=0.6, anchor="center")

    def update_chart(self, crime_data=None):
        """Updates or creates a bar chart displaying crime category counts."""
        if crime_data is None:
            return

        text_size = 10
        number_text_size = 8
        count_bar_gap = 0.1
        bar_width = 0.6
        layout_padding = 2

        self.clear_chart()

        figure = Figure(figsize=(6, 6), dpi=100)
        axes = figure.add_subplot(111)

        categories = list(crime_data.keys())
        counts = list(crime_data.values())

        bars = axes.bar(categories, counts, width=bar_width, zorder=2)

        axes.set_xticks(range(len(categories)))
        axes.set_xticklabels(categories, rotation=90, fontsize=text_size)

        for bar in bars:
            height = bar.get_height()
            axes.text(bar.get_x() + bar.get_width() / 2, height + count_bar_gap, str(height), ha='center', va='bottom', fontsize=number_text_size)

        axes.set_title("Crime Data", fontsize=12, fontweight='bold', pad=5)
        axes.set_xlabel("Crime Categories", fontsize=text_size, fontweight='bold', labelpad=10)
        axes.set_ylabel("Counts", fontsize=text_size, fontweight='bold', labelpad=0)

        figure.tight_layout(pad=layout_padding)

        self.canvas = FigureCanvasTkAgg(figure, self.left_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8)
        self.canvas.draw()

    def clear_chart(self):
        """Clears any displayed Matplotlib chart."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

    def create_results_display(self):
        """Creates a read-only text box to display results messages."""
        self.results_textbox = ctk.CTkTextbox(self.right_frame, font=("Helvetica", 14), width=400, height=150)  # relwidth overrides width
        self.results_textbox.place(relx=0.5, rely=0.75, relwidth=0.9, anchor="center")
        self.results_textbox.configure(state="disabled")

    def update_results(self, results_message):
        """Updates the results display textbox with a given message."""
        if results_message == "":
            return  # preserve the box message

        self.results_textbox.configure(state="normal")
        self.results_textbox.delete("1.0", "end")
        self.results_textbox.insert("1.0", results_message)
        self.results_textbox.configure(state="disabled")
