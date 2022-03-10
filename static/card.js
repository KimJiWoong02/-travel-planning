
// get 요청 API code
  function listing() {
            $("#cards-posted").empty()

            $.ajax({
                type: 'GET',
                url: '/plan',
                data: {},
                success: function (response) {
                    let rows = response['plans']
                    for(let i =0; i < rows.length; i++){
                        let title = rows[i]['title']
                        let area = rows[i]['area']
                        let location = rows[i]['location']


                        let temp = `
                        <div class="card"> 
                            <div class="card-body">
                                <h5 class="card-title">${title}</h5>
                                <p class="card-text"> ${area} / ${location} </p>
                            </div>
                
                            <div class="card-like">
                                <a class="card-like-a" aria-label="heart" onclick="toggle_like('', 'heart')">
                                    <span class="icon is-small"><i class="fa fa-heart" aria-hidden="true"></i></span>&nbsp;<span
                                        class="like-num">2.7k</span>
                                </a>
                            </div>
                        </div>
                        
                        `
                        let cardWrap = document.querySelector('#cards-posted')
                        cardWrap.insertAdjacentHTML('beforeend', temp)
                    }
                    console.log(response['plans'])

                }
            })
        }



function posting() {
    // 상세폼이 빈칸일시 alert & 박스 안없어지게 하기 notes는 제외
    if($('#card-title').val() == '' ) {
        alert("제목을 입력하세요.");
        $('#card-title').focus();
        e.preventDefault();
    }
   if($('#card-image').val() == '' ) {
        alert("이미지 url를 넣어주세요..");
        $('#card-image').focus();
        e.preventDefault();
   }
   if($('#card-area').val() == "selected" ) {
        alert("지역을 선택해주세요.");
        $('#card-area').focus();
        e.preventDefault();
   }
   if($('#card-date-start').val() == '' && $('#card-date-start').val() == '') {
        alert("여행 기간을 설정해주세요");
        $('#card-date-start').focus();
        e.preventDefault();
   }


    else {
        let image =  $('#card-image').val()
        let title = $('#card-title').val()
        let area = $('#card-area').val()
        let location = $('#card-location').val()
        let dateStart = $('#card-date-start').val()
        let dateEnd = $('#card-date-end').val()
        let detailTable = tableToArr()

        console.log(detailTable)

        $.ajax({
            type: "POST",
            url: "/plan",
            data: {
                 image_give : image,
                 title_give: title,
                 area_give: area,
                 location_give: location,
                 date_start_give: dateStart,
                 date_end_give: dateEnd,
                 detail_table_give: JSON.stringify(detailTable)
            },
            success: function (response) {
                alert(response['msg'])
                window.location.reload()
            }
        })
    }
}

// 세부일정 폼 추가


const modal = document.getElementById('modal-wrap');
const cardForm = document.getElementById('card-form');

const detailContainer = document.getElementById('detail-form');
const detailTableRow = document.getElementById('detail-contents');
const datailAddBtn = document.getElementById('btn-detail-add');

const detailDate = document.getElementById('form-detail-date');
const detailLocation = document.getElementById('form-detail-location');
const detailAddress = document.getElementById('form-detail-address');
const detailNotes = document.getElementById('form-detail-notes');

const detailTableContents = document.getElementById('detail-table-contents')



// 세부일정 등록 버튼 클릭 (제출)

datailAddBtn.addEventListener('click',  addDetailForm)


// 전체일정 등록 버튼 클릭(제출)
cardForm.addEventListener("submit", addCardForm);

function addCardForm(e) {
    e.preventDefault();

}

// 카드폼 열기
function openForm() {
    modal.classList.remove('hide');
}

// 카드폼 닫기
function closeForm() {
    modal.classList.add('hide');
}

// 세부일정 추가
function openDetailForm() {
    detailContainer.classList.remove('hide');
}

// 세부일정 취소
function hideDetailForm() {
    detailContainer.classList.add('hide');
}


// 세부일정 등록

function addDetailForm() {
    const card = createDetailRow();
    // 상세폼이 빈칸일시 alert & 박스 안없어지게 하기 notes는 제외
    if (detailDate.value== '' || detailLocation.value== '' || detailAddress.value== '') {
    alert("내용을 입력하세요.");
    datailAddBtn.disable = true;

    } else {
    detailTableRow.append(card);
    hideDetailForm();
    tableToArr();
    detailDate.value = ""
    detailAddress.value = ""
    detailLocation.value = ""
    detailNotes.value = ""
    }
}


// 세부일정 td 생성
let id = 0;
function createDetailRow() {
    const tableRow = document.createElement('tr');
    tableRow.setAttribute('class', 'detail-tr');
    tableRow.setAttribute('data-id', id);
    tableRow.innerHTML = `
                <td class="tg">
                    <span>${detailDate.value} 일차 </span>
                </td>
                <td class="tg">
                    <span>${detailLocation.value}</span>
                </td>
                <td class="tg">
                    <span>${detailAddress.value}</span>
                </td>
                <td class="tg-l1tf">${detailNotes.value}</td>
                <td class="td-bin"><button onclick="removeDetailPlan()" id="btn-remove-detail">🗑</button></td>  
    `
    id++;
    return tableRow;
}

// table to array

function tableToArr() {
     let detailTableArr = [];

    $('.detail-tr').each(function () {
        let rowDataArray = [];
        let detailVal = $(this).find('td');
        if (detailVal.length > 0) {
            detailVal.each(function () {
                rowDataArray.push($(this).text().replace(/\n|\r|\s*/g, ""));
            });
            detailTableArr.push(rowDataArray);
        }
    })
    return detailTableArr
}

// card click 했을 때

const card = document.querySelector('card');