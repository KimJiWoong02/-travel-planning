const navMax = 5

$(document).ready(() => {
    let query = window.location.search

    loadPlans(query)

    function getQueryStringValue(key) {
        return decodeURIComponent(query.replace(new RegExp("^(?:.*[&\\?]" + encodeURIComponent(key).replace(/[\.\+\*]/g, "\\$&") + "(?:\\=([^&]*))?)?.*$", "i"), "$1"));
    }

    const selected_loca = getQueryStringValue("location")
    const selected_sort = getQueryStringValue("sort")
    const search_query = getQueryStringValue("query")

    $('#location').val(selected_loca).prop('selected', true)
    $('#sort').val(selected_sort).prop('selected', true)

    $('#location').change(() => {
        const location = $('#location').val()
        const sort = $('#sort').val()

        if (location.length > 0 && sort.length > 0) {
            query = `/?location=${location}&sort=${sort}`
        } else if (location.length > 0) {
            query = `/?location=${location}`
        } else if (sort.length > 0) {
            query = `/?sort=${sort}`
        } else {
            query = '/'
        }

        window.location.href = query
    })

    $('#sort').change(() => {
        const location = $('#location').val()
        const sort = $('#sort').val()

        if (location.length > 0 && sort.length > 0) {
            query = `/?location=${location}&sort=${sort}`
        } else if (sort.length > 0 && search_query) {
            query = `/?sort=${sort}&query=${search_query}`
        } else if (sort.length > 0) {
            query = `/?sort=${sort}`
        } else if (location.length > 0) {
            query = `/?location=${location}`
        } else {
            query = '/'
        }

        window.location.href = query
    })

    $('.form').submit((e) => {
        e.preventDefault()

        const queryStr = $('.query').val()

        query = `/?query=${queryStr}`

        window.location.href = query
    })

    $('#planModal').on("show.bs.modal", onPlanModalShow)
})

function loadPlans(query) {
    $.ajax({
        type: 'GET',
        url: '/api/plans',
        data: Object.fromEntries(new URLSearchParams(query)),
        success: onSuccess
    })
}

function onSuccess(response) {
    const {plans, last_page, page, none} = response
    const planList = $("#planList")
    const paginatorHolder = $("#paginatorHolder")
    if (none) {
        planList.replaceWith(`<div class="d-flex justify-content-center mt-5"><h1>${none}</h1></div>`)
        return
    }
    plans.forEach(plan => planList.append(createPlanCard(plan)))
    paginatorHolder.replaceWith(createPaginator(page, last_page, navMax))
}

function createPlanCard(plan) {
    let {image, title, user_id, _id, dateStart, dateEnd} = plan

    return `<div class="col" id=${_id}>
                <div class="card" data-bs-toggle="modal" data-bs-target="#planModal" data-id="${_id}">
                    <div class="card-img-top" style="height: 13rem; background-image: url(${image}); background-size: cover; background-position: center"></div>
                    <div class="card-body">
                        <h5 class="card-title text-dark">${title}</h5>
                        <p class="card-text text-muted small">${dateStart} ~ ${dateEnd}</p>
                        <div class="d-flex justify-content-end">
                            <span class="card-text text-muted">by ${user_id}</span>
                        </div>
                    </div>
                </div>
            </div>`
}

function createPaginator(page, last_page, navMax) {
    let html = ''
    let buttons = ''
    let next = ''
    let prev = ''
    const isLastNavPage = last_page - page >= navMax

    const buttonGenerator = (pageNum, route) => {
        const listClassName = (pageNum === page) ? "page-item active" : "page-item"
        return `<li class="${listClassName}"><a class="page-link" href="${route}">${pageNum}</a></li>`
    }

    const range = (start, stop, step = 1) => Array.from({length: (stop - start) / step + 1}, (_, i) => start + (i * step))

    if (isLastNavPage) {
        range(page, page + navMax - 1).forEach(pageNum => {
            buttons += buttonGenerator(pageNum, `/?${getQueryString({page: pageNum})}`)
        })
    } else {
        range(page, last_page).forEach(pageNum => {
            buttons += buttonGenerator(pageNum, `/?${getQueryString({page: pageNum})}`)
        })
    }

    if (page !== 1) {
        prev = `<li class="page-item">
                    <a class="page-link" href='/?${getQueryString({page: page <= 5 ? (page - page + 1) : page - 5})}' aria-label="Previous">
                        <span aria-hidden="true">&laquo;</span>
                    </a>
                </li>`
    } else {
        prev = ''
    }

    if (page !== last_page) {
        next = `<li class="page-item">
                    <a class="page-link" href="/?${getQueryString({page: last_page - page <= 5 ? page + (last_page - page) : page + navMax})}" aria-label="Next">
                        <span aria-hidden="true">&raquo;</span>
                    </a>
                </li>`
    } else {
        next = ''
    }

    html = `<nav id="paginator" class="mt-4 d-flex justify-content-center">
                <ul class="pagination">
                    ${prev}
                    ${buttons}
                    ${next}
                </ul>
            </nav>`

    return html
}

function getQueryString(query = undefined) {
    const usp = new URLSearchParams(window.location.search)
    query && Object.entries(query).forEach(([key, value]) => {
        usp.delete(key)
        usp.append(key, String(value))
    })
    return usp.toString()
}

function onPlanModalShow(event) {
    $.ajax({
        type: 'GET',
        url: `/api/plans/${event.relatedTarget.dataset.id}`,
        success: drawPlanModal
    })
}


function drawPlanModal(plan) {
    const arr = JSON.parse(plan.detailTable);

const newArr = arr.map((item) => {
        console.log(item[0])
        return `<tr>
                    <td className="tg">
                        <span>${item[0]}</span>
                    </td>
                    <td className="tg">
                        <span>${item[1]}</span>
                    </td>
                    <td className="tg">
                        <span>${item[2]}</span>
                    </td>
                    <td className="tg-l1tf">${item[3]}</td>
                </tr>`;
})
    console.log("new", newArr);


     const header = `<strong>${plan['user_id']}</strong> 님의 여행계획
     <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
    `
      let html = `
    
    <div class="card-group">
        <div class="card-img"> <img src="${plan.image}" id="card-posted-img" class="card-img-top" alt="card-image"></div>
        <div class="card-temp">
           
            <h2 class="card-temp-title modal-title fw-bold text-primary">${plan.title}</h2>
            <ul>
                <li class="card-temp-location ">지역 : ${plan.area} / ${plan.location}</li>
                <li class="card-temp-date">기간 : ${plan.dateStart} ~ ${plan.dateEnd}</li>
            </ul>
        </div>

        <!-- detail table 세부일정 테이블 -->
        <table class="contents table">
            <thead>
            <tr>
                <th class="tg">일차</th>
                <th class="tg">
                    <span>장소 </span>
                </th>
                <th class="tg">
                    <span>주소</span>
                </th>
                <th class="tg">
                    <span>메모</span>
                </th>
            </tr>
            </thead>
            <!-- detail form template 세부일정 템플릿 -->

            <tbody class="detail-contents">     
            ${newArr}
            </tbody>
        </table>
        
        </div>
    </div>
</div>
 `

    console.log(plan)

    $("#planModal .modal-header").html(header)
    $("#planModal .modal-body").html(html)


}