const chaptersPageTable = document.getElementById("chapters-page-table");
const idInput = document.getElementById("search-by-id");
const nameInput = document.getElementById("search-by-serie-name");
const chapterNumInput = document.getElementById("search-by-chapter-no");

function filterByID () {
    const searchText = idInput.value.toLocaleUpperCase();
    const trs = chaptersPageTable.getElementsByTagName("tbody")[0].getElementsByTagName("tr");

    if (!searchText) {
        for (let tr of trs) {
            tr.style.display = ""
        }
    } else {
        for (let tr of trs) {
            const ths = tr.getElementsByTagName("th")
            const idText = ths[0].innerText || ths[0].textContent

            if (idText.toLocaleUpperCase() === searchText) {
                tr.style.display = ""
            } else {
                tr.style.display = "none"
            }

        }
    }
}

function filterBySerieName () {
    const searchedName = nameInput.value.toLocaleUpperCase();
    const searhcedChapterNo = chapterNumInput.value.toLocaleUpperCase();
    const trs = chaptersPageTable.getElementsByTagName("tbody")[0].getElementsByTagName("tr");

    if (!searchedName) {
        if (!searhcedChapterNo) {
            for (let tr of trs) {
                tr.style.display = "";
            }
        } else {
            filterByChapterNumber();
        }
    } else {
        for (let tr of trs) {
            const tds = tr.getElementsByTagName("td");
            const nameText = tds[0].innerText || tds[0].textContent;
            
            if (searhcedChapterNo) {
                const chapterNumText = tds[1].innerText || tds[1].textContent;
                const searhcedChapterNoWithDot = searhcedChapterNo.replace(",", ".");

                if (nameText.toLocaleUpperCase().indexOf(searchedName) > -1 && chapterNumText.toLocaleUpperCase().indexOf(searhcedChapterNoWithDot) > -1) {
                    tr.style.display = "";
                } else {
                    tr.style.display = "none";
                }
            } else {
                if (nameText.toLocaleUpperCase().indexOf(searchedName) > -1) {
                    tr.style.display = "";
                } else {
                    tr.style.display = "none";
                }
            }
        }
    }

}

function filterByChapterNumber () {
    const searchedName = nameInput.value.toLocaleUpperCase();
    const searhcedChapterNo = chapterNumInput.value.toLocaleUpperCase();
    const trs = chaptersPageTable.getElementsByTagName("tbody")[0].getElementsByTagName("tr");

    if (!searhcedChapterNo) {
        if (!searchedName) {
            for (let tr of trs) {
                tr.style.display = "";
            }
        } else {
            filterBySerieName();
        }
    } else {
        for (let tr of trs) {
            const tds = tr.getElementsByTagName("td");
            const chapterNumText = tds[1].innerText || tds[1].textContent;
            const searhcedChapterNoWithDot = searhcedChapterNo.replace(",", ".");
            
            if (searchedName) {
                const nameText = tds[0].innerText || tds[0].textContent;

                if (nameText.toLocaleUpperCase().indexOf(searchedName) > -1 && chapterNumText.toLocaleUpperCase().indexOf(searhcedChapterNoWithDot) > -1) {
                    tr.style.display = "";
                } else {
                    tr.style.display = "none";
                }
            } else {
                if (chapterNumText.toLocaleUpperCase().indexOf(searhcedChapterNoWithDot) > -1) {
                    tr.style.display = "";
                } else {
                    tr.style.display = "none";
                }
            }
        }
    }
}

function changeOnFocus(colReference) {
    const currentValue = colReference.innerText || colReference.textContent;

    const first = colReference.getAttribute("data-first");
    const second = colReference.getAttribute("data-second");

    if (currentValue === first) {
        colReference.innerText = second;
    } else if (currentValue === second) {
        colReference.innerText = first;
    }
}