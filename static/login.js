// 로그인 작업
function sign_in() {
    let id = $('#userID').val()
    let pw = $('#userPassword').val()

    // err 메세지 hide
    err_msg_hide()

    // id와 pw의 값이 있는지 확인
    if (isBlank(id)) {
        $('#err_empty_id').show()
        return
    } else if (isBlank(pw)) {
        $('#err_empty_pw').show()
        return
    }

    $.ajax({
        type: "POST",
        url: "/api/sign_in",
        data: {id_give: id, pw_give: pw},
        success: function (response) {
            if (response['result'] == 'success') {
                // 쿠키에 accessToken, refreshToken 저장
                $.cookie('accessToken', response['accessToken'], {httponly: true});
                $.cookie('refreshToken', response['refreshToken'], {httponly: true});
                window.location.href = '/'
            } else {
                // 아이디 비밀번호가 틀리면 메세지 표시
                $('#err_common').show()
            }
        }
    })
}

function sign_up() {
    window.location.href = '/register'
}

// 문자열이 blank인지 확인
function isBlank(str) {
    return (!str || str.length === 0);
}

// 모든 err 메세지를 hide
function err_msg_hide() {
    $('#err_empty_id').hide()
    $('#err_empty_pw').hide()
    $('#err_common').hide()
}

function init() {
    // 페이지 로딩 후 error 메세지 hide
    err_msg_hide()
}