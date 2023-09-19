import network
from time import sleep
from machine import Pin,I2C,ADC
from umqtt.simple import MQTTClient
import os

# Fill in your WiFi network name (ssid) and password here:
wifi_ssid = os.getenv(WIFI_SSID)
wifi_password = os.getenv(WIFI_PASSWORD)

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    sleep(1)
print("Connected to WiFi")

# Fill in your Adafruit IO Authentication and Feed MQTT Topic details
mqtt_host = os.getenv(mqtt_host)
mqtt_username = os.getenv(mqtt_username)  # Your Adafruit IO username
mqtt_password = os.getenv(mqtt_password)  # Adafruit IO Key

# The MQTT topic for your Adafruit IO Feed
mqtt_publish_topic1 = "(Your adafruit username)/feeds/temperature"
mqtt_publish_topic2 = "(Your adafruit username)/feeds/ph"
mqtt_publish_topic3 = "(Your adafruit username)/feeds/Nutrient Concentration"
# Enter a random ID for this MQTT Client
# It needs to be globally unique across all of Adafruit IO.
mqtt_client_id = os.getenv(mqtt_client_id)

# Initialize our MQTTClient and connect to the MQTT server
mqtt_client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        user=mqtt_username,
        password=mqtt_password)

mqtt_client.connect()

counter = 0

# Initialize the analog Temperature
temp_val = machine.ADC(26)

# Define ADC pin for water concentartion
nutrient_val = ADC(Pin(27))  # Use the second GPIO27 as ADC pin

# Define ADC pin for pH
pH_val = ADC(Pin(28))
# Set up LED for indicating moisture level
led_BUILTIN = Pin("LED",Pin.OUT)

try:
    while True:
        # Read the voltage from the potentiometer
        temperature = temp_val.read_u16()/ 65535.0 * 100  # Convert to voltage (Scaling to 100*C simulation)
        print(f"Voltage: {temperature}*C")
        sleep(2)
        
        # Read the voltage from the potentiometer
        concentration = nutrient_val.read_u16()/ 65535.0 * 100  # Convert to voltage (Scaling to 100% simulation)
        print(f"Tank concentration: {concentration}%")
        sleep(2)
        
        # Read the voltage from the potentiometer
        pH = pH_val.read_u16()/ 65535.0 * 14  # Convert to voltage (Scaling to 0-14 simulation)
        print(f"pH: {pH}")
        sleep(2)
        
        
        # Soil moisture sensor's control loop
        if concentration > 50:
            led_BUILTIN.value(1)
            print(f"Concentration val: {concentration}")
            sleep(2)
        else:
            led_BUILTIN.value(0)
            print(f"Concentration val: {concentration}")
            sleep(0.5)
        
        
        # Publish data to MQTT topic
        print(f'Publish {temperature}')
        mqtt_client.publish(mqtt_publish_topic1, str(temperature))
        
        print(f'Publish {pH}')
        mqtt_client.publish(mqtt_publish_topic2, str(pH))
        
        print(f'Publish {concentration}')
        mqtt_client.publish(mqtt_publish_topic3, str(concentration))
        
        # Delay a bit to avoid hitting the rate limit set by Adafruit
        # Publish a data point to the Adafruit IO MQTT server every 3 seconds
        # Note: Adafruit IO has rate limits in place, every 3 seconds is frequent
        #  enough to see data in realtime without exceeding the rate limit.
        sleep(5)
except Exception as e:
    print(f'Failed to publish message: {e}')
finally:
    mqtt_client.disconnect()
