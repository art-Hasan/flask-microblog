
// Add or remove class active to list element in nav-tabs.
var updateState = function() {
    var state = document.cookie.endsWith('1'),
        navTab = document.getElementById("nav-tabs"),
        tabs = navTab.getElementsByTagName("li");
    if (!state) {
        tabs[1].classList.remove("active")
        tabs[0].classList.add("active")
    } else {
        tabs[0].classList.remove("active")
        tabs[1].classList.add("active")
    }
}

window.addEventListener("load", updateState, false);