import customtkinter as ctk
from tkcalendar import Calendar
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from GlobalDormFunctions import fetch_dorm_room_names, add_application,cancel_application, httpJsonCrimeData
from GlobalDormFunctions import fetch_dorm_room_combined_information, view_room_application_history, httpJsonDistanceData
from GlobalVariables import global_fetch_user, global_authenticate
from GlobalVariables import database_url, crime_url, distance_url

# Positioning of the application is off when switching windows back and forth.
# ...only when the app is moved though.

class SearchAndApplyWindow:
    """
    Manages the 'Search and Apply for Rooms' window, allowing users to search,
    view details, apply for, and cancel applications for dorm rooms.
    It also integrates crime data visualisations and distance calculations.
    """
    def __init__(self, parent_app):
        """Initialises the search and apply window and its components."""
        self.window = ctk.CTkToplevel(parent_app.window)
        self.window.title("Global Dorm: Search and Apply for Rooms")
        self.parent = parent_app

        parent_x = self.parent.window.winfo_x()
        parent_y = self.parent.window.winfo_y()
        window_width = self.parent.width
        window_height = self.parent.height
        self.grid_width = self.parent.width * 2

        self.window.geometry(f"{self.grid_width}x{window_height}+{parent_x}+{parent_y}")
        self.window.resizable(False, False)

        self.grid_container = ctk.CTkFrame(self.window, width=self.grid_width, height=window_height, fg_color="#27374D")
        self.grid_container.grid(row=0, column=0, sticky="nsew")

        self.left_frame = ctk.CTkFrame(self.grid_container, width=window_width, height=window_height, fg_color="#33495F")
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.add_image_to_left()

        self.right_frame = ctk.CTkFrame(self.grid_container, width=window_width, height=window_height, fg_color='#27374D')
        self.right_frame.grid(row=0, column=1, sticky="nsew")

