#!/usr/bin/env python3
"""
LCD 1602 (I2C) テストスクリプト
接続確認と基本動作テスト
"""

import pigpio
import time
import subprocess

class LCD1602Test:
    """LCD 1602テストクラス"""
    
    # LCD設定
    LCD_WIDTH = 16
    LCD_CHR = 1
    LCD_CMD = 0
    LCD_LINE_1 = 0x80
    LCD_LINE_2 = 0xC0
    LCD_BACKLIGHT = 0x08
    ENABLE = 0b00000100
    
    def __init__(self, address=0x27):
        """初期化"""
        self.address = address
        self.pi = None
        self.handle = None
        
    def connect(self):
        """接続"""
        try:
            # pigpioに接続
            self.pi = pigpio.pi()
            if not self.pi.connected:
                print("❌ pigpioデーモンに接続できません")
                print("   sudo pigpiod を実行してください")
                return False
            
            # I2Cハンドルを開く
            self.handle = self.pi.i2c_open(1, self.address)
            print(f"✅ LCD接続成功 (アドレス: 0x{self.address:02X})")
            return True
            
        except Exception as e:
            print(f"❌ LCD接続失敗: {e}")
            return False
    
    def init_lcd(self):
        """LCD初期化"""
        try:
            self._lcd_byte(0x33, self.LCD_CMD)
            self._lcd_byte(0x32, self.LCD_CMD)
            self._lcd_byte(0x06, self.LCD_CMD)
            self._lcd_byte(0x0C, self.LCD_CMD)
            self._lcd_byte(0x28, self.LCD_CMD)
            self._lcd_byte(0x01, self.LCD_CMD)
            time.sleep(0.005)
            print("✅ LCD初期化完了")
            return True
        except Exception as e:
            print(f"❌ LCD初期化失敗: {e}")
            return False
    
    def _lcd_byte(self, bits, mode):
        """1バイト送信"""
        bits_high = mode | (bits & 0xF0) | self.LCD_BACKLIGHT
        bits_low = mode | ((bits << 4) & 0xF0) | self.LCD_BACKLIGHT
        
        self.pi.i2c_write_byte(self.handle, bits_high)
        self._lcd_toggle_enable(bits_high)
        
        self.pi.i2c_write_byte(self.handle, bits_low)
        self._lcd_toggle_enable(bits_low)
    
    def _lcd_toggle_enable(self, bits):
        """Enableピントグル"""
        time.sleep(0.0005)
        self.pi.i2c_write_byte(self.handle, (bits | self.ENABLE))
        time.sleep(0.0005)
        self.pi.i2c_write_byte(self.handle, (bits & ~self.ENABLE))
        time.sleep(0.0005)
    
    def display_text(self, line1, line2=""):
        """テキスト表示"""
        self._lcd_string(line1, self.LCD_LINE_1)
        self._lcd_string(line2, self.LCD_LINE_2)
    
    def display_pattern(self, pattern: str):
        """パターン表示"""
        patterns = {
            'startup': ("startup...", ""),
            'ready': ("ready ok", "please control"),
            'vulcan': ("shot!", "!!!!!!"),
            'konami': ("secret command!", "start！！"),
            'motion': ("motion detect!!", "fire!!")
        }
        text = patterns.get(pattern, ("", ""))
        self.display_text(text[0], text[1])

    def _lcd_string(self, message, line):
        """文字列表示"""
        self._lcd_byte(line, self.LCD_CMD)
        
        message = message.ljust(self.LCD_WIDTH, " ")[:self.LCD_WIDTH]
        
        for char in message:
            self._lcd_byte(ord(char), self.LCD_CHR)
    
    def clear(self):
        """画面クリア"""
        self._lcd_byte(0x01, self.LCD_CMD)
        time.sleep(0.002)
    
    def test_backlight(self):
        """バックライトテスト"""
        print("\n📍 バックライトテスト")
        
        for i in range(3):
            print(f"   バックライト OFF")
            self.pi.i2c_write_byte(self.handle, 0x00)
            time.sleep(0.5)
            
            print(f"   バックライト ON")
            self.pi.i2c_write_byte(self.handle, self.LCD_BACKLIGHT)
            time.sleep(0.5)
    
    def test_display(self):
        """表示テスト"""
        print("\n📍 表示テスト")
        
        tests = [
            ("Hello, World!", "LCD 1602 Test"),
            ("Raspberry Pi 4", "Gundam Robot"),
            ("1234567890123456", "ABCDEFGHIJKLMNOP"),
            ("日本語テスト", "カタカナ表示"),
        ]
        
        for line1, line2 in tests:
            print(f"   表示: '{line1}' / '{line2}'")
            self.display_text(line1, line2)
            time.sleep(2)
    
    def test_scroll(self):
        """スクロールテスト"""
        print("\n📍 スクロールテスト")
        
        long_text = "This is a long text that needs scrolling... "
        for i in range(len(long_text)):
            display = long_text[i:i+16]
            if len(display) < 16:
                display = display + long_text[0:16-len(display)]
            self._lcd_string(display, self.LCD_LINE_1)
            self._lcd_string("Scrolling Test", self.LCD_LINE_2)
            time.sleep(0.2)
    
    def cleanup(self):
        """クリーンアップ"""
        if self.handle:
            self.clear()
            self.pi.i2c_close(self.handle)
        if self.pi:
            self.pi.stop()

