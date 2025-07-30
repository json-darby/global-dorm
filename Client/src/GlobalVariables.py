logged_in_user = ""
logged_in_password = ""

# database = "http://localhost:8080/GlobalDorm/webresources/database"
# weatherPostcode = "http://localhost:8080/GlobalDorm/webresources/globaldorm/weather?postcode="
# crime = "http://localhost:8080/GlobalDorm/webresources/globaldorm/crime?crime=all-crime&postcode="
# distance = "http://localhost:8080/GlobalDorm/webresources/globaldorm/route?mode=driving&"

servers = {"netbeans": "localhost:8080", "docker": "localhost:8081", "azure": "20.162.251.254:8080"}
current_server = servers["netbeans"]

'''
This is quite unconventional.
Created a centralised place to put links and login information.
Seemed like a good idea at the time.
'''

def global_set_user(username, password):
    global logged_in_user, logged_in_password
    logged_in_user = username
    logged_in_password = password


def global_fetch_user():
    global logged_in_user
    return logged_in_user


def global_fetch_password():
    global logged_in_password
    return logged_in_password


def global_authenticate(username, password):
    global logged_in_user, logged_in_password
    if logged_in_user == username and logged_in_password == password:
        return True
    return False


def change_server(server):
    global current_server
    current_server = servers[server]


def global_fetch_server():
    global current_server

    for server_name, server_url in servers.items():
        if server_url == current_server:
            return server_name


def database_url():
    return f"http://{current_server}/GlobalDorm/webresources/database"


def weather_url():
    return f"http://{current_server}/GlobalDorm/webresources/globaldorm/weather?postcode="


def crime_url():
    return f"http://{current_server}/GlobalDorm/webresources/globaldorm/crime?crime=all-crime&postcode="


def distance_url():
    return f"http://{current_server}/GlobalDorm/webresources/globaldorm/route?mode=driving&"
