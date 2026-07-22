import smbus
import time

I2C_ADDR = 0x27
I2C_CH = 1

LCD_LINE_1 = 0x80  # LCD RAM address for the first line
LCD_LINE_2 = 0xC0  # LCD RAM address for the second line

LCD_CMD = 0
LCD_CHR = 1

ENABLE = 0b00000100  # Enable bit
BACKLIGHT = 0x08  # Backlight bit
LCD_BACKLIGHT = 0x08  # Backlight bit

E_PULSE = 0.0005
E_DELAY = 0.0005

bus = smbus.SMBus(I2C_CH)

def lcd_init():
    lcd_write(0x33, LCD_CMD)  # Initialize the LCD
    lcd_write(0x32, LCD_CMD)  # Set to 4-bit mode
    lcd_write(0x06, LCD_CMD)  
    lcd_write(0x0C, LCD_CMD)  # Display on, cursor off
    lcd_write(0x28, LCD_CMD)  # Function set: 2 lines, 5x8 dots
    lcd_write(0x01, LCD_CMD)  # Clear display
    time.sleep(0.0005)

    # bus.write_byte(IC2_ADDR, 0x33)  # Initialize the LCD in 4-bit mode
    # bus.write_byte(IC2_ADDR, 0x32)  # Set to 4-bit mode
    # bus.write_byte(IC2_ADDR, 0x28)  # Function set: 2 lines, 5x8 dots
    # bus.write_byte(IC2_ADDR, 0x0C)  # Display on, cursor off
    # bus.write_byte(IC2_ADDR, 0x01)  # Clear display
    # time.sleep(0.002)

def lcd_write(bits, mode):
    # bits: 送信するデータ
    # mode: LCD_CMD (コマンド) または LCD_CHR (データ)
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    # 高位ビットを送信
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    # 低位ビットを送信
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

# def lcd_write(bits, mode):
#     bus.write_byte(IC2_ADDR, mode | (bits & 0xF0) | BACKLIGHT)  # Send upper nibble
#     lcd_toggle_enable()

#     bus.write_byte(IC2_ADDR, mode | ((bits << 4) & 0xF0) | BACKLIGHT)  # Send lower nibble
#     lcd_toggle_enable()

# def lcd_toggle_enable():
#     time.sleep(E_DELAY)
#     bus.write_byte(I2C_ADDR, ENABLE | BACKLIGHT)  # Enable pulse
#     time.sleep(E_PULSE)
#     bus.write_byte(I2C_ADDR, (ENABLE | BACKLIGHT) & ~ENABLE)  # Disable pulse
#     time.sleep(E_DELAY)

def lcd_toggle_enable(bits):
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(E_DELAY)

def lcd_message(message, line):
    message = message.ljust(16, " ")  # Pad message to 16 characters

    message = message.encode('shift_jis', errors='ignore')
    lcd_write(line, LCD_CMD)

    for char in message:
        lcd_write(char, LCD_CHR)  # Send character to display
        # lcd_write(ord(char), LCD_CHR)  # Send character to display


lcd_init()

# set_contrast(bus, 0x27, 128)
try:
    while True:
        lcd_message("Hello, World!", LCD_LINE_1)
        lcd_message("12345678901234567", LCD_LINE_2) # 16文字表示,17文字以降は表示されない
        # アスキーアートのショボン表示
        # 表示できない記号は変換
        time.sleep(2)
        lcd_message("ﾌﾟｷﾞｬｰwwww", LCD_LINE_1)
        lcd_message("(^w^)(^w^)(^w^)", LCD_LINE_2)
        time.sleep(2)

except KeyboardInterrupt:
    # 強制終了時はディスプレイクリア
    lcd_write(0x01, LCD_CMD)  # Clear display
    pass
