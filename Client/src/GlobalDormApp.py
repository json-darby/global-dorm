import customtkinter as ctk
import queue
from WeatherSafetyCommuteWindow import WeatherSafetyCommuteWindow
from SearchAndApplyWindow import SearchAndApplyWindow
from RabbitPushNotifications import PushNotifications
from PIL import Image
from GlobalDormFunctions import register_user, verify_user
from GlobalVariables import global_set_user, global_fetch_user, database_url
from GlobalVariables import servers, change_server, global_fetch_server


# database = "http://localhost:8080/GlobalDorm/webresources/database"
# http://localhost:8080/GlobalDorm/webresources/database/fetchDormRoomCombinedInformation?roomName=Quiet%20Room%20in%20Suburban%20House

# WARNING! Once application is cancelled, user cannot apply again...
# also, becareful with spaces


ctk.set_appearance_mode("dark")  # adjust as needed: "light", "dark", or "system"

'''Homepage of the appication'''
class GlobalDormApp:
    def __init__(self):
        self.height = 720
        self.width = int(self.height / 16 * 10)

        # window = whole, grid mathces the size, two frames for split sides.
        self.window = ctk.CTk()
        self.window.title("Global Dorm")
        # self.window.iconbitmap("images/icons/global_dorm_2.ico")
        self.window.geometry(f"{self.width * 2}x{self.height}")
        self.window.resizable(False, False)

        # grid
        self.grid_container = ctk.CTkFrame(self.window, width=self.width * 2, height=self.height, fg_color="#27374D")
        self.grid_container.grid(row=0, column=0, sticky="nsew")

        # left frame
        self.left_frame = ctk.CTkFrame(self.grid_container, width=self.width, height=self.height, fg_color="#33495F")
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.add_image_to_left()

        # right frame
        self.right_frame = ctk.CTkFrame(self.grid_container, width=self.width, height=self.height, fg_color="#27374D")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.create_labels()
        self.create_information_buttons()
        self.create_exit_logout_button()
        self.turn_notifications_on()  # has a test message at the moment

        self.message_queue = queue.Queue()  # message queue for receiving messages from the RabbitMQ listener
        self.push_notifications = PushNotifications(message_queue=self.message_queue)
        self.is_logged_in = False
        
        self.create_server_toggle_button()
        self.create_server_label()

        self.window.after(4000, self.create_login_register_form)
        self.window.mainloop()

    def add_image_to_left(self):
        '''Displays the main image on the left side.'''
        home_image = ctk.CTkImage(light_image=Image.open("images/pexels-abdullahalmallah-8654406.jpg"),
                                  dark_image=Image.open("images/pexels-abdullahalmallah-8654406.jpg"),
                                  size=(self.width, self.height))

        home_image_label = ctk.CTkLabel(self.left_frame, text="", image=home_image)
        home_image_label.place(relx=0.5, rely=0.5, anchor="center")

    def create_labels(self):
        '''Shows welcome and title labels.'''
        welcome_label = ctk.CTkLabel(self.right_frame, text="Welcome to", font=("Helvetica", 30),
                                     text_color="#DDE6ED", bg_color="transparent")
        welcome_label.place(relx=0.5, rely=0.12, anchor="center")

        global_dorm_label = ctk.CTkLabel(self.right_frame, text="Global Dorm", font=("Helvetica", 65, "bold"),
                                         text_color="#DDE6ED", bg_color="transparent")
        global_dorm_label.place(relx=0.5, rely=0.22, anchor="center")

    def create_information_buttons(self):
        '''Displays navigation buttons for features.'''
        def search_and_apply():
            if global_fetch_user() == "":
                return

            SearchAndApplyWindow(self)
            self.window.withdraw()

        def weather_safety_commute():
            WeatherSafetyCommuteWindow(self)
            self.window.withdraw()

        search_button = ctk.CTkButton(self.right_frame, text="Search and Apply for Rooms",
                                      command=search_and_apply, font=("Helvetica", 18), width=300, height=80,
                                      text_color="#DDE6ED", fg_color="#526D82", hover_color="#9DB2BF")
        search_button.place(relx=0.5, rely=0.46, anchor="center")

        weather_button = ctk.CTkButton(self.right_frame, text="Weather, Safety and Commute Info",
                                       command=weather_safety_commute, font=("Helvetica", 18), width=300, height=80,
                                       text_color="#DDE6ED", fg_color="#526D82", hover_color="#9DB2BF")
        weather_button.place(relx=0.5, rely=0.63, anchor="center")

    def create_exit_logout_button(self):
        '''Shows the exit/logout buttons.'''
        def exit_or_logout():
            if self.is_logged_in:
                self.logout()
            else:
                self.exit_application()

        self.exit_logout_button = ctk.CTkButton(self.right_frame, text="Exit", command=exit_or_logout, font=("Helvetica", 18),
                                                width=300, height=80, text_color="#DDE6ED", fg_color="#526D82", hover_color="#9DB2BF")
        self.exit_logout_button.place(relx=0.5, rely=0.8, anchor="center")

    def logout(self):
        '''Handles user logout.'''
        self.is_logged_in = False
        global_set_user("", "")
        if hasattr(self, "logged_in_user_label"):
            self.logged_in_user_label.destroy()
            del self.logged_in_user_label  # for ++ logins, delete previous reference
        self.update_exit_logout()
        self.create_login_register_form()

    def exit_application(self):
        '''Closes the application.'''
        self.window.destroy()
        self.push_notifications.stop_consuming()

    def update_exit_logout(self):
        '''Updates exit/logout button text.'''
        if self.is_logged_in:
            self.exit_logout_button.configure(text="Logout", command=self.logout)
        else:
            self.exit_logout_button.configure(text="Exit", command=self.exit_application)

    def create_login_register_form(self):
        '''Displays the login/registration form.'''
        self.register_form_frame = ctk.CTkFrame(self.left_frame, width=self.width * 0.8, height=self.height // 3,
                                                fg_color="#27374D", bg_color="#27374D")
        self.register_form_frame.place(relx=0.5, rely=0.2, anchor="center")

        self.title_label = ctk.CTkLabel(self.register_form_frame, text="Create an Account", font=("Helvetica", 20, "bold"),
                                        text_color="#DDE6ED", bg_color="transparent")
        self.title_label.place(relx=0.5, rely=0.15, anchor="center")

        self.username_entry = ctk.CTkEntry(self.register_form_frame, placeholder_text="Username", width=250)
        self.username_entry.place(relx=0.5, rely=0.3, anchor="center")

        self.password_entry = ctk.CTkEntry(self.register_form_frame, placeholder_text="Password", width=120, show="*")
        self.password_entry.place(relx=0.325, rely=0.45, anchor="center")

        self.confirm_password_entry = ctk.CTkEntry(self.register_form_frame, placeholder_text="Confirm Password", width=120, show="*")
        self.confirm_password_entry.place(relx=0.68, rely=0.45, anchor="center")

        already_member_label = ctk.CTkLabel(self.register_form_frame, text="Already registered?", font=("Helvetica", 12),
                                            text_color="#DDE6ED", bg_color="transparent")
        already_member_label.place(relx=0.28, rely=0.6, anchor="center")

        self.switch = ctk.CTkSwitch(self.register_form_frame, text="Switch to Login", command=self.toggle_form, progress_color="#526D82")
        self.switch.place(relx=0.69, rely=0.6, anchor="center")

        self.action_button = ctk.CTkButton(self.register_form_frame, text="Register", command=self.handle_action, width=200,
                                           fg_color="#526D82", hover_color="#9DB2BF")
        self.action_button.place(relx=0.5, rely=0.75, anchor="center")

    def toggle_form(self):
        '''Switches between login and registration forms.'''
        if self.switch.get():  # login
            self.confirm_password_entry.place_forget()
            self.password_entry.place(relx=0.325, rely=0.45, anchor="center")
            self.title_label.destroy()
            self.title_label = ctk.CTkLabel(self.register_form_frame, text="Login", font=("Helvetica", 20, "bold"),
                                            text_color="#DDE6ED", bg_color="transparent")
            self.title_label.place(relx=0.5, rely=0.15, anchor="center")
            self.action_button.configure(text="Login")
        else:  # register
            self.confirm_password_entry.place(relx=0.68, rely=0.45, anchor="center")
            self.password_entry.place(relx=0.325, rely=0.45, anchor="center")
            self.title_label.destroy()
            self.title_label = ctk.CTkLabel(self.register_form_frame, text="Create an Account", font=("Helvetica", 20, "bold"),
                                            text_color="#DDE6ED", bg_color="transparent")
            self.title_label.place(relx=0.5, rely=0.15, anchor="center")
            self.action_button.configure(text="Register")

    def clear_form(self):
        '''Clears form input fields.'''
        self.username_entry.delete(0, ctk.END)
        self.password_entry.delete(0, ctk.END)
        self.confirm_password_entry.delete(0, ctk.END)

    def handle_action(self):
        '''Processes login or registration.'''
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.switch.get():  # login
            message, verify_result_status = verify_user(database_url(), username, password, timeout=5)
            if verify_result_status == "success":
                self.is_logged_in = True
                global_set_user(username, password)
                self.display_logged_in_user(username)
                self.update_exit_logout()  # switch to logout
                self.register_form_frame.place_forget()
            else:
                self.show_secret_message(message)
        else:  # register
            confirm_password = self.confirm_password_entry.get()
            message, register_result_status = register_user(database_url(), username, password, confirm_password, timeout=5)
            if password == confirm_password:
                if register_result_status == "success":
                    self.clear_form()
                else:
                    self.show_secret_message(message)
            else:
                self.show_secret_message("Passwords do not match!")

    def display_logged_in_user(self, username):
        '''Shows the logged-in username.'''
        self.is_logged_in = True
        self.update_exit_logout()

        if not hasattr(self, "logged_in_user_label"):
            self.logged_in_user_label = ctk.CTkLabel(self.right_frame, text=f"@{username}", font=("Helvetica", 14),
                                                     text_color="#FFD700", bg_color="transparent")
            self.logged_in_user_label.place(relx=0.95, rely=0.01, anchor="ne")
        else:
            self.logged_in_user_label.configure(text=f"@{username}")

# rabbitmq rabbitmq rabbitmq rabbitmq rabbitmq rabbitmq rabbitmq
# rabbitmq rabbitmq rabbitmq rabbitmq rabbitmq rabbitmq rabbitmq
# rabbitmq rabbitmq rabbitmq rabbitmq rabbitmq rabbitmq rabbitmq
    def show_update_notification_message(self, message):
        '''Displays a sliding RabbitMQ notification.'''
        message_length = len(message)
        scaled_length = message_length / 40  # ensures full message is displayed
        relwidth = min(scaled_length, 2)
        update_notification_label = ctk.CTkLabel(self.right_frame, text=message, font=("Helvetica", 16),
                                                 text_color="#FFD700", fg_color="transparent")
        update_notification_label.place(relx=1, rely=0.95, relwidth=relwidth, anchor="nw")  # Start outside the frame on the right

        def notification_slide(current_relx=1.1):  # off right side
            if current_relx > -relwidth:
                update_notification_label.place_configure(relx=current_relx - 0.002)
                self.window.after(20, notification_slide, current_relx - 0.002)
            else:
                update_notification_label.destroy()
                print("destroyed.")
                self.check_for_new_messages()

        notification_slide()

    def show_secret_message(self, message):
        '''Shows temporary feedback messages.'''
        secret_label = ctk.CTkLabel(self.register_form_frame, text=message, font=("Helvetica", 12),
                                    text_color="#FFD700", fg_color="transparent")
        secret_label.place(relx=0.5, rely=0.9, relwidth=0.95, anchor="center")

        self.window.after(2500, secret_label.destroy)

    def turn_notifications_on(self):
        '''Displays the notifications checkbox.'''
        self.notifications_enabled = ctk.BooleanVar(value=False)

        notifications_checkbox = ctk.CTkCheckBox(self.right_frame, text="Enable Notifications", variable=self.notifications_enabled,
                                                 onvalue=True, offvalue=False, command=self.toggle_message)
        notifications_checkbox.place(relx=0.05, rely=0.015, anchor="nw")  # nw left, ne right

    def check_for_new_messages(self):
        '''Checks for new RabbitMQ messages.'''
        if not self.message_queue.empty():
            message = self.message_queue.get()
            self.show_update_notification_message(message)
        else:
            self.window.after(100, self.check_for_new_messages)

    def toggle_message(self):
        '''Toggles RabbitMQ message listening.'''
        if self.notifications_enabled.get():
            self.push_notifications.listen_for_messages()
            self.check_for_new_messages()
