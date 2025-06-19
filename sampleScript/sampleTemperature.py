import spidev
import time

# SPI設定
SPI_BUS = 0
SPI_DEVICE = 0
spi = spidev.SpiDev()
spi.open(SPI_BUS, SPI_DEVICE)
spi.max_speed_hz = 1350000

# MCP3208のチャンネル設定
TEMP_SENSOR_CHANNEL = 0  # 温度センサーが接続されているチャンネル

def read_adc(channel):
    """MCP3208から指定したチャンネルの値を読み取る"""
    if channel < 0 or channel > 7:
        raise ValueError("チャンネルは0から7の間で指定してください")
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def convert_to_temperature(adc_value):
    """ADC値を温度に変換 (LM60BIZを想定)"""
    voltage = (adc_value * 3.3) / 4096  # MCP3208は12ビットADC
    temperature = (voltage - 0.424) / 0.00625  # LM60BIZの仕様に基づく計算
    return temperature

try:
    while True:
        adc_value = read_adc(TEMP_SENSOR_CHANNEL)
        temperature = convert_to_temperature(adc_value)
        print(f"温度: {temperature:.2f}°C")
        time.sleep(1)
except KeyboardInterrupt:
    print("終了します")
finally:
    spi.close()