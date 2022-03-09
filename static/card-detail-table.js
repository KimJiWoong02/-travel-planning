
function posting() {
    // 빈칸일시 제출 못함
    // if ($('.card-form').val() == '') {
    // alert("내용을 입력하세요.");
    // } else {
        let title = $('#card-title').val()
        let area = $('#card-area').val()
        let location = $('#card-location').val()
        let dateStart = $('#card-date-start').val()
        let dateEnd = $('#card-date-end').val()
        let share = $('#card-share').val()

        for (let i = 0; i < detailTableArr.length; i++) {

            let detailDate = detailTableArr[i][0];
            let detailLocation = detailTableArr[i][1];
            let detailAddress = detailTableArr[i][2];
            let detailNotes = detailTableArr[i][3];
        }
        console.log("wpfef",detailTableArr);


        $.ajax({
            type: "POST",
            url: "/plan",
            data: {
                 title_give: title,
                 area_give: area,
                 location_give: location,
                 dateStart_give: dateStart,
                 dateEnd_give: dateEnd,
                 share_give: share,
                 detailTable_give : [detailDate, detailLocation, detailAddress, detailNotes ]
            },
            success: function (response) {
                alert(response['msg'])
                window.location.reload()
            }
        })
   // }
}