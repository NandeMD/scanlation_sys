function filterByName () {
    const personnelTable = document.getElementById("table-personnel")
    const input = document.getElementById("search-by-name")

    const searchText = input.value.toLocaleUpperCase()

    const trs = personnelTable.getElementsByTagName("tbody")[0].getElementsByTagName("tr")

    if (!searchText) {
        for (let tr of trs) {
            tr.style.display = ""
        }
    } else {
        for (let tr of trs) {
            const tds = tr.getElementsByTagName("td")
            const nameText = tds[0].innerText || tds[0].textContent

            if (nameText.toLocaleUpperCase().indexOf(searchText) > -1) {
                tr.style.display = ""
            } else {
                tr.style.display = "none"
            }

        }
    }

}

function filterByID () {
    const personnelTable = document.getElementById("table-personnel")
    const input = document.getElementById("search-by-id")

    const searchText = input.value

    const trs = personnelTable.getElementsByTagName("tbody")[0].getElementsByTagName("tr")

    if (!searchText) {
        for (let tr of trs) {
            tr.style.display = ""
        }
    } else {
        for (let tr of trs) {
            const ths = tr.getElementsByTagName("th")
            const idText = ths[0].innerText || ths[0].textContent

            if (idText === searchText) {
                tr.style.display = ""
            } else {
                tr.style.display = "none"
            }
        }
    }

}