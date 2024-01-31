
import mysql.connector as my
from typing import Any

class Database:
    con:Any=None
    def getConnection() -> Any:
        try:
            if Database.con is None or not Database.con.is_connected():
                Database.con = my.connect(
                    user='root',
                    password='1234',
                    database='db_hosts',
                    host='localhost', 
                    port=36000  
                )
                print("Connected to the database.")
        except my.Error as e:
            print(f"Error connecting to the database: {e}")
            raise  
        return Database.con
        
class IotDao:

    def __init__(self, mac):
        self.mac = mac

    @staticmethod
    def getAllIot():
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            query = "SELECT mac FROM Iot"
            cursor.execute(query)
            results = cursor.fetchall()

            iot_devices = []
            for result in results:
                iot_device = IotDao(*result)
                iot_devices.append(iot_device)

            return iot_devices
        except Error as e:
            print("Error while fetching data from Iot table:", e)
            return None
        finally:
            cursor.close()

    @staticmethod
    def add(mac):
        try:
            con = Database.getConnection()
            cursor = con.cursor()
            query = "INSERT INTO Iot (mac) VALUES (%s)"
            data = (mac,)
            cursor.execute(query, data)
            con.commit()
            return True
        except Error as e:
            print("Error while adding data to Iot table:", e)
            return False
        finally:
            if con:
                con.close()

    @staticmethod
    def get_random_mac_from_db():
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            # Query to select a random MAC address from the database
            query = "SELECT mac FROM Iot ORDER BY RAND() LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()

            if result:
                random_mac = result[0]
                return random_mac
            else:
                print("No MAC addresses found in the database.")
                return None
        except my.Error as e:
            print(f"Error retrieving random MAC address: {e}")
            return None
        finally:
            cursor.close()
            con.close()

class TemperatureIotDao:
    @staticmethod
    def getAllTemp():
        try:
            con = Database.getConnection()
            cursor = con.cursor()
            cursor.execute('SELECT * FROM TemperatureIot')
            return cursor.fetchall()
        except Error as e:
            print("Error while fetching data from TemperatureIot table:", e)
            return None
        finally:
            if con:
                con.close()

    @staticmethod
    def add(device):
        try:
            con = Database.getConnection()
            cursor = con.cursor()
            query = "INSERT INTO TemperatureIot (mac, temp, datetime) VALUES (%s, %s, %s)"
            data = (device.mac, device.temp, device.datetime)
            cursor.execute(query, data)
            con.commit()
            return True
        except Error as e:
            print("Error while adding data to TemperatureIot table:", e)
            return False
        finally:
            if con:
                con.close()
class PcDao:
    def __init__(self, id, user_id, adressIp, memoryUsage, processeurUsage, usageDisque, date_time):
        self.id = id
        self.user_id = user_id
        self.adressIp = adressIp
        self.memoryUsage = memoryUsage
        self.processeurUsage = processeurUsage
        self.usageDisque = usageDisque
        self.date_time = date_time
    @staticmethod
    def get_all():
        con = Database.getConnection()
        cursor = con.cursor()
        
        try:
            cursor.execute('SELECT * FROM Pc')
            return cursor.fetchall()
        except my.Error as e:
            print(f"Error retrieving PCs: {e}")
        finally:
            cursor.close()

    @staticmethod
    def add(pc):
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            query = "INSERT INTO Pc (user_id, adressIp, memoryUsage, processeurUsage, usageDisque) VALUES (%s, %s, %s, %s, %s)"
            values = (pc.user_id, pc.adressIp, pc.memoryUsage, pc.processeurUsage, pc.usageDisque)

            cursor.execute(query, values)
            con.commit()

            print(f"PC with IP {pc.adressIp} added successfully.")
        except my.Error as e:
            con.rollback()
            print(f"Error adding PC: {e}")
        finally:
            cursor.close()

    @staticmethod
    def delete_by_userId(user_id):
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            query = "DELETE FROM Pc WHERE user_id = %s"
            value = (user_id,)

            cursor.execute(query, value)
            con.commit()

            print(f"PC records for user {user_id} deleted successfully.")
        except my.Error as e:
            con.rollback()
            print(f"Error deleting PC records: {e}")
        finally:
            cursor.close()


    @staticmethod
    def get_pc_data_by_user_id(user_id):
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            query = "SELECT * FROM Pc WHERE user_id = %s"
            value = (user_id,)
            cursor.execute(query, value)
            pc_data = cursor.fetchall()

            pcs = []
            for data in pc_data:
                pc = PcDao(*data)
                pcs.append(pc)

            return pcs
        except my.Error as e:
            print(f"Error retrieving PC data for user {user_id}: {e}")
            return None
        finally:
            cursor.close()
            con.close()

class VilleDao:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
    @staticmethod
    def add_city(city_name):
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            query = "INSERT INTO ville (name) VALUES (%s)"
            values = (city_name,)

            cursor.execute(query, values)
            con.commit()

            print(f"City {city_name} added successfully.")
        except my.Error as e:
            con.rollback()
            print(f"Error adding city: {e}")
        finally:
            cursor.close()

    @staticmethod
    def get_all_cities():
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            query = "SELECT id, name FROM ville"
            cursor.execute(query)
            results = cursor.fetchall()

            cities = []
            for result in results:
                city = VilleDao(*result)
                cities.append(city)

            return cities
        except my.Error as e:
            print(f"Error retrieving cities: {e}")
        finally:
            cursor.close()

    @staticmethod
    def delete_city(city_id):
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            query = "DELETE FROM ville WHERE id = %s"
            values = (city_id,)

            cursor.execute(query, values)
            con.commit()

            print(f"City with ID {city_id} deleted successfully.")
        except my.Error as e:
            con.rollback()
            print(f"Error deleting city: {e}")
        finally:
            cursor.close()

