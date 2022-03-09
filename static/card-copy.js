$(document).ready(function () {
    listing()
})

function getDetailForm() {
    window.location.href = "http://localhost:5000/result"
}

// get 요청 API code
function listing() {
    $.ajax({
        type: "GET",
        url: "/plans?sample_give=샘플데이터",
        data: {},
        success: function (response) {
            alert(response['msg'])
        }
    })
}

function posting() {
    $.ajax({
        type: "POST",
        url: "/plans",
        data: {sample_give: '샘플데이터'},
        success: function (response) {
            alert(response['msg'])
        }
    })
}


// 세부일정 폼 추가

const modal = document.getElementById('modal');
const cardForm = document.getElementById('card-form');

const detailContainer = document.getElementById('detail-form');
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
    let detail_temp = `
        <tbody class="detail-contents">
           <tr class="detail-tr">
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
           </tr>
        </tbody>
`
    // 상세폼이 빈칸일시 alert & 박스 안없어지게 하기 notes는 제외
    if (detailDate.value== '' || detailLocation.value== '' || detailAddress.value== '') {
    alert("내용을 입력하세요.");
    datailAddBtn.disable = true;

    } else {
    detailTableContents.insertAdjacentHTML('beforeend', detail_temp);
    hideDetailForm();
    }
}

