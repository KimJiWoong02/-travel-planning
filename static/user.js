$(document).ready(function () {
  bsCustomFileInput.init();
  listing("{{ user_info.id }}");
});

function listing(id) {
  $.ajax({
    url: "/user/myplan",
    data: {
      id: id,
    },
    success: function (response) {
      const { myplan } = response;
      console.log(myplan);
    },
    // window.location.reload();
  });
}

function sign_out() {
  $.removeCookie("accessToken", { path: "/" });
  $.removeCookie("refreshToken", { path: "/" });
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
      }
    },
    error: function (request, status, error) {
      alert(
        "code:" +
          request.status +
          "\n" +
          "message:" +
          request.responseText +
          "\n" +
          "error:" +
          error
      );
    },
  });
}