#        self.frame = ctk.CTkFrame(self.window, width=window_width, height=window_height, fg_color='#27374D')
#        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        self.create_title()
        self.create_dropdown_menu()
        self.create_username_password_fields()
        self.create_dorm_details_textbox()
        self.create_radio_buttons()
        self.create_action_button()
        self.create_back_button()
        
        self.min_price = None
        self.max_price = None
        self.city = None
        self.live_in_landlord = 2
        self.bills_included = 2
        self.shared_bathroom = 2
        self.languages_spoken = None
        self.available_from = None
        self.max_roommates = None
        self.selected_dorm_room_postcode = ""
        self.entered_location = ""  # line 471
        # self.refine_search() # allows the toggle to control
        self.canvas = None
        self.create_options_frame()
        self.window.lift()
        self.window.focus_force()
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

    def add_image_to_left(self):
        """Adds the background image to the left."""
        home_image = ctk.CTkImage(light_image=Image.open("images/kira-laktionov-ezyhA0jc1oU-unsplash.jpg"),
                                  dark_image=Image.open("images/kira-laktionov-ezyhA0jc1oU-unsplash.jpg"),
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

        # refer back to the WeatherSafetyCommuteWindow class, same function
        self.parent.window.geometry(f"{self.grid_width}x{self.parent.height}+{parent_x}+{parent_y}")

    def create_title(self):
        """Creates and places the title label for the window."""
        self.title_label = ctk.CTkLabel(self.right_frame, text="Search and Apply for Rooms", font=("Helvetica", 24, "bold"), text_color="#DDE6ED")
        self.title_label.place(relx=0.5, rely=0.05, anchor="center")

    def create_dropdown_menu(self):
        """Sets up the dropdown menu for selecting dorm rooms and its associated search button."""
        self.dropdown_var = ctk.StringVar()
        self.dropdown_var.set("Select a dorm room")

        self.dropdown_menu = ctk.CTkOptionMenu(self.right_frame, variable=self.dropdown_var, font=("Helvetica", 13.5), values=["search first..."])
        self.dropdown_menu.place(relx=0.05, rely=0.15, anchor="w", relwidth=0.6)

        self.search_button = ctk.CTkButton(self.right_frame, text="Search", command=self.populate_dropdown, font=("Helvetica", 16),
                                           text_color="#DDE6ED", fg_color="#526D82", hover_color="#9DB2BF")
        self.search_button.place(relx=0.75, rely=0.15, anchor="w", relwidth=0.2)
        self.dropdown_menu.configure(command=self.update_details_text_box)

    def populate_dropdown(self):
        """
        Fetches dorm room names based on current filters and populates the dropdown menu.
        Displays a message indicating success or failure.
        """
        dorm_options, message = fetch_dorm_room_names(database_url(), self.min_price, self.max_price, self.city, self.live_in_landlord, self.max_roommates,
                                                      self.bills_included, self.shared_bathroom, self.languages_spoken, self.available_from)
#        dorm_options = fetch_dorm_room_names(database_url())  # room_name=None
        self.dropdown_menu.configure(values=[])
        self.dropdown_menu.configure(values=dorm_options)
        self.show_secret_message(message)

    def create_username_password_fields(self):
        """Creates input fields for applicant name, password, and confirm password."""
        self.name_label = ctk.CTkLabel(self.right_frame, text="Name:", font=("Helvetica", 16), text_color="#DDE6ED")
        self.name_label.place(relx=0.05, rely=0.58, anchor="w")
        self.name_entry = ctk.CTkEntry(self.right_frame, font=("Helvetica", 16))
        self.name_entry.place(relx=0.35, rely=0.58, relwidth=0.6, anchor="w")

        self.password_label = ctk.CTkLabel(self.right_frame, text="Password:", font=("Helvetica", 16), text_color="#DDE6ED")
        self.password_label.place(relx=0.05, rely=0.65, anchor="w")
        self.password_entry = ctk.CTkEntry(self.right_frame, font=("Helvetica", 16), show="*")
        self.password_entry.place(relx=0.35, rely=0.65, relwidth=0.6, anchor="w")

        self.confirm_password_label = ctk.CTkLabel(self.right_frame, text="Confirm Password:", font=("Helvetica", 14), text_color="#DDE6ED")
        self.confirm_password_label.place(relx=0.05, rely=0.72, anchor="w")
        self.confirm_password_entry = ctk.CTkEntry(self.right_frame, font=("Helvetica", 16), show="*")
        self.confirm_password_entry.place(relx=0.35, rely=0.72, relwidth=0.6, anchor="w")

    def create_dorm_details_textbox(self):
        """Creates a read-only text box to display dorm room details."""
        self.dorm_details_textbox = ctk.CTkTextbox(self.right_frame, font=("Helvetica", 14), width=400, height=250)
        self.dorm_details_textbox.place(relx=0.5, rely=0.37, relwidth=0.9, anchor="center")
        self.dorm_details_textbox.configure(state="disabled")

    def update_details_text_box(self, selected_dorm):
        """Updates the dorm details textbox with information for the selected dorm room, including its postcode for other features."""
        selected_room = self.dropdown_var.get()

        postcode, dorm_details = fetch_dorm_room_combined_information(database_url(), selected_room)
        self.selected_dorm_room_postcode = postcode.replace(" ", "")

#        print(self.selected_dorm_room_postcode)  # error with postcode - %20...

        self.dorm_details_textbox.configure(state="normal")
        self.dorm_details_textbox.delete(0.0, ctk.END)
        self.dorm_details_textbox.insert("0.0", dorm_details)
        self.dorm_details_textbox.configure(state="disabled")

    def create_radio_buttons(self):
        """Creates radio buttons for choosing between 'Apply', 'Cancel', and 'History' actions."""
        self.radio_var = ctk.StringVar(value="apply")

        self.apply_radio = ctk.CTkRadioButton(self.right_frame, text="Apply", variable=self.radio_var, value="apply", font=("Helvetica", 14),
                                              text_color="#DDE6ED", command=self.update_button_text)
        self.apply_radio.place(relx=0.1, rely=0.79, anchor="w")

        self.cancel_radio = ctk.CTkRadioButton(self.right_frame, text="Cancel", variable=self.radio_var, value="cancel", font=("Helvetica", 14),
                                               text_color="#DDE6ED", command=self.update_button_text)
        self.cancel_radio.place(relx=0.55, rely=0.79, anchor="center")

        self.history_radio = ctk.CTkRadioButton(self.right_frame, text="History", variable=self.radio_var, value="history", font=("Helvetica", 14),
                                                text_color="#DDE6ED", command=self.update_button_text)
        self.history_radio.place(relx=0.9, rely=0.79, anchor="center")

    def update_button_text(self):
        """Updates the text of the action button based on the selected radio button."""
        selected_action = self.radio_var.get()

        if selected_action == "apply":
            self.action_button.configure(text="Apply for Room")
        elif selected_action == "cancel":
            self.action_button.configure(text="Cancel Application")
        elif selected_action == "history":
            self.action_button.configure(text="View History")

    def create_action_button(self):
        """Creates the main action button that triggers apply, cancel, or history functions."""
        self.action_button = ctk.CTkButton(self.right_frame, text="Apply for Room", command=self.trigger_action, font=("Helvetica", 16),
                                           text_color="#DDE6ED", fg_color="#526D82", hover_color="#9DB2BF")
        self.action_button.place(relx=0.5, rely=0.85, relwidth=0.6, anchor="center")

    def create_back_button(self):
        """Creates the 'Home' button to return to the main application window."""
        self.back_button = ctk.CTkButton(self.right_frame, text="Home", command=self.show_main_window, font=("Helvetica", 18),
                                         text_color="#DDE6ED", fg_color="#526D82", hover_color="#9DB2BF")
        self.back_button.place(relx=0.5, rely=0.92, relwidth=0.6, anchor="center")

    def trigger_action(self):
        """Calls the appropriate function based on the selected radio button."""
        selected_action = self.radio_var.get()
        if selected_action == "apply":
            self.apply_for_room()
        elif selected_action == "cancel":
            self.cancel_application()
        elif selected_action == "history":
            self.view_history()

    def apply_for_room(self):
        """Handles the logic for applying for a dorm room."""
        applicant_name = self.name_entry.get()
        password = self.password_entry.get()
        repeat_password = self.confirm_password_entry.get()
            
        if not applicant_name:
            message = "Please enter your name."
        elif not password or not repeat_password:
            message = "Please enter a password."
        elif password != repeat_password:
            message = "Passwords do not match. Please try again."
        else:
            if not global_authenticate(global_fetch_user(), password):
                message = "Incorrect passwords, try again."
            else:
                dorm_name = self.dropdown_var.get()
                message = add_application(database_url(), dorm_name, applicant_name, global_fetch_user(), password)

        self.show_secret_message(message)

    def cancel_application(self):
        """Handles the logic for cancelling a dorm room application."""
        applicant_name = self.name_entry.get()
        password = self.password_entry.get()
        repeat_password = self.confirm_password_entry.get()

        if not applicant_name:
            message = "Please enter your name."
        elif not password or not repeat_password:
            message = "Please enter a password."
        elif password != repeat_password:
            message = "Passwords do not match. Please try again."
        else:
            if not global_authenticate(global_fetch_user(), password):
                message = "Incorrect passwords, try again."
            else:
                dorm_name = self.dropdown_var.get()
                message = cancel_application(database_url(), global_fetch_user(), password, dorm_name, applicant_name)

        self.show_secret_message(message)

    def view_history(self):
        """Handles the logic for viewing a room's application history."""
        applicant_name = self.name_entry.get()
        password = self.password_entry.get()
        repeat_password = self.confirm_password_entry.get()
        
        message = ""
        dorm_details = ""
        
        if not applicant_name:
            message = "Please enter your name."
        elif not password or not repeat_password:
            message = "Please enter a password."
        elif password != repeat_password:
            message = "Passwords do not match. Please try again."
        else:
            if not global_authenticate(global_fetch_user(), password):
                message = "Incorrect passwords, try again."
            else:
                dorm_name = self.dropdown_var.get()
                message = "..."
                dorm_details = view_room_application_history(database_url(), dorm_name)
                
        self.dorm_details_textbox.configure(state="normal")
        self.dorm_details_textbox.delete(0.0, ctk.END)
        self.dorm_details_textbox.insert("0.0", dorm_details)
        self.dorm_details_textbox.configure(state="disabled")
        self.show_secret_message(message)
        
    def refine_search(self):
        """Creates and displays a scrollable frame with various input fields for refining dorm room searches."""
        # scrollable frame in the left_frame
        self.search_frame = ctk.CTkScrollableFrame(self.left_frame, width=self.parent.width * 0.8, height=self.parent.height // 3,
                                                   fg_color="#000000", bg_color="#000000")
        self.search_frame.place(relx=0.5, rely=0.2, anchor="center")

        # title
        search_query_label = ctk.CTkLabel(self.search_frame, text="Search Query", font=("Helvetica", 16, "bold"), text_color="#FFD700")
        search_query_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        query_fields = ["Min Price (per month)", "Max Price (per month)", "City", "Live-in Landlord",
                        "Max Roommates", "Bills Included", "Shared Bathroom", "Languages Spoken", "Available From..."]

        languages = ["English", "Spanish", "French", "German", "Mandarin", "Italian"]
        options = ["Yes", "No", "Either"]

        for index, field in enumerate(query_fields):
            row_index = index + 1

            label = ctk.CTkLabel(self.search_frame, text=field, font=("Helvetica", 14), text_color="#DDE6ED")
            label.grid(row=row_index, column=0, padx=10, pady=5, sticky="w")

            if field not in ["Live-in Landlord", "Bills Included", "Shared Bathroom", "Available From...", "Languages Spoken"]:
                entry = ctk.CTkEntry(self.search_frame, font=("Helvetica", 14))
                entry.grid(row=row_index, column=1, padx=10, pady=5, sticky="ew")
                setattr(self, f"{field.replace(' ', '_').lower()}_entry", entry)

            elif field == "Languages Spoken":
                language_dropdown = ctk.CTkComboBox(self.search_frame, values=languages, font=("Helvetica", 14))
                language_dropdown.grid(row=row_index, column=1, padx=10, pady=5, sticky="ew")
                setattr(self, "languages_spoken_dropdown", language_dropdown)

            elif field == "Live-in Landlord":
                self.live_in_landlord_dropdown = ctk.CTkOptionMenu(
                    self.search_frame,
                    values=options,
                    font=("Helvetica", 14),
                    dropdown_font=("Helvetica", 14),
                    text_color="#DDE6ED"
                )
                self.live_in_landlord_dropdown.set("Either")  # Default value
                self.live_in_landlord_dropdown.grid(row=row_index, column=1, padx=10, pady=5, sticky="ew")
                setattr(self, "live_in_landlord_dropdown", self.live_in_landlord_dropdown)

            elif field == "Bills Included":
                self.bills_included_dropdown = ctk.CTkOptionMenu(
                    self.search_frame,
                    values=options,
                    font=("Helvetica", 14),
                    dropdown_font=("Helvetica", 14),
                    text_color="#DDE6ED"
                )
                self.bills_included_dropdown.set("Either")  # Default value
                self.bills_included_dropdown.grid(row=row_index, column=1, padx=10, pady=5, sticky="ew")
                setattr(self, "bills_included_dropdown", self.bills_included_dropdown)

            elif field == "Shared Bathroom":
                self.shared_bathroom_dropdown = ctk.CTkOptionMenu(
                    self.search_frame,
                    values=options,
                    font=("Helvetica", 14),
                    dropdown_font=("Helvetica", 14),
                    text_color="#DDE6ED"
                )
                self.shared_bathroom_dropdown.set("Either")  # Default value
                self.shared_bathroom_dropdown.grid(row=row_index, column=1, padx=10, pady=5, sticky="ew")
                setattr(self, "shared_bathroom_dropdown", self.shared_bathroom_dropdown)

            elif field == "Available From...":
                self.available_from_label = ctk.CTkLabel(self.search_frame, text=field, font=("Helvetica", 14), text_color="#DDE6ED")
                self.available_from_label.grid(row=row_index, column=0, padx=10, pady=5, sticky="w")

                self.calendar = Calendar(self.search_frame, selectmode="day", date_pattern="yyyy-mm-dd", font=("Helvetica", 14),
                                         width=280, height=240)
                self.calendar.grid(row=row_index + 1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")  # ew is center

        self.search_frame.grid_columnconfigure(1, weight=1)
        self.search_frame.grid_columnconfigure(0, weight=1)
        self.search_frame.grid_rowconfigure(0, weight=0)
        self.search_frame.grid_rowconfigure(row_index + 1, weight=1)

        select_button = ctk.CTkButton(self.search_frame, text="Select", font=("Helvetica", 14), command=self.select_entries)
        select_button.grid(row=row_index + 2, column=0, columnspan=1, padx=10, pady=10, sticky="ew")

        reset_button = ctk.CTkButton(self.search_frame, text="Reset", font=("Helvetica", 14), command=self.reset_entries)
        reset_button.grid(row=row_index + 2, column=1, columnspan=1, padx=10, pady=10, sticky="ew")

    def select_entries(self):
        """Retrieves and stores the selected filter criteria from the search query fields."""
        min_price_widget = getattr(self, "min_price_(per_month)_entry", None)
        if min_price_widget:
            self.min_price = float(min_price_widget.get() or 0.0)
        else:
            self.min_price = 0.0

        max_price_widget = getattr(self, "max_price_(per_month)_entry", None)
        if max_price_widget:
            self.max_price = float(max_price_widget.get() or 0.0)
        else:
            self.max_price = 0.0

        city_widget = getattr(self, "city_entry", None)
        self.city = city_widget.get() if city_widget.get() else None

        live_in_landlord_dropdown = getattr(self, "live_in_landlord_dropdown", None)
        self.live_in_landlord = (
            {"No": 0, "Yes": 1, "Either": 2}.get(live_in_landlord_dropdown.get(), 2)
            if live_in_landlord_dropdown
            else 2
        )

        max_roommates_widget = getattr(self, "max_roommates_entry", None)
        if max_roommates_widget:
            self.max_roommates = int(max_roommates_widget.get() or 0)
        else:
            self.max_roommates = 0
            
        bills_included_dropdown = getattr(self, "bills_included_dropdown", None)
        self.bills_included = (
            {"No": 0, "Yes": 1, "Either": 2}.get(bills_included_dropdown.get(), 2)
            if bills_included_dropdown
            else 2
        )

        shared_bathroom_dropdown = getattr(self, "shared_bathroom_dropdown", None)
        self.shared_bathroom = (
            {"No": 0, "Yes": 1, "Either": 2}.get(shared_bathroom_dropdown.get(), 2)
            if shared_bathroom_dropdown
            else 2
        )

        languages_spoken_dropdown = getattr(self, "languages_spoken_dropdown", None)
        self.languages_spoken = languages_spoken_dropdown.get() if languages_spoken_dropdown else ""

        available_from_calendar = getattr(self, "calendar", None)
        self.available_from = available_from_calendar.get_date() if available_from_calendar else ""
        
    def reset_entries(self):
        """Resets all search filter entries to their default (empty or 'Either') states."""
        self.min_price = None
        self.max_price = None
        self.city = None
        self.max_roommates = None
        self.languages_spoken = None
        self.available_from = None

        # text boxes, "widgets" used becasue () is a syntax error
        if hasattr(self, "min_price_(per_month)_entry"):
            min_price_widget = getattr(self, "min_price_(per_month)_entry")
            min_price_widget.delete(0, 'end')
        if hasattr(self, "max_price_(per_month)_entry"):
            max_price_widget = getattr(self, "max_price_(per_month)_entry")
            max_price_widget.delete(0, 'end')
        if hasattr(self, "max_roommates_entry"):
            self.max_roommates_entry.delete(0, 'end')
        if hasattr(self, "city_entry"):
            self.city_entry.delete(0, 'end')
            
        # dropdown - yes, no, either
        if hasattr(self, "live_in_landlord_dropdown"):
            self.live_in_landlord_dropdown.set("Either")
            self.live_in_landlord = 2

        if hasattr(self, "bills_included_dropdown"):
            self.bills_included_dropdown.set("Either")
            self.bills_included = 2

        if hasattr(self, "shared_bathroom_dropdown"):
            self.shared_bathroom_dropdown.set("Either")
            self.shared_bathroom = 2

    def create_options_frame(self):
        """Creates the options frame with postcode entry and feature toggle switches."""
        self.options_frame = ctk.CTkFrame(self.left_frame, fg_color="#000000", bg_color="#000000",
                                          height=self.parent.height // 6, width=self.parent.width * 0.8)
        self.options_frame.place(relx=0.5, rely=0.9, anchor="center")

        options_label = ctk.CTkLabel(self.options_frame, text="Options", font=("Helvetica", 16, "bold"), 
                                     text_color="#FFD700")
        options_label.place(relx=0.5, rely=0.15, relwidth=0.4, anchor="center")

        self.postcode_entry = ctk.CTkEntry(self.options_frame, font=("Helvetica", 14), placeholder_text="Enter Postcode")
        self.postcode_entry.place(relx=0.05, rely=0.4, relwidth=0.6, relheight=0.25)

        self.select_button = ctk.CTkButton(self.options_frame, text="Select", font=("Helvetica", 14), 
                                           command=self.handle_postcode_selection, fg_color="#33495F", text_color="#DDE6ED")
        self.select_button.place(relx=0.7, rely=0.4, relwidth=0.25, relheight=0.25)

        self.toggle_vars = {"search_query": ctk.BooleanVar(value=False), "crime_data": ctk.BooleanVar(value=False),
                            "distance": ctk.BooleanVar(value=False)}

        self.search_query_toggle = ctk.CTkSwitch(self.options_frame, text="Search Query", font=("Helvetica", 12), 
                                                 variable=self.toggle_vars["search_query"], onvalue=True, offvalue=False,
                                                 command=lambda: [self.handle_toggle_logic(), self.toggle_search_frame()])
        self.search_query_toggle.place(relx=0.02, rely=0.75, relwidth=0.3333, relheight=0.2)

        self.crime_data_toggle = ctk.CTkSwitch(self.options_frame, text="Crime Data", font=("Helvetica", 12),
                                               variable=self.toggle_vars["crime_data"], onvalue=True, offvalue=False,
                                               command=lambda: [self.handle_toggle_logic(), self.toggle_crime_chart()])
        self.crime_data_toggle.place(relx=0.3933, rely=0.75, relwidth=0.3333, relheight=0.2)

        self.distance_toggle = ctk.CTkSwitch(self.options_frame, text="Distance", font=("Helvetica", 12),
                                             variable=self.toggle_vars["distance"], onvalue=True, offvalue=False,
                                             command=lambda: [self.handle_toggle_logic(), self.toggle_distance_frame()])
        self.distance_toggle.place(relx=0.7466, rely=0.75, relwidth=0.3333, relheight=0.2)

    def handle_postcode_selection(self):
        """Processes the entered postcode for use in other features."""
        postcode = self.postcode_entry.get().strip()
        if postcode:
            self.entered_location = postcode
            self.show_secret_message("Postcode entered.")
        else:
            self.show_secret_message("Please enter a postcode.")

    def handle_toggle_logic(self):
        """Ensures only one major feature (Search Query, Crime Data, Distance) is active at a time."""
        search_query_active = self.toggle_vars["search_query"].get()
        if search_query_active:
            self.toggle_vars["crime_data"].set(False)
            self.toggle_vars["distance"].set(False)

    def toggle_search_frame(self):
        """Toggles the visibility of the search filter frame."""
        if self.toggle_vars["search_query"].get():
            if not hasattr(self, "search_frame"):
                self.clear_crime_information()
                self.refine_search()

            if hasattr(self, "search_frame"):
                self.clear_crime_information()
                self.search_frame.place(relx=0.5, rely=0.2, anchor="center")
        else:
            if hasattr(self, "search_frame") and self.search_frame.winfo_exists():
                self.search_frame.place_forget()

    def toggle_crime_chart(self):
        """
        Toggles the display of the crime data chart.
        Fetches data and updates the chart if activated.
        """
        if self.toggle_vars["crime_data"].get():  # active
            results_message, crime_data = httpJsonCrimeData(crime_url(), self.selected_dorm_room_postcode)
            if crime_data:
                self.update_chart(crime_data)
                self.show_secret_message(results_message)
        else:
            self.clear_chart()
            
    def clear_crime_information(self):
        """Clears displayed crime chart and distance information."""
        if hasattr(self, 'distance_frame') and self.distance_frame is not None:
            self.distance_frame.place_forget()
            self.clear_chart()

    def toggle_distance_frame(self):
        """
        Toggles the visibility of the distance information frame.
        Creates the frame and displays route data if activated.
        """
        if self.toggle_vars["distance"].get():
            if not hasattr(self, "distance_frame"):
                self.create_distance_frame()
                self.route_data_message()
            if hasattr(self, "distance_frame"):
                self.distance_frame.place(relx=0.5, rely=0.68, anchor="center")
                self.route_data_message()
        else:
            if hasattr(self, "distance_frame") and self.distance_frame.winfo_exists():
                self.distance_frame.place_forget()
                
    def route_data_message(self):
        """Fetches and displays route distance information between the entered starting postcode and the selected dorm room postcode."""
        if not self.entered_location or not self.selected_dorm_room_postcode:
            self.text_widget.configure(state="normal")
            self.text_widget.delete("1.0", "end")
            self.text_widget.insert("1.0", "Please enter a starting location and select a dorm room.")
            self.text_widget.configure(state="disabled")
        else:
            route_message = httpJsonDistanceData(distance_url(), self.entered_location, self.selected_dorm_room_postcode) 
            self.text_widget.configure(state="normal")
            self.text_widget.delete("1.0", "end")
            self.text_widget.insert("1.0", route_message)
            self.text_widget.configure(state="disabled")

    def update_chart(self, crime_data=None):
        """
        Updates or creates a bar chart displaying crime category counts.
        Highlights the category with the maximum count.
        """
        if crime_data is None:
            return

        text_size = 10
        number_text_size = 8
        count_bar_gap = 0.1
        bar_width = 0.6
        layout_padding = 1

        self.clear_chart()

        figure = Figure(figsize=(4, 4), dpi=100)
        axes = figure.add_subplot(111)

        categories = list(crime_data.keys())
        counts = list(crime_data.values())
        max_count = max(counts) if counts else 0

        bars = axes.bar(categories, counts, width=bar_width, zorder=2, color=['red' if count == max_count else '#526D82' for count in counts])

        for bar in bars:
            height = bar.get_height()
            axes.text(bar.get_x() + bar.get_width() / 2, height + count_bar_gap, str(height), 
                      ha='center', va='bottom', fontsize=number_text_size)

        axes.set_xticks(range(len(categories)))
        axes.set_xticklabels(categories, rotation=90, fontsize=text_size)
        axes.set_title("Crime Data", fontsize=12, fontweight='bold', pad=5)
        axes.set_xlabel("Crime Categories", fontsize=text_size, fontweight='bold', labelpad=10)
        axes.set_ylabel("Counts", fontsize=text_size, fontweight='bold', labelpad=0)
        axes.grid(zorder=1)

        figure.tight_layout(pad=layout_padding)

        self.canvas = FigureCanvasTkAgg(figure, self.left_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.place(relx=0.5, rely=0.3, anchor="center", relwidth=0.8, relheight=0.5)
        self.canvas.draw()

    def clear_chart(self):
        """Clears any displayed Matplotlib chart."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

    def create_distance_frame(self):
        """Creates the frame and text widget to display commute distance information."""
        self.distance_frame = ctk.CTkFrame(self.left_frame, fg_color="#000000", bg_color="#000000",
                                           width=self.parent.width * 0.8, height=self.parent.height * 0.2)
        self.distance_frame.place(relx=0.5, rely=0.685, anchor="center")

        self.text_widget = ctk.CTkTextbox(self.distance_frame, font=("Helvetica", 13), width=self.parent.width * 0.8,
                                          height=self.parent.height * 0.2, wrap="word", fg_color="#000000", bg_color="#000000")

        self.text_widget.place(relx=0.5, rely=0.5, anchor="center")

#        self.text_widget.insert("1.0", "To achieve the highest marks(Mid 1st to Excep 1st), you must show initiative and inventiveness beyond the stated specification.\n"
#                                       "To achieve the highest marks(Mid 1st to Excep 1st), you must show initiative and inventiveness beyond the stated specification.\n"
#                                       "To achieve the highest marks(Mid 1st to Excep 1st), you must show initiative and inventiveness beyond the stated specification.\n"
#                                       "To achieve the highest marks(Mid 1st to Excep 1st), you must show initiative and inventiveness beyond the stated specification.\n")
        self.text_widget.configure(state="disabled")

    def show_secret_message(self, message):
        """Displays a temporary feedback message on the right frame."""
        secret_label = ctk.CTkLabel(self.right_frame, text=message, font=("Helvetica", 12),
                                    text_color="#FFD700", fg_color="transparent")
        secret_label.place(relx=0.5, rely=0.1, relwidth=0.95, anchor="center")

        self.window.after(2500, secret_label.destroy)