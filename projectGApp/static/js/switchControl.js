console.log('start script');
document.addEventListener('DOMContentLoaded', function() {
    const switches = document.querySelectorAll('.custom-control-input');

    switches.forEach(switchElement => {
        switchElement.addEventListener('change', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            const isChecked = this.checked;
            const gpioNo = this.getAttribute('data-gpio');

            // 非同期リクエストを送信
            fetch('/update-switch-state/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}' // DjangoのCSRFトークン
                },
                body: JSON.stringify({
                    switchId: this.id,
                    state: isChecked,
                    gpioNo: gpioNo
                })
            })
            .then(response => response.json())
            .then(data => {
                // サーバーからのレスポンスに基づいて表示文言を変更
                if (data.success) {
                    targetElement.textContent = `${targetElement.getAttribute('data-label')}の状態: ${isChecked ? 'ライトオン' : 'ライトオフ'}`;
                } else {
                    alert('スイッチの状態を更新できませんでした。');
                }
            })
            .catch(error => {
                console.error('エラー:', error);
                alert('スイッチの状態を更新できませんでした。');
            });
        });
    });
});