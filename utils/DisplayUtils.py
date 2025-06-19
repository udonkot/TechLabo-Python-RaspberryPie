import smbus
import time

class DisplayUtils:

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

    def __init__(self):
        pass

    def lcd_write(self, bits, mode):
        # bits: 送信するデータ
        # mode: LCD_CMD (コマンド) または LCD_CHR (データ)
        bits_high = mode | (bits & 0xF0) | self.LCD_BACKLIGHT
        bits_low = mode | ((bits << 4) & 0xF0) | self.LCD_BACKLIGHT

        # 高位ビットを送信
        self.bus.write_byte(self.I2C_ADDR, bits_high)
        self.lcd_toggle_enable(bits_high)

        # 低位ビットを送信
        self.bus.write_byte(self.I2C_ADDR, bits_low)
        self.lcd_toggle_enable(bits_low)


    # @staticmethod
    # def display_message(message: str):
    #     print(f"Message: {message}")

    # @staticmethod
    # def display_error(error_message: str):
    #     print(f"Error: {error_message}")

    # @staticmethod
    # def display_warning(warning_message: str):
    #     print(f"Warning: {warning_message}")


    def lcd_init(self):
        self.lcd_write(0x33, self.LCD_CMD)  # Initialize the LCD
        self.lcd_write(0x32, self.LCD_CMD)  # Set to 4-bit mode
        self.lcd_write(0x06, self.LCD_CMD)  
        self.lcd_write(0x0C, self.LCD_CMD)  # Display on, cursor off
        self.lcd_write(0x28, self.LCD_CMD)  # Function set: 2 lines, 5x8 dots
        self.lcd_write(0x01, self.LCD_CMD)  # Clear display
        time.sleep(0.0005)

    def lcd_toggle_enable(self, bits):
        time.sleep(self.E_DELAY)
        self.bus.write_byte(self.I2C_ADDR, (bits | self.ENABLE))
        time.sleep(self.E_PULSE)
        self.bus.write_byte(self.I2C_ADDR, (bits & ~self.ENABLE))
        time.sleep(self.E_DELAY)

    def lcd_message(self, message, line):
        message = message.ljust(16, " ")  # Pad message to 16 characters

        message = message.encode('shift_jis', errors='ignore')
        self.lcd_write(line, self.LCD_CMD)

        for char in message:
            self.lcd_write(char, self.LCD_CHR)  # Send character to display
    
    def lcd_clear(self):
        self.lcd_write(0x01, self.LCD_CMD)

    # lcd_init()

    # # set_contrast(bus, 0x27, 128)
    # try:
    #     while True:
    #         lcd_message("Hello, World!", LCD_LINE_1)
    #         lcd_message("12345678901234567", LCD_LINE_2) # 16文字表示,17文字以降は表示されない
    #         # アスキーアートのショボン表示
    #         # 表示できない記号は変換
    #         time.sleep(2)
    #         lcd_message("ﾌﾟｷﾞｬｰwwww", LCD_LINE_1)
    #         lcd_message("(^w^)(^w^)(^w^)", LCD_LINE_2)
    #         time.sleep(2)

    # except KeyboardInterrupt:
    #     # 強制終了時はディスプレイクリア
    #     lcd_write(0x01, LCD_CMD)  # Clear display
    #     pass
