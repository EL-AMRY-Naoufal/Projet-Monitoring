from flask import (
    Flask, render_template, request, redirect, url_for, flash, send_file, session
)
from dal import (IotDao, UserDao, PcDao, WeatherDao, VilleDao, TemperatureIotDao)
from models import(Pc, Weather, User, Iot, TemperatureIot)
import matplotlib
import requests
from matplotlib import pyplot as plt
from io import BytesIO
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from snmp import SNMPMonitor
from datetime import datetime
import base64
from flask_bcrypt import Bcrypt
from apscheduler.schedulers.background import BackgroundScheduler
from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity,nextCmd
from flask import jsonify
import json
from flask_mqtt import Mqtt


from random import uniform
import threading
import time

app=Flask(__name__)
matplotlib.use('agg')
app.config['SECRET_KEY'] = 'azeqsdqsdsq'  # Change this to a secure secret key
app.config['JWT_SECRET_KEY'] = 'qsdffdgbb'
jwt = JWTManager(app)

bcrypt = Bcrypt(app)


mqtt = Mqtt(app)

app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_REFRESH_TIME'] = 1.0

mqtt.init_app(app)


@app.route("/disk/usage", methods=["GET"])
def get_disk_usage():
    oid = "1.3.6.1.2.1.25.2.3.1.6"
    result = walk_snmp_data(ip_target, oid)
    if result:
        return jsonify({"Disk Usage": [int(varBind[1]) for varBind in result]})
    else:
        return jsonify({"Error": "Failed to retrieve disk usage"}), 500



################################## user pc info in real time ################################

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(add_pc_info, 'interval', seconds=4, args=[session['isConnected'], session['id']])

def add_pc_info(is_connected, id):
    print(is_connected)
    if is_connected:
        target_ip = '127.0.0.1'
        community_string = 'public'

        snmp_monitor = SNMPMonitor(target_ip, community_string)

        memory_usage = snmp_monitor.get_memory_usage()
        cpu_load = 0.0;
        disk_space = snmp_monitor.get_disk_space()

        adressIp = snmp_monitor.get_adressIp()

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(memory_usage)

        pc = Pc(id, adressIp, memory_usage, cpu_load, disk_space, current_datetime)
        PcDao.add(pc)

###############################################################################################

########################################## login ################################################

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('logemail')
    password = request.form.get('logpass')
    print(f'{email}    {password}')

    user = UserDao.login(email)
    if user:
        if not bcrypt.check_password_hash(user.get_password(), password):
            flash('Invalid credentials. Please try again.', 'error')
            return render_template('login.html')

        session['id'] = user.get_id()
        session['isConnected'] = True
        access_token = create_access_token(identity=email)

        if user.is_admin() == False:
            response = redirect(url_for('weather'))
        else :
            response = redirect(url_for('adminUI'))
        response.headers['Authorization'] = f'Bearer {access_token}'
        response.set_cookie('access_token', access_token)
        start_scheduler()
        return response
    else:
        flash('Invalid credentials. Please try again.', 'error')
        return render_template('login.html')

@app.route('/createAccount', methods=['POST'])
def createAccount():
    username = request.form.get('signame')
    email = request.form.get('sigemail')
    password = request.form.get('sigpass')
    hashedPassword = bcrypt.generate_password_hash(password)
    user_id = UserDao.create(username, hashedPassword, email)
    if user_id:

        target_ip = '127.0.0.1'
        community_string = 'public'

        snmp_monitor = SNMPMonitor(target_ip, community_string)

        memory_usage = snmp_monitor.get_memory_usage()
        # cpu_load = snmp_monitor.get_cpu_load()
        cpu_load = 0.0;
        disk_space = snmp_monitor.get_disk_space()

        adressIp = snmp_monitor.get_adressIp()

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        pc = Pc(user_id, adressIp, memory_usage, cpu_load, disk_space, current_datetime)
        PcDao.add(pc)

        flash('Account created successfully.', 'success')
        return render_template('login.html')
    else:
        flash('Failed to create account. Please try again.', 'error')
        return render_template('login.html')


