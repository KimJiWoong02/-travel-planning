$(document).ready(function () {
  bsCustomFileInput.init();
  listing();
});

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

function listing() {
  $.ajax({
    type: "GET",
    url: "/user/myplan",
    data: {},
    success: function (response) {
      const { myplan } = response;
      console.log(myplan);

      const planList = $("#planList");

      if (!myplan) {
        planList.replaceWith(
          `<div class="d-flex justify-content-center mt-5"><h1>아직 작성한 여행계획이 없습니다.</h1></div>`
        );
        return;
      }
      myplan.forEach((plan) => planList.append(createPlanCard(plan)));
    },
    // window.location.reload();
  });
}

function createPlanCard(plan) {
  const { image, title, user_id, _id, dateStart, dateEnd } = plan;

  return `<div class="col" id=${_id}>
                <div class="card" data-bs-toggle="modal" data-bs-target="#planModal" data-id="${_id}">
                    <div class="card-img-top" style="height: 13rem; background-image: url(${image}); background-size: cover; background-position: center"></div>
                    <div class="card-body">
                        <h5 class="card-title text-dark">${title}</h5>
                        <p class="card-text text-muted small">${dateStart} ~ ${dateEnd}</p>
                        <div class="d-flex justify-content-end">
                            <span class="card-text text-muted">Host - ${user_id}</span>
                        </div>
                    </div>
                </div>
            </div>`;
}
