import smbus2, time
from so1602 import so1602

SO1602_ADDR = 0x27
I2C_CH = 1

i2c = smbus2.SMBus( I2C_CH  )

oled = so1602( i2c, SO1602_ADDR )

oled.clear()          # ディスプレイをクリア
oled.move_home()      # カーソルをホーム位置に移動
oled.write('Hello')   # 文字を表示

# oled.set_cursol( 0 )
# oled.set_blink( 0 )

# oled.set_cursol( 1 )
# oled.set_blink( 1 )


# 文字を表示
# oled.move_home()
# oled.put_string("hoge")

# oled.move( 0x02, 0x01 )
# oled.write( "Raspberry Pi" )

