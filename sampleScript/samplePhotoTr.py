import gpiozero
import time

VREF = 3.3  # MCP3208の参照電圧
Rx = 1000  # フォトトランジスタの抵抗値 (10kΩ)

#MCP3208
acd = gpiozero.MCP3208(device=0, channel=0)  # MCP3208のチャンネル0を使用

while True:
    # フォトトランジスタの値を取得
    print("raw_value:", acd.raw_value)  # MCP3008の生データを表示
    light_level = acd.raw_value
    volt = light_level / 4096.0 * VREF  # 3.3Vの範囲にスケーリング
    current = volt / Rx
    u_current = current * ( 10 ** 6)
    illumi = 20 / 9 * u_current
    print("Illuminance:{:.2f}lx Current:{:.2f}uA".format(illumi, u_current))
    time.sleep(0.5)  # 0.5秒待機

# # SPI設定
# spi = spidev.SpiDev()
# spi.open(1, 0)  # Bus 0, Device 0
# spi.max_speed_hz = 1350000

# def read_adc(channel):
#     """MCP3008から指定したチャンネルのデータを取得"""
#     if channel < 0 or channel > 7:
#         raise ValueError("チャンネルは0から7の間で指定してください")
#     adc = spi.xfer2([1, (8 + channel) << 4, 0])
#     data = ((adc[1] & 3) << 8) + adc[2]
#     return data

# def main():
#     try:
#         print("フォトトランジスタのデータ取得を開始します (Ctrl+Cで終了)")
#         while True:
#             # チャンネル0からデータを取得
#             light_level = read_adc(0)
#             print(f"光レベル: {light_level}")
#             time.sleep(0.5)  # 0.5秒待機
#     except KeyboardInterrupt:
#         print("\n終了します")
#     finally:
#         spi.close()

# if __name__ == "__main__":
#     main()