class WeatherDao:
    @staticmethod
    def insert(weather):
        try:
            con = Database.getConnection()
            cursor = con.cursor()

            query = """INSERT INTO weather 
                       (id_city, date, temperature, humidity, wind_speed, precipitation) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            data = (weather.id_city, weather.date, weather.temperature, 
                    weather.humidity, weather.wind_speed, weather.precipitation)
            
            cursor.execute(query, data)
            con.commit()
            print("Weather data inserted successfully")
            
        except my.Error as e:
            print(f"Error inserting weather data: {e}")
        finally:
            if con.is_connected():
                cursor.close()
                con.close()
                print("MySQL connection closed")

    @staticmethod
    def get_weather_by_city(city_id):
        try:
            con = Database.getConnection()
            cursor = con.cursor()

            query = "SELECT * FROM weather WHERE id_city = %s"
            cursor.execute(query, (city_id,))
            records = cursor.fetchall()

            return records
        except my.Error as e:
            print(f"Error fetching weather data: {e}")
        finally:
            if con.is_connected():
                cursor.close()
                con.close()
                print("MySQL connection closed")
class UserDao:
    def __init__(self, user_id, username, email, password, isAdmin=False):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.isAdmin = isAdmin

    @staticmethod
    def create(username, email, password, is_admin=False):
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            query = "INSERT INTO User (username, email, password, isAdmin) VALUES (%s, %s, %s, %s)"
            values = (username, password, email, is_admin)

            cursor.execute(query, values)
            con.commit()

            print(f"User {username} created successfully.")
            
            # Fetch the last inserted user_id
            user_id = cursor.lastrowid

            return user_id
        except my.Error as e:
            con.rollback()
            print(f"Error creating user: {e}")
        finally:
            cursor.close()

    @staticmethod
    def get_all_users():
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            query = "SELECT * FROM User"
            cursor.execute(query)
            results = cursor.fetchall()

            users = []
            for result in results:
                user = UserDao(*result)
                users.append(user)

            return users
        except my.Error as e:
            print(f"Error reading users: {e}")
            return None
        finally:
            cursor.close()
            con.close()

    @staticmethod
    def read(email):
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            query = "SELECT * FROM User"
            value = (user_id,)

            cursor.execute(query, value)
            result = cursor.fetchone()

            if result:
                user = UserDao(*result)
                return user
            else:
                return None
        except my.Error as e:
            print(f"Error reading user: {e}")
        finally:
            cursor.close()

    def update(self, new_username, new_password):
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            query = "UPDATE User SET username = %s, password = %s WHERE user_id = %s"
            values = (new_username, new_password, self.user_id)

            cursor.execute(query, values)
            con.commit()

            print(f"User {self.username} updated successfully.")
        except my.Error as e:
            con.rollback()
            print(f"Error updating user: {e}")
        finally:
            cursor.close()

    @staticmethod
    def get_user_id_by_username(username):
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            query = "SELECT id FROM User WHERE username LIKE %s"  # Corrected query
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result:
                return result[0]  # Return the user ID
            else:
                return None  # User not found
        except my.Error as e:
            print(f"Error reading users: {e}")
            return None
        finally:
            cursor.close()
            con.close()

    @staticmethod
    def delete(username):
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            # Get the user ID first
            user_id = UserDao.get_user_id_by_username(username)  # Retrieve user ID

            print(user_id)

            # If user ID is found, proceed with deletion
            if user_id:
                print(user_id)
                # Delete PC records associated with the user
                PcDao.delete_by_userId(user_id)

                # Now delete the user
                query = "DELETE FROM User WHERE username like '%s'"
                value = (username,)

                cursor.execute(query, value)
                con.commit()

                print(f"User {username} deleted successfully.")
            else:
                print(f"User {username} not found.")
        except my.Error as e:
            con.rollback()
            print(f"Error deleting user: {e}")
        finally:
            cursor.close()
            con.close()

    @staticmethod
    def login(email):
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            query = "SELECT * FROM User where email like %s";
            values = (email,)

            cursor.execute(query, values)
            result = cursor.fetchone()

            if result:
                user = UserDao(*result)
                print(f"Login successful. Welcome, {user.email}!")
                return user
            else:
                print("Invalid email or password.")
                return None
        except my.Error as e:
            print(f"Error during login: {e}")
        finally:
            cursor.close()

    def get_id(self):
        return self.user_id

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_email(self):
        return self.email

    def is_active(self):
        return self.is_active

    def is_admin(self):
        return self.isAdmin

class TemperatureIotDao:
    def __init__(self, id=None, mac=None, temp=None, datetime=None):
        self.id = id
        self.mac = mac
        self.temp = temp
        self.datetime = datetime
    @staticmethod
    def get_temperatures_by_mac(mac):
        con = Database.getConnection()
        cursor = con.cursor()

        try:
            query = "SELECT * FROM TemperatureIot WHERE mac = %s"
            cursor.execute(query, (mac,))
            results = cursor.fetchall()

            temperatures = []
            for result in results:
                temperature = TemperatureIotDao(*result)
                temperatures.append(temperature)

            return temperatures
        except my.Error as e:
            print(f"Error reading temperatures for MAC {mac}: {e}")
            return None
        finally:
            cursor.close()
            con.close()

    @staticmethod
    def add_temperature(device):
        try:
            con = Database.getConnection()
            cursor = con.cursor()
            query = "INSERT INTO TemperatureIot (mac, temp, datetime) VALUES (%s, %s, %s)"
            data = (device.mac, device.temp, device.datetime)
            cursor.execute(query, data)
            con.commit()
            return True
        except Error as e:
            print("Error while adding data to TemperatureIot table:", e)
            return False
        finally:
            if con:
                con.close()