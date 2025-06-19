import smbus2, time

class so1602:
    char_table = {
        u' ': [0x20],
        u'　': [0x20],
        u'!': [0x21],
        u'"': [0x22],
        u'#': [0x23],
        u'$': [0x24],
        u'%': [0x25],
        u'&': [0x26],
        u"'": [0x27],
        u'(': [0x28],
        u')': [0x29],
        u'*': [0x2a],
        u'+': [0x2b],
        u',': [0x2c],
        u'-': [0x2d],
        u'.': [0x2e],
        u'/': [0x2f],

        u'0': [0x30],
        u'1': [0x31],
        u'2': [0x32],
        u'3': [0x33],
        u'4': [0x34],
        u'5': [0x35],
        u'6': [0x36],
        u'7': [0x37],
        u'8': [0x38],
        u'9': [0x39],
        u':': [0x3a],
        u';': [0x3b],
        u'<': [0x3c],
        u'=': [0x3d],
        u'>': [0x3e],
        u'?': [0x3f],

        u'@': [0x40],
        u'A': [0x41],
        u'B': [0x42],
        u'C': [0x43],
        u'D': [0x44],
        u'E': [0x45],
        u'F': [0x46],
        u'G': [0x47],
        u'H': [0x48],
        u'I': [0x49],
        u'J': [0x4a],
        u'K': [0x4b],
        u'L': [0x4c],
        u'M': [0x4d],
        u'N': [0x4e],
        u'O': [0x4f],

        u'P': [0x50],
        u'Q': [0x51],
        u'R': [0x52],
        u'S': [0x53],
        u'T': [0x54],
        u'U': [0x55],
        u'V': [0x56],
        u'W': [0x57],
        u'X': [0x58],
        u'Y': [0x59],
        u'Z': [0x5a],
        u'[[': [0x5b],
        u'¥': [0x5c],
        u']]': [0x5d],
        u'^': [0x5e],
        u'_': [0x5f],

        u'`': [0x60],
        u'a': [0x61],
        u'b': [0x62],
        u'c': [0x63],
        u'd': [0x64],
        u'e': [0x65],
        u'f': [0x66],
        u'g': [0x67],
        u'h': [0x68],
        u'i': [0x69],
        u'j': [0x6a],
        u'k': [0x6b],
        u'l': [0x6c],
        u'm': [0x6d],
        u'n': [0x6e],
        u'o': [0x6f],

        u'p': [0x70],
        u'q': [0x71],
        u'r': [0x72],
        u's': [0x73],
        u't': [0x74],
        u'u': [0x75],
        u'v': [0x76],
        u'w': [0x77],
        u'x': [0x78],
        u'y': [0x79],
        u'z': [0x7a],
        u'(': [0x7b],
        u'|': [0x7c],
        u')': [0x7d],
        u'→': [0x7e],
        u'←': [0x7f],

        u'。': [0xa1],
        u'「': [0xa2],
        u'」': [0xa3],
        u'、': [0xa4],
        u'・': [0xa5],
        u'ヲ': [0xa6],
        u"ァ": [0xa7],
        u'ィ': [0xa8],
        u'ゥ': [0xa9],
        u'ェ': [0xaa],
        u'ォ': [0xab],
        u'ャ': [0xac],
        u'ュ': [0xad],
        u'ョ': [0xae],
        u'ッ': [0xaf],

        u'ー': [0xb0],
        u'ア': [0xb1],
        u'イ': [0xb2],
        u'ウ': [0xb3],
        u'エ': [0xb4],
        u'オ': [0xb5],
        u'カ': [0xb6],
        u'キ': [0xb7],
        u'ク': [0xb8],
        u'ケ': [0xb9],
        u'コ': [0xba],
        u'サ': [0xbb],
        u'シ': [0xbc],
        u'ス': [0xbd],
        u'セ': [0xbe],
        u'ソ': [0xbf],

        u'タ': [0xc0],
        u'チ': [0xc1],
        u'ツ': [0xc2],
        u'テ': [0xc3],
        u'ト': [0xc4],
        u'ナ': [0xc5],
        u'ニ': [0xc6],
        u'ヌ': [0xc7],
        u'ネ': [0xc8],
        u'ノ': [0xc9],
        u'ハ': [0xca],
        u'ヒ': [0xcb],
        u'フ': [0xcc],
        u'ヘ': [0xcd],
        u'ホ': [0xce],
        u'マ': [0xcf],

        u'ミ': [0xd0],
        u'ム': [0xd1],
        u'メ': [0xd2],
        u'モ': [0xd3],
        u'ヤ': [0xd4],
        u'ユ': [0xd5],
        u'ヨ': [0xd6],
        u'ラ': [0xd7],
        u'リ': [0xd8],
        u'ル': [0xd9],
        u'レ': [0xda],
        u'ロ': [0xdb],
        u'ワ': [0xdc],
        u'ン': [0xdd],
        u'゛': [0xde],
        u'゜': [0xdf],

        u'ガ': [0xb6, 0xde],
        u'ギ': [0xb7, 0xde],
        u'グ': [0xb8, 0xde],
        u'ゲ': [0xb9, 0xde],
        u'ゴ': [0xba, 0xde],
        u'ザ': [0xbb, 0xde],
        u'ジ': [0xbc, 0xde],
        u'ズ': [0xbd, 0xde],
        u'ゼ': [0xbe, 0xde],
        u'ゾ': [0xbf, 0xde],
        u'ダ': [0xc0, 0xde],
        u'ヂ': [0xc1, 0xde],
        u'ヅ': [0xc2, 0xde],
        u'デ': [0xc3, 0xde],
        u'ド': [0xc4, 0xde],
        u'バ': [0xca, 0xde],
        u'ビ': [0xcb, 0xde],
        u'ブ': [0xcc, 0xde],
        u'ベ': [0xcd, 0xde],
        u'ボ': [0xce, 0xde],
        u'パ': [0xca, 0xdf],
        u'ピ': [0xcb, 0xdf],
        u'プ': [0xcc, 0xdf],
        u'ペ': [0xcd, 0xdf],
        u'ポ': [0xce, 0xdf],

        u'┌': [0x09],
        u'┐': [0x0a],
        u'└': [0x0b],
        u'┘': [0x0c],
        u'®': [0x0e],
        u'©': [0x0f],

        u'™': [0x10],
        u'†': [0x11],
        u'§': [0x12],
        u'¶': [0x13],
        u'Γ': [0x14],
        u'Δ': [0x15],
        u'θ': [0x16],
        u'Λ': [0x17],
        u'Ξ': [0x18],
        u'Π': [0x19],
        u'Σ': [0x1a],
        u'γ': [0x1b],
        u'Φ': [0x1c],
        u'Ψ': [0x1d],
        u'Ω': [0x1e],
        u'α': [0x1f],

        u'ς': [0x80],
        u'ü': [0x81],
        u'é': [0x82],
        u'â': [0x83],
        u'ä': [0x84],
        u'à': [0x85],
        u'å': [0x86],
        u'ê': [0x88],
        u'ë': [0x89],
        u'è': [0x8a],
        u'ï': [0x8b],
        u'î': [0x8c],
        u'ì': [0x8d],
        u'Ä': [0x8e],
        u'Å': [0x8f],

        u'': [0x90],
        u'': [0x91],
        u'': [0x92],
        u'': [0x93],
        u'': [0x94],
        u'': [0x95],
        u'': [0x96],
        u'': [0x97],
        u'': [0x98],
        u'': [0x99],
        u'': [0x9a],
        u'': [0x9b],
        u'': [0x9c],
        u'': [0x9d],
        u'': [0x9e],
        u'': [0x9f],

        u'á': [0xe0],
        u'í': [0xe1],
        u'ó': [0xe2],
        u'ú': [0xe3],
        u'￠': [0xe4],
        u'£': [0xe5],
        u'¡': [0xe7],
        u'∮': [0xe8],
        u'': [0xe9],
        u'Ã': [0xea],
        u'ã': [0xeb],
        u'Õ': [0xec],
        u'õ': [0xed],
        u'Φ': [0xee],
        u'φ': [0xef],

        u'̇': [0xf0],
        u'̈': [0xf1],
        u'̊': [0xf2],
        u'̀': [0xf3],
        u'́': [0xf4],
        u'½': [0xf5],
        u'¼': [0xf6],
        u'×': [0xf7],
        u'÷': [0xf8],
        u'≧': [0xf9],
        u'≦': [0xfa],
        u'≪': [0xfb],
        u'≫': [0xfc],
        u'≠': [0xfd],
        u'√': [0xfe],
        u'⌒': [0xff],

    }
    
    def __init__( self, i2c, ad ):
        print("so1602 init")
        self.i2c = i2c
        self.ad = ad
        self.cursol = 0
        self.blink = 0
        self.display = 1
        self.x = 0
        self.y = 0

        # self.i2c.write_byte_data( self.ad, 0x00, 0x01)
        # time.sleep(0.20)
        # self.i2c.write_byte_data( self.ad, 0x00, 0x02)
        # time.sleep(0.02)
        # self.i2c.write_byte_data( self.ad, 0x00, 0x0f)
        # time.sleep(0.02)
        # self.i2c.write_byte_data( self.ad, 0x00, 0x06)
        # time.sleep(0.1)
        # self.i2c.write_byte_data( self.ad, 0x00, 0x01)
        # time.sleep(0.1)

         # 初期化コマンドを送信
        self.i2c.write_byte_data(self.ad, 0x00, 0x38)  # Function set
        self.i2c.write_byte_data(self.ad, 0x00, 0x39)  # Function set (extended)
        self.i2c.write_byte_data(self.ad, 0x00, 0x14)  # Internal OSC frequency
        self.i2c.write_byte_data(self.ad, 0x00, 0x70)  # Contrast set
        self.i2c.write_byte_data(self.ad, 0x00, 0x56)  # Power/ICON/Contrast control
        self.i2c.write_byte_data(self.ad, 0x00, 0x6C)  # Follower control
        time.sleep(0.2)  # 待機
        self.i2c.write_byte_data(self.ad, 0x00, 0x38)  # Function set
        self.i2c.write_byte_data(self.ad, 0x00, 0x0C)  # Display ON
        self.clear()  # ディスプレイをクリア
        

    def clear(self):
        self.i2c.write_byte_data( self.ad, 0x00, 0x01)
        time.sleep(0.1)

    def set_display(self):
        buf = 0x08 + 0x04 * self.display + 0x02 * self.cursol + self.blink
        self.i2c.write_byte_data( self.ad, 0x00, buf)
        time.sleep(0.1)
        
    def set_cursol(self,buf):
        if buf != 0:
            buf = 1
        self.cursol = buf
        self.set_display()

    def set_blink(self,buf):
        if buf != 0:
            buf = 1
        self.blink = buf
        self.set_display()        

    def move_home(self):
        self.i2c.write_byte_data(self.ad, 0x00, 0x02)  # Return home
        time.sleep(0.1)  # 待機

    # def move_home(self):
    #     self.x = 0
    #     self.y = 0
    #     self.i2c.write_byte_data( self.ad, 0x00, 0x01)
    #     time.sleep(0.1)

    def move(self,mx,my):    
        self.x = mx
        self.y = my
        if self.x < 0:
            self.x=0
        if self.x > 0x0f:
            self.x=0x0f
        if self.y < 0:
            self.y=0
        if self.y > 1:
            self.y=1
        oy=self.y*0x20
        out=self.x+oy+0x80
        self.i2c.write_byte_data( self.ad, 0x00, out)
        time.sleep(0.1)       

    def write(self, data):
        if isinstance(data, str):
            for char in data:
                self.i2c.write_byte_data(self.ad, 0x40, ord(char))
        else:
            self.i2c.write_byte_data(self.ad, 0x40, data)

    # def write( self, buf ):
    #     msg = []
    #     for ch in buf:
    #         msg += self.char_table[ ch ]
        
    #     length = len(msg)
    #     i = 0
    #     while i < length:
    #         if self.x > 0x0f:
    #             if self.y == 0:
    #                 self.move( 0x00, 0x01 )
    #             else:
    #                 break

    #         out = msg[i]
    #         self.i2c.write_byte_data( self.ad, 0x40, out )

    #         self.x = self.x + 1
    #         i = i + 1

    # def __init__(self, i2c, address):
    #     self.i2c = i2c
    #     self.ad = address
    #     # 初期化処理など

    def write_char(self, char_code):
        # 1文字をディスプレイに送信
        self.i2c.write_byte_data(self.ad, 0x40, char_code)

    def put_string(self, string):
        for char in string:
            self.write_char(ord(char))