#########################################################################################################################

################################################# Admin User Controller #################################################

@app.route('/adminUI', methods=["GET"])
def adminUI():
    cities = VilleDao.get_all_cities()

    weather_data = []

    for city in cities:
        r = get_weather_data(city.name)
        weather = {
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
            'humidity': r['main']['humidity'],
            'wind_speed': r['wind']['speed'],
            'precipitation': r['clouds']['all']
        }
        weather_data.append(weather)
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        weatherDb = Weather(city.id, current_datetime, weather['temperature'], weather['humidity'], weather['wind_speed'], weather['precipitation'])
        WeatherDao.insert(weatherDb)
    return render_template('site.html', weather_data=weather_data)

#########################################################################################################################


################################################# weather Controller ####################################################

def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=b21a2633ddaac750a77524f91fe104e7"
    r = requests.get(url).json()
    return r

@app.route('/weather', methods=["GET"])
def weather():
    cities = VilleDao.get_all_cities()

    weather_data = []

    for city in cities:
        r = get_weather_data(city.name)
        weather = {
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
            'humidity': r['main']['humidity'],
            'wind_speed': r['wind']['speed'],
            'precipitation': r['clouds']['all']
        }
        weather_data.append(weather)
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        weatherDb = Weather(city.id, current_datetime, weather['temperature'], weather['humidity'], weather['wind_speed'], weather['precipitation'])
        WeatherDao.insert(weatherDb)
    return render_template('weatherCard.html', weather_data=weather_data)

@app.route('/getVilles', methods=["GET"])
def get_all_ville():
    try:
        villes = VilleDao.get_all_cities()

        if villes:
            return render_template('listVilles.html', villes=villes)
        else:
            return render_template('listVilles.html', message="No villes found")
    except Exception as e:
        return render_template('listVilles.html', message=f"Error: {str(e)}")

@app.route('/visualize_weather/<city_id>')
def visualize_weather(city_id):
    weather_data = WeatherDao.get_weather_by_city(city_id)

    weather_dates = [entry[2] for entry in weather_data]  # Assuming date is at index 2
    temperature = [entry[3] for entry in weather_data]  # Temperature at index 3
    humidity = [entry[4] for entry in weather_data]  # Humidity at index 4
    wind_speed = [entry[5] for entry in weather_data]  # Wind speed at index 5
    precipitation = [entry[6] for entry in weather_data]  # Precipitation at index 6

    plt.figure(figsize=(10, 6))
    plt.plot(weather_dates, temperature, label='Temperature')
    plt.plot(weather_dates, humidity, label='Humidity')
    plt.plot(weather_dates, wind_speed, label='Wind Speed')
    plt.plot(weather_dates, precipitation, label='Precipitation')
    plt.xlabel('Date and Time')
    plt.ylabel('Value')
    plt.title('Weather Data Over Time')
    plt.legend()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)

    img_data = base64.b64encode(img_buffer.getvalue()).decode()

    return render_template('weatherStats.html', image=img_data)

@app.route('/addCity', methods=["GET", "POST"])
def addVille():
    return render_template('addVille.html')

@app.route('/addCityUI', methods=["GET", "POST"])
def add_ville():
    username = request.form.get('username')

    city_id = VilleDao.add_city(username)
    
    return redirect(url_for('adminUI'))


#########################################################################################################################

####################################### Normal User Controller ####################################



from flask import render_template

@app.route('/getUsers', methods=["GET"])
def get_all_users():
    try:
        users = UserDao.get_all_users()

        if users:
            for i in users:
                print('sdsssss' + i.email)
            return render_template('listDevices.html', users=users)
        else:
            return render_template('listDevices.html', message="No users found")
    except Exception as e:

        return render_template('listDevices.html', message=f"Error: {str(e)}")

@app.route('/createUser', methods=["GET", "POST"])
def createUser():
    return render_template('createUser.html')

@app.route('/createUserUI', methods=["GET", "POST"])
def create_user():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    hashedPassword = bcrypt.generate_password_hash(password)
    user_id = UserDao.create(username, email, hashedPassword)

    if user_id:
        return redirect(url_for('adminUI'))
    else:
        flash('Failed to create user. Please try again.', 'error')
        return redirect(url_for('adminUI'))

