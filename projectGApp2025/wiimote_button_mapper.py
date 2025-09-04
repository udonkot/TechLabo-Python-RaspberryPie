#!/usr/bin/env python3
"""
Wiiリモコンのボタンマッピングを確認するツール
どのボタンがどのキーコードに対応しているか確認できます
"""

import evdev
from evdev import InputDevice, categorize, ecodes
import sys
import time

def find_wiimote():
    """Wiiリモコンを自動検出"""
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    
    for device in devices:
        if "Nintendo" in device.name or "Wii" in device.name:
            return device
    return None

def print_capabilities(device):
    """デバイスのケーパビリティを表示"""
    print("\n📊 デバイス情報:")
    print(f"  名前: {device.name}")
    print(f"  パス: {device.path}")
    print(f"  物理アドレス: {device.phys}")
    
    capabilities = device.capabilities(verbose=True)
    print("\n🎮 利用可能な機能:")
    for event_type, codes in capabilities.items():
        print(f"  {event_type[0]}: {len(codes)} codes")

def monitor_buttons(device):
    """ボタン入力を監視してマッピングを表示"""
    print("\n" + "="*60)
    print("🎯 ボタンマッピングテスト")
    print("="*60)
    print("\n横持ちでWiiリモコンのボタンを押してください:")
    print("（終了: Ctrl+C）\n")
    
    # 横持ち時のボタン説明
    button_descriptions = {
        'KEY_LEFT': '十字キー左（実際の下）',
        'KEY_RIGHT': '十字キー右（実際の上）',
        'KEY_UP': '十字キー上（実際の左）',
        'KEY_DOWN': '十字キー下（実際の右）',
        'BTN_1': '1ボタン',
        'BTN_2': '2ボタン',
        'BTN_A': 'Aボタン（大きいボタン）',
        'BTN_B': 'Bボタン（トリガー）',
        'KEY_PREVIOUS': '-ボタン',
        'KEY_NEXT': '+ボタン',
        'BTN_MODE': 'HOMEボタン',
        'BTN_TRIGGER': 'Bボタン（別名）',
        'BTN_THUMB': 'Aボタン（別名）'
    }
    
    button_states = {}
    last_combo_time = 0
    combo_buttons = []
    
    try:
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                
                # キーコードを取得
                if isinstance(key_event.keycode, list):
                    keycode = key_event.keycode[0] if key_event.keycode else 'UNKNOWN'
                else:
                    keycode = key_event.keycode
                
                # ボタン状態を更新
                button_states[keycode] = (key_event.keystate == 1)
                
                # 状態を文字列化
                state_str = {
                    0: "🔴 離した",
                    1: "🟢 押した",
                    2: "🔄 長押し"
                }.get(key_event.keystate, "❓ 不明")
                
                # 説明を取得
                description = button_descriptions.get(keycode, "")
                
                # 表示
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] {state_str} | コード: {keycode:15} | {description}")
                
                # 同時押し検出
                if key_event.keystate == 1:
                    current_time = time.time()
                    if current_time - last_combo_time < 0.2:  # 200ms以内
                        combo_buttons.append(keycode)
                    else:
                        combo_buttons = [keycode]
                    last_combo_time = current_time
                    
                    # 現在押されているボタンをチェック
                    pressed_buttons = [k for k, v in button_states.items() if v]
                    if len(pressed_buttons) > 1:
                        print(f"    💫 同時押し検出: {' + '.join(pressed_buttons)}")
                
            elif event.type == ecodes.EV_ABS:
                abs_event = categorize(event)
                print(f"[モーション] {abs_event.event}")
                
            elif event.type == ecodes.EV_REL:
                rel_event = categorize(event)
                print(f"[相対移動] {rel_event.event}")
                
    except KeyboardInterrupt:
        print("\n\n終了します")

def generate_mapping_code(device):
    """検出したボタンからマッピングコードを生成"""
    print("\n📝 以下のマッピングコードを使用できます:")
    print("-"*40)
    print("BUTTON_MAP = {")
    
    # 標準的なWiiリモコンのマッピング
    standard_mapping = [
        ("'KEY_LEFT'", "'left'"),
        ("'KEY_RIGHT'", "'right'"),
        ("'KEY_UP'", "'up'"),
        ("'KEY_DOWN'", "'down'"),
        ("'BTN_1'", "'1'"),
        ("'BTN_2'", "'2'"),
        ("'BTN_A'", "'a'"),
        ("'BTN_B'", "'b'"),
        ("'KEY_PREVIOUS'", "'minus'"),
        ("'KEY_NEXT'", "'plus'"),
        ("'BTN_MODE'", "'home'"),
    ]
    
    for key, value in standard_mapping:
        print(f"    {key:15}: {value},")
    
    print("}")
    print("-"*40)

def main():
    """メイン処理"""
    print("="*60)
    print("🎮 Wiiリモコン ボタンマッピング確認ツール")
    print("="*60)
    
    # Wiiリモコンを検出
    device = find_wiimote()
    
    if not device:
        print("\n❌ Wiiリモコンが見つかりません!")
        print("\n接続方法:")
        print("1. bluetoothctl を起動")
        print("2. scan on でスキャン開始")
        print("3. Wiiリモコンの 1+2 ボタンを同時押し")
        print("4. pair <MACアドレス> でペアリング")
        print("5. connect <MACアドレス> で接続")
        
        print("\n\n利用可能なデバイス一覧:")
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for d in devices:
            print(f"  {d.path}: {d.name}")
        
        sys.exit(1)
    
    print(f"\n✅ Wiiリモコンを検出しました!")
    
    # ケーパビリティを表示
    print_capabilities(device)
    
    # マッピングコードを生成
    generate_mapping_code(device)
    
    # ボタン監視を開始
    monitor_buttons(device)

if __name__ == "__main__":
    try:
        main()
    except PermissionError:
        print("\n❌ 権限エラー: sudo で実行するか、ユーザーを input グループに追加してください")
        print("   sudo usermod -a -G input $USER")
        print("   その後、再ログインしてください")
    except Exception as e:
        print(f"\n❌ エラー: {e}")