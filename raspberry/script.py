# importamos librerias
import RPi.GPIO as GPIO
import time
import smbus
from random import randint
import mysql.connector

#Datos del cliente
ID = 12

# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address, if any error, change this address to 0x27
LCD_WIDTH = 16   # Maximum characters per line


# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line


LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

# indicamos el uso de  la identificacion BCM para los GPIO
GPIO.setmode(GPIO.BCM)
# configuramos el pin 18 como entrada y activamos 
# la resistencia de activacion del pin 18 con PUD_UP
# esto hara que al presionar el boton se interrumpe
# la tension de 3,3V del pin
GPIO.setup(18,GPIO.IN,pull_up_down=GPIO.PUD_UP)

# por defecto el estado anterior es True (encendido)
old_input_state=True # activada
new_input_state=False

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)
  lcd_string("Cliente "+str(ID),LCD_LINE_1)
  
  time.sleep(6)


def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def insert(id_c, productos, estado, date, caja, demora):
    cnx = mysql.connector.connect(user='mariana', password='vulpix97',
                              host='nomasfilas2.c5h2cytdcjx1.us-west-2.rds.amazonaws.com',
                              database='mydb')
    cursor = cnx.cursor() 
    query = ("INSERT INTO COLA "
               "(CLIENTE, PRODUCTOS, ESTADO, DATE, CAJA, DEMORA) "
               "VALUES (%s, %s, %s, %s, %s, %s)")
    data = (id_c, productos, estado, date, caja, demora)
    cursor.execute(query, data)
    cnx.commit() 
    cursor.close()
    cnx.close()

def delete(id_c):
    cnx = mysql.connector.connect(user='mariana', password='vulpix97',
                                host='nomasfilas2.c5h2cytdcjx1.us-west-2.rds.amazonaws.com',
                                database='mydb')
    cursor = cnx.cursor() 
    query = "DELETE FROM COLA WHERE ESTADO = 1 AND CLIENTE = %s"
    data = (id_c,)
    cursor.execute(query, data)
    cnx.commit() 
    cursor.close()
    cnx.close()

def change_state(new_state, old_state, id_c): 
    cnx = mysql.connector.connect(user='mariana', password='vulpix97',
                                host='nomasfilas2.c5h2cytdcjx1.us-west-2.rds.amazonaws.com',
                                database='mydb')
    cursor = cnx.cursor() 
    query = "UPDATE COLA SET ESTADO = %s WHERE ESTADO = %s AND CLIENTE = %s"
    data = (new_state, old_state, id_c)
    cursor.execute(query, data)
    cnx.commit() 
    cursor.close()
    cnx.close()

def get_caja():
    cnx = mysql.connector.connect(user='mariana', password='vulpix97',
                                host='nomasfilas2.c5h2cytdcjx1.us-west-2.rds.amazonaws.com',
                                database='mydb')
    cursor = cnx.cursor()
    query = "SELECT SUM(DEMORA), CAJA FROM COLA WHERE ESTADO = 1 OR ESTADO = 2 OR ESTADO = 3 GROUP BY CAJA ORDER BY SUM(DEMORA)"
    cursor.execute(query)
    retorno = cursor.fetchone()[1]
    cursor.fetchall()
        
    cursor.close()
    cnx.close()
    return retorno

def get_estado(id_c):
    cnx = mysql.connector.connect(user='mariana', password='vulpix97',
                                host='nomasfilas2.c5h2cytdcjx1.us-west-2.rds.amazonaws.com',
                                database='mydb')
    cursor = cnx.cursor()
    query = "SELECT ESTADO FROM COLA WHERE CLIENTE = %s AND (ESTADO = 1 OR ESTADO = 2 OR ESTADO = 3) "
    cursor.execute(query, (id_c,))
    retorno = cursor.fetchone()[0]
    cursor.close()
    cnx.close()
    return retorno

def main():
  # Main program block
  PRODUCTOS = 0
  CAJA = 0
  ESTADO = 0 # 1 ES EN ESPERA, 2 ES PROXI
  DATE = 0.0
  TIEMPO = 7 # Tiempo de espera en minutos
  # Initialise display
  lcd_init()
  new_input_state=False

  while True:       

    # guardo en una variable el estado del pin
    #new_input_state=GPIO.input(18)
    
    # si el estado es False (presionado),y el estado
    # anterior es True cambiamos el valor del switch
    if (ESTADO==0 or ESTADO==1) and new_input_state==False :
        if ESTADO==1:
            #Aqui se cancela el turno en base de datos y se coge el nuevo
            delete(ID)
            lcd_string("Asignando turno...         ",LCD_LINE_1)
            PRODUCTOS = randint(0, 50)
            DATE = time.time()
            CAJA = get_caja()
            DEMORA = 2 + PRODUCTOS/5
            insert(ID, PRODUCTOS, ESTADO, DATE, CAJA, DEMORA)
            #Imprimimos el estado de la reserva
            lcd_string("Cliente "+str(ID)+" Caja "+str(CAJA),LCD_LINE_1)
            lcd_string("Espera: "+str(TIEMPO) +" min",LCD_LINE_2)
        elif ESTADO==0:
            #Aqui se coge el turno 
            lcd_string("Asignando turno...         ",LCD_LINE_1)
            PRODUCTOS = randint(0, 50)
            DATE = time.time()
            CAJA = get_caja()
            DEMORA = 2 + PRODUCTOS/5
            ESTADO=1
            TIEMPO=TIEMPO+DEMORA
            insert(ID, PRODUCTOS, ESTADO, DATE, CAJA, DEMORA)
            #Imprimimos el estado de la reserva
            lcd_string("Cliente"+str(ID)+" Caja "+str(CAJA),LCD_LINE_1)
            lcd_string("Espera "+str(TIEMPO) +"min",LCD_LINE_2)
        # tiempo de demora para evitar rebote
        new_input_state=True
        
    if ESTADO==1 or ESTADO==2:
        #Sacar si ya soy el proximo
        if get_estado(ID)==2:
            ESTADO=2
            lcd_string("Vaya a la caja",LCD_LINE_2)

        #Sacar si ya es mi turno
        if get_estado(ID)==3:
            for i in range(30):
                lcd_string("Quedan "+str(30-i)+" s",LCD_LINE_2)
                time.sleep(1)
            lcd_string("Cliente "+str(ID),LCD_LINE_1)
            lcd_string("                               ",LCD_LINE_2)
            ESTADO=0   
        
    # guardamos el estado actual del GPIO18
    old_input_state=new_input_state

    time.sleep(0.5)

if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