#            self.show_update_notification_message("This is just a test, just a little test. ABCDEFGHIJKLMNOPQRSTUVWXYZ")
#            self.show_update_notification_message("This is just a test.")
        else:
            self.push_notifications.stop_consuming()
            
    def create_server_toggle_button(self):  # switch servers - database doesn't work!
        '''Shows the server toggle button.'''
        def toggle_server():
            servers_list = list(servers.keys())
            current_server_index = servers_list.index(global_fetch_server())
            next_server_index = (current_server_index + 1) % len(servers_list)
            next_server = servers_list[next_server_index]
            change_server(next_server)
            self.update_server_label()

        button_size = 10
        self.server_toggle_button = ctk.CTkButton(self.right_frame, text="#", command=toggle_server, font=("Helvetica", 14),
                                                  width=button_size, height=button_size, text_color="#3D4A5E", fg_color="#27374D",
                                                  hover_color="#27374D")
        self.server_toggle_button.place(relx=0.477, rely=0.014, anchor="nw")

    def create_server_label(self):
        '''Shows the server toggle button.'''
        self.server_label = ctk.CTkLabel(self.right_frame, text=f"{global_fetch_server()}", font=("Helvetica", 14),
                                         text_color="#3D4A5E", bg_color="transparent")
        self.server_label.place(relx=0.51, rely=0.01, anchor="nw")

    def update_server_label(self):
        '''Updates the displayed server name. THIS ISN'T NECESSARY.'''
        self.server_label.configure(text=f"{global_fetch_server()}")


GlobalDormApp()