def scan_i2c_devices():
    """I2Cデバイスをスキャン"""
    print("\n🔍 I2Cデバイスをスキャン中...")
    
    try:
        result = subprocess.run(['i2cdetect', '-y', '1'], 
                              capture_output=True, 
                              text=True)
        print(result.stdout)
        
        if "27" in result.stdout:
            print("✅ アドレス 0x27 にデバイスを検出")
            return 0x27
        elif "3c" in result.stdout:
            print("✅ アドレス 0x3C にデバイスを検出")
            return 0x3C
        else:
            print("❌ I2Cデバイスが見つかりません")
            print("\n接続を確認してください:")
            print("  VCC -> 5V")
            print("  GND -> GND")
            print("  SDA -> GPIO2 (ピン3)")
            print("  SCL -> GPIO3 (ピン5)")
            return None
            
    except FileNotFoundError:
        print("❌ i2cdetect コマンドが見つかりません")
        print("   sudo apt install i2c-tools")
        return None
    except subprocess.CalledProcessError as e:
        print(f"❌ I2Cスキャンエラー: {e}")
        print("\nI2Cを有効にしてください:")
        print("  sudo raspi-config")
        print("  -> Interface Options -> I2C -> Yes")
        return None

def main():
    """メイン処理"""
    print("="*50)
    print("LCD 1602 (I2C) テストプログラム")
    print("="*50)
    
    # pigpiodの確認
    try:
        result = subprocess.run(['pgrep', 'pigpiod'], 
                              capture_output=True, 
                              text=True)
        if not result.stdout:
            print("\n⚠️  pigpiodが起動していません")
            print("起動しています...")
            subprocess.run(['sudo', 'pigpiod'])
            time.sleep(1)
    except:
        pass
    
    # I2Cデバイススキャン
    detected_address = scan_i2c_devices()
    
    if detected_address is None:
        print("\nデフォルトアドレス 0x27 で試行します...")
        detected_address = 0x27
    
    # LCDテスト開始
    lcd = LCD1602Test(detected_address)
    
    try:
        # 接続
        if not lcd.connect():
            print("\n別のアドレスを試してください:")
            print("  0x27 (標準)")
            print("  0x3F (代替)")
            print("  0x20 (PCF8574)")
            print("  0x38 (PCF8574A)")
            return
        
        # 初期化
        if not lcd.init_lcd():
            return
        
        # 各種テスト実行
        print("\n🚀 テスト開始")
        print("-"*30)
        
        # バックライトテスト
        lcd.test_backlight()
        
        # 表示テスト
        lcd.test_display()
        
        # スクロールテスト
        lcd.test_scroll()
        
        # 完了メッセージ
        lcd.clear()
        lcd.display_text("Test Complete!", "All OK!")
        
        print("\n✅ 全テスト完了")
        
    except KeyboardInterrupt:
        print("\n\n中断されました")
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        
    finally:
        lcd.cleanup()
        print("\nクリーンアップ完了")

if __name__ == "__main__":
    main()