@app.route('/deleteUser', methods=["GET", "POST"])
def deleteUser():
    return render_template('deleteUser.html')

@app.route('/deleteUserUI', methods=["GET", "POST"])
def delete_user():
    username = request.form.get('username')
    user_id = UserDao.delete(username)

    if user_id:
        return redirect(url_for('adminUI'))
    else:
        flash('Failed to create user. Please try again.', 'error')
        return redirect(url_for('adminUI'))

@app.route('/visualize_user/<user_id>')
def visualize_user(user_id):
    pc_data = PcDao.get_pc_data_by_user_id(user_id)

    dates = [entry.date_time for entry in pc_data]
    memory_usage = [entry.memoryUsage for entry in pc_data]
    cpu_usage = [entry.processeurUsage for entry in pc_data]
    disk_usage = [entry.usageDisque for entry in pc_data]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, memory_usage, label='Memory Usage')
    plt.plot(dates, cpu_usage, label='CPU Usage')
    plt.plot(dates, disk_usage, label='Disk Usage')
    plt.xlabel('Date and Time')
    plt.ylabel('Usage')
    plt.title('PC Usage Over Time')
    plt.legend()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)

    img_data = base64.b64encode(img_buffer.getvalue()).decode()

    return render_template('userStats.html', image=img_data)

@app.route('/visualize_temperature/<mac_address>')
def visualize_temperature(mac_address):
    temperature_data = TemperatureIotDao.get_temperatures_by_mac(mac_address)

    if not temperature_data:
        return "No temperature data found for the specified MAC address."

    datetimes = [entry.datetime for entry in temperature_data]
    temperatures = [entry.temp for entry in temperature_data]

    plt.figure(figsize=(10, 6))
    plt.plot(datetimes, temperatures, label='Temperature')
    plt.xlabel('Datetime')
    plt.ylabel('Temperature (°C)')
    plt.title(f'Temperature Over Time for MAC: {mac_address}')
    plt.legend()

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)

    img_data = base64.b64encode(img_buffer.getvalue()).decode()

    # Render the HTML template with the base64-encoded image
    return render_template('temperatureStats.html', image=img_data)

###################################################################################################

######################################### Iot device ##############################################

@app.route('/createIot', methods=["GET", "POST"])
def createIot():
    return render_template('createIot.html')

@app.route('/createIotUI', methods=["GET", "POST"])
def create_iot():
    mac = request.form.get('mac')
    IotDao.add(mac)

    return redirect(url_for('adminUI'))


@app.route('/getIot', methods=["GET"])
def get_all_Iot():
    try:
        iots = IotDao.getAllIot()

        if iots:
            return render_template('listiot.html', iots=iots)
        else:
            return render_template('listiot.html', message="No iot found")
    except Exception as e:
        return render_template('listiot.html', message=f"Error: {str(e)}")

def send_mqtt_data(topic, data):
    json_data = json.dumps(data)
    mqtt.publish(topic, json_data)



def send_mqtt_data_periodically():
    while True:
        data = {
            "temperature": round(uniform(20.0, 30.0), 2)
        }

        mac = IotDao.get_random_mac_from_db()
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        temperature = TemperatureIot(mac, data['temperature'], current_datetime)
        TemperatureIotDao.add_temperature(temperature)
        send_mqtt_data("ambient_data", data)
        time.sleep(5)  



mqtt_thread = threading.Thread(target=send_mqtt_data_periodically)
mqtt_thread.daemon = True
mqtt_thread.start()

###################################################################################################


@app.route('/visualize')
def visualise():
    figure=plt.figure()
    data=IotDao.getAllTemp()
    temp=[]
    dates=[]
    for id,mac,t,date in data:
        temp.append(t)
        dates.append(date)
    plt.plot(dates,temp)
    img=BytesIO()
    figure.savefig(img)
    img.seek(0)
    return send_file(img,mimetype='image/png')

