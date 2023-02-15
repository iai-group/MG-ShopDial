// Search engine retrieval

let searchUrl = document.getElementById("search_engine").getAttribute("url");

let generalResults = undefined;
let currentGeneralPage = 0;
let generalPages = "";
let page_size = 5;
let resultList = document.getElementById("search-results");


$(document).on("submit", "#search-bar", function (event) {
    event.preventDefault();
    privateRoomId = document.getElementById("private-room-id").value;

    var data = new FormData(this);
    data.append("private_room_id", privateRoomId);
    data.append("date", Date.now());
    fetch(searchUrl, {
        "method": "POST",
        "body": data,
    }).then(response => response.json())
        .then(data => {
            generalResults = data["results"];

            if (typeof generalResults !== "undefined" && generalResults.length !== 0) {
                generalPages = createPagination(generalResults, "general");
                removeChildren(resultList);
                printItems(searchItem, resultList, generalPages[currentGeneralPage]);
                document.getElementById("general_page_" + currentGeneralPage).classList.add("active");

                document.getElementById("general-pagination").hidden = false;
            }
        });
});

// Inspired from https://stackoverflow.com/a/67292763
function createPagination(data, index) {
    pages = paginate(data, page_size);

    $("#" + index + "-list li:not(:first-child):not(:last-child)").remove();

    let li = document.getElementById(index + "-next-page");
    pages.forEach((element, i) => {
        var pageLi = document.createElement("li");
        pageLi.className = "page-item list-item " + index;
        pageLi.id = index + '_page_' + i;
        pageLi.setAttribute("onclick", "pageChange('" + index + "', " + i + ")");

        var a = document.createElement("a");
        a.className = "page-link";
        a.innerText = i + 1;

        pageLi.appendChild(a);
        li.parentNode.insertBefore(pageLi, li.previousSibling);
    });

    return pages;
}

function nextPage(index) {
    switch (index) {
        case "general":
            if (generalPages.length - 1 > currentGeneralPage) {
                currentGeneralPage = currentGeneralPage + 1;
            }
            pageChange(index, currentGeneralPage);
            break;
        default:
            break;
    }
}

function previousPage(index) {
    switch (index) {
        case "general":
            if (generalPages.length > currentGeneralPage && currentGeneralPage != 0) {
                currentGeneralPage = currentGeneralPage - 1;
            }
            pageChange(index, currentGeneralPage);
            break;

        default:
            break;
    }
}

function pageChange(index, page) {
    switch (index) {

        case "general":
            currentGeneralPage = page;
            resultList.innerHTML = "";
            Object.values(document.getElementsByClassName("list-item " + index)).forEach(element => {
                element.classList.remove("active");
            })
            document.getElementById(index + "_page_" + page).classList.add("active");

            page = generalPages[page];
            printItems(searchItem, resultList, page);
            break;

        default:
            break;
    }
}

function paginate(arr, size) {
    return arr.reduce((acc, val, i) => {
        let idx = Math.floor(i / size)
        let page = acc[idx] || (acc[idx] = [])
        page.push(val)
        return acc
    }, [])
}

function printItems(printFunc, listElement, items) {
    Object.values(items).forEach((element, index) => {
        var item = printFunc(element, index);
        listElement.appendChild(item);
    });
}

function searchItem(result, index) {
    var item_div = document.createElement("div");
    item_div.className = "list-group-item rounded-3 py-3";

    var passage = document.createElement("p");
    passage.className = "mb-1";

    var title = document.createElement("b");
    title.innerHTML = result["title"];
    passage.appendChild(title);
    passage.appendChild(document.createElement("br"));

    var snippet = generateSnippet(result["body"], "search-" + index);
    passage.appendChild(snippet);

    var extend_button = generateSeeMoreButton("search-" + index, "button-search-" + index);
    passage.appendChild(extend_button);

    item_div.appendChild(passage)

    return item_div;
};

function toggleText(spanId) {
    var showExtendedSnippet = document.getElementById(spanId);
    var points = document.getElementById("points-" + spanId);

    if (showExtendedSnippet.style.display === "none") {
        points.style = "display: none;";
        showExtendedSnippet.style = "display: inline;";
        event.target.innerHTML = "See less";
    } else {
        points.style = "display: inline;";
        showExtendedSnippet.style = "display: none;";
        event.target.innerHTML = "See more";
    }
};

function generateSeeMoreButton(spanId, buttonId) {
    var extend_button = document.createElement("button");
    extend_button.id = buttonId;
    extend_button.type = "button";
    extend_button.className = "btn btn-link";
    extend_button.innerText = "See more";
    extend_button.setAttribute("onclick", "toggleText('" + spanId + "')");
    return extend_button;
};

function generateSnippet(text, spanId) {
    passage_text = text.split(/\W+/);
    var snippet = document.createElement("p");
    snippet.innerHTML = passage_text.slice(0, 14).join(" ");

    var span = document.createElement("span");
    span.id = "points-" + spanId;
    span.innerHTML = " ...";
    snippet.appendChild(span);

    var extended_snippet = document.createElement("span");
    extended_snippet.id = spanId;
    extended_snippet.className = "collapse";
    extended_snippet.innerHTML = " " + passage_text.slice(14).join(" ");
    extended_snippet.style = "display: none;";
    snippet.appendChild(extended_snippet);
    return snippet;
};

const removeChildren = (parent) => {
    while (parent.lastChild) {
        parent.removeChild(parent.lastChild);
    }
};


function searchProducts() {
    var searchQuery = document.getElementById("search-products");
    var filter = searchQuery.value.toUpperCase();
    var productsList = document.getElementById("products-list");
    var products = productsList.getElementsByClassName("card mb-3");

    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < products.length; i++) {
        var productDescription = products[i].getElementsByClassName("card-body")[0].innerText;
        if (productDescription.toUpperCase().indexOf(filter) > -1) {
            products[i].style.display = "";
        } else {
            products[i].style.display = "none";
        }
    }
}