/**
 * LED制御のJavaScript
 */
$(document).ready(function() {
    $('#led-all-blink-form').submit(function(event) {
        event.preventDefault(); // フォームのデフォルト送信を防ぐ

        // フォームのデータを取得
        const formData = new FormData(this);
        const blinkInterval = formData.get('blink-interval');
        

        // 非同期リクエストを送信
        fetch('/LedAllLightOnAjax/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}' // DjangoのCSRFトークン
            },
            body: {}
        })
        .then(response => response.json())
        .then(data => {})
        
    });

    // $('#led-all-blink-form').submit(function(event) {
    //     event.preventDefault(); // フォームのデフォルト送信を防ぐ
    //     var form = $(this);
    //     $.ajax({
    //         type: form.attr('method'),
    //         url: form.attr('action'),
    //         data: form.serialize(),
    //         success: function(response) {
    //             alert(response.message);
    //         },
    //         error: function(response) {
    //             alert('エラーが発生しました');
    //         }
    //     });
    // });
});