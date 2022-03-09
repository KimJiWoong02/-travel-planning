// 회원가입
function sign_up() {
    let name_pass = inputForm_name()
    let id_pass = inputForm_id() // 서버 return이 늦어 깜빡임을 방지하기 위해 호출만 한다
    let pw_pass = inputForm_pw()
    let repw_pass = inputForm_repw()

    // 모든 입력 양식 충족 시 회원가입 진행
    if (name_pass && pw_pass && repw_pass) {
        $.ajax({
            type: "POST",
            url: "/api/sign_up/save",
            data: {
                id_give: $('#userID').val(),
                pw_give: $('#userPassword').val(),
                name_give: $('#userName').val()
            },
            success: function (response) {
                if (response['result'] == 'success') { // 회원가입 성공 시
                    // input과 err 메세지 초기화
                    textInit()

                    // login 페이지로 이동
                    window.location.href = '/login'
                } else { // 중복된 아이디로 회원가입 실패 시
                    $('#err_id_msg').text('이미 사용중인 아이디입니다.')
                    $('#err_id_msg').css("color", 'red');
                    $('#err_id_wrap').show()
                }
            }
        })
    }
}

// ID 중복체크 (ajax 실행 후 값이 돌아오는 시간이 걸려 문자가 깜빡이는 현상이 있어 api 호출 후 처리한다
// [중복체크 api호출 -> 사용가능 ID입니다 출력 -> api return(중복입니다) -> 중복입니다 출력]현상)
function check_dup() {
    $.ajax({
        type: "GET",
        url: "/api/sign_up/check_dup",
        data: {id_give: $('#userID').val()},
        success: function (response) {
            if (response['result'] == 'success') { // 중복되는 아이디 없음
                let id = $('#userID').val()
                if (isBlank(id)) { // id가 빈 공간일 시
                    $('#err_id_msg').text('필수 정보입니다.')
                    $('#err_id_msg').css("color", 'red');
                    $('#err_id_wrap').show()
                    return false
                } else if (!is_userID(id)) { // id 양식에 적합한지 체크
                    $('#err_id_msg').text('5~20자의 영문 소문자, 숫자와 특수기호(_), (-)만 사용 가능합니다.')
                    $('#err_id_msg').css("color", 'red');
                    $('#err_id_wrap').show()
                    return false
                } else { // 사용가능한 아이디 일 시
                    $('#err_id_msg').text('멋진 아이디에요!')
                    $('#err_id_msg').css("color", '#00cc00');
                    $('#err_id_wrap').show()
                    return true
                }
                return false
            } else { // 중복되는 아이디가 있으면 response['result']가 fail
                $('#err_id_msg').text('이미 사용중인 아이디입니다.')
                $('#err_id_msg').css("color", 'red');
                $('#err_id_wrap').show()
                return false
            }
        }
    })
}

// str이 빈 공간인지 확인
function isBlank(str) {
    return (!str);
}

// 유저 이름은 한글과 영문 대 소문자를 사용. (특수기호, 공백 사용 불가)
function is_userName(name) {
    var regExp = /^[가-힣a-zA-Z0-9]+$/;
    return regExp.test(name);
}

// 유저 ID는 5~20자의 영문 소문자, 숫자와 특수기호(_),(-)만 사용
function is_userID(id) {
    // 정규표현식은 '/' 로 감싼다. 대괄호 앞에 '^'가 있으면 시작을 뜻하고, 대괄호 안에 '^'가 붙으면 제외를 뜨한다
    var regExp = /^[a-z0-9]+[a-z0-9_-]{4,19}$/;
    return regExp.test(id);
}

// 유저 pw는 무조건 숫자와 영문을 포함한 8~16자 영문 대 소문자, 숫자, 특수문자를 사용.
function is_userPassword(pw) {
    // *\d = 숫자 무조건 포함해라
    var regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,16}$/;
    return regExp.test(pw);
}

// 비밀번호와 재입력 비밀번호가 같은지 체크
function is_samePassword(pw, repw) {
    return pw == repw
}

// 이름이 입력 양식에 맞는지 체크
function inputForm_name() {
    let name = $('#userName').val()

    if (isBlank(name)) {
        $('#err_name_msg').text('필수 정보입니다.')
        $('#err_name_wrap').show()
        return false
    } else if (!is_userName(name)) {
        $('#err_name_msg').text('한글과 영문 대 소문자를 사용하세요. (특수기호, 공백 사용 불가)')
        $('#err_name_wrap').show()
        return false
    } else {
        $('#err_name_wrap').hide()
        return true
    }
}

// id가 입력 양식에 맞는지 체크
function inputForm_id() {
    return check_dup()  // ID 중복 체크
}

// pw가 입력 양식에 맞는지 체크
function inputForm_pw() {
    let pw = $('#userPassword').val()

    if (isBlank(pw)) {
        $('#err_pw_msg').text('필수 정보입니다.')
        $('#err_pw_wrap').show()
        return false
    } else if (!is_userPassword(pw)) {
        $('#err_pw_msg').text('8~16자 영문 대 소문자, 숫자, 특수문자를 사용하세요.')
        $('#err_pw_wrap').show()
        return false
    } else {
        $('#err_pw_wrap').hide()
        return true
    }
}

// repw가 입력 양식에 맞는지 체크, pw와 같은지 비교
function inputForm_repw() {
    let pw = $('#userPassword').val()
    let repw = $('#userRePassword').val()

    if (isBlank(repw)) {
        $('#err_repw_msg').text('필수 정보입니다.')
        $('#err_repw_wrap').show()
        return false
    } else if (!is_samePassword(pw, repw)) {
        $('#err_repw_msg').text('비밀번호가 일치하지 않습니다.')
        $('#err_repw_wrap').show()
        return false
    } else {
        $('#err_repw_wrap').hide()
        return true
    }
}

function textInit() {
    $('#userName').val('')
    $('#userID').val('')
    $('#userPassword').val('')
    $('#userRePassword').val('')

    $('#err_name_wrap').hide()
    $('#err_id_wrap').hide()
    $('#err_pw_wrap').hide()
    $('#err_repw_wrap').hide()
}

function init() {
    $('#userName').focusout(function () {
        inputForm_name()
    });

    $('#userID').focusout(function () {
        inputForm_id()
    });

    $('#userPassword').focusout(function () {
        inputForm_pw()
    });

    $('#userRePassword').focusout(function () {
        inputForm_repw()
    });
}