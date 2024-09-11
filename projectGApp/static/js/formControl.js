/**
 * form ajax JavaScript
 */
$(document).ready(function() {
    $('.ajax-form').submit(function(event) {
        event.preventDefault(); // フォームのデフォルト送信を防ぐ

        // フォームのデータを取得
        const formData = new FormData(this);
        const url = formData.get('url');

        const val01 = formData.get('val01');
        const val02 = formData.get('val02');
        const val03 = formData.get('val03');

        // CSRF トークンを取得
        const csrf_token = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // 非同期リクエストを送信
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token // DjangoのCSRFトークン
            },
            body: JSON.stringify({
                val01: val01,
                val02: val02,
                val03: val03
            })
        })
        .then(response => response.json())
        .then(data => {})
        
    });
});