$(document).ready(function () {
    bsCustomFileInput.init();
});

function sign_out() {
    $.removeCookie("accessToken", {path: "/"});
    $.removeCookie("refreshToken", {path: "/"});
    window.location.href = "/login";
}

function update_profile() {
    let name = $("#input-name").val();
    let file = $("#input-pic")[0].files[0];
    let form_data = new FormData();
    form_data.append("file_give", file);
    form_data.append("name_give", name);

    $.ajax({
        type: "POST",
        url: "/user/edit",
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            if (response["result"] == "success") {
                alert(response["msg"]);
                window.location.reload();
            } else {
                alert('로그인이 만료되었습니다. 다시 로그인해 주십시오.');
                window.location.reload();
            }
        },
    });
}
