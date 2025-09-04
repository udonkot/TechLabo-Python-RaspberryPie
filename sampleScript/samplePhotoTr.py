# import gpiozero
import spidev
import time

# VREF = 3.3  # MCP3208の参照電圧
# Rx = 1000  # フォトトランジスタの抵抗値 (10kΩ)

# #MCP3208
# acd = gpiozero.MCP3208(device=0, channel=0)  # MCP3208のチャンネル0を使用

# while True:
#     # フォトトランジスタの値を取得
#     print("raw_value:", acd.raw_value)  # MCP3008の生データを表示
#     light_level = acd.raw_value
#     volt = light_level / 4096.0 * VREF  # 3.3Vの範囲にスケーリング
#     current = volt / Rx
#     u_current = current * ( 10 ** 6)
#     illumi = 20 / 9 * u_current
#     print("Illuminance:{:.2f}lx Current:{:.2f}uA".format(illumi, u_current))
#     time.sleep(0.5)  # 0.5秒待機

# SPI設定
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0
spi.max_speed_hz = 1350000

# 定数
VREF = 3.3  # MCP3208の基準電圧 (3.3V)
RESOLUTION = 4096  # MCP3208は12ビットADC (2^12 = 4096)
RX = 10000  # フォトトランジスタの負荷抵抗 (10kΩ)

def read_adc(channel):
    """MCP3208から指定したチャンネルのデータを取得"""
    if channel < 0 or channel > 7:
        raise ValueError("チャンネルは0から7の間で指定してください")
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 15) << 8) + adc[2]  # MCP3208は12ビットデータ
    return data

def calculate_voltage(adc_value):
    """ADC値を電圧に変換"""
    return (adc_value * VREF) / RESOLUTION

def calculate_current(voltage):
    """電圧を電流に変換 (単位: μA)"""
    current = voltage / RX  # 電流 (A)
    return current * 1e6  # μAに変換

def calculate_illuminance(current_uA):
    """電流を照度に変換 (単位: lx)"""
    return (20 / 9) * current_uA

def main():
    try:
        print("フォトトランジスタのデータ取得を開始します (Ctrl+Cで終了)")
        while True:
            # チャンネル0からデータを取得
            adc_value = read_adc(0)
            voltage = calculate_voltage(adc_value)
            current_uA = calculate_current(voltage)
            illuminance = calculate_illuminance(current_uA)

            # 結果を表示
            print(f"ADC値: {adc_value}, 電圧: {voltage:.3f}V, 電流: {current_uA:.3f}μA, 照度: {illuminance:.3f}lx")
            time.sleep(0.5)  # 0.5秒待機

    except KeyboardInterrupt:
        print("終了します")
    finally:
        spi.close()

if __name__ == "__main__":
    main()