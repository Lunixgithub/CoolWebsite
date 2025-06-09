function goLogin() {
    window.location.href = "/login";
}

function goAbout() {
    window.location.href = "/about";

}



document.addEventListener("DOMContentLoaded", function () {
    const dropdownBtn = document.getElementById("dropdownMenuButton");
    const action1 = document.getElementById("action1");
    const action2 = document.getElementById("action2");
    const action3 = document.getElementById("action3");

    if (action1) {
        action1.addEventListener("click", function (e) {
            e.preventDefault();
            window.location.href = "/login"
        });
    }

    if (action2) {
        action2.addEventListener("click", function (e) {
            e.preventDefault();
            alert("Tach");
        });
    }

    if (action3) {
        action3.addEventListener("click", function (e) {
            e.preventDefault();
            document.body.style.backgroundColor = "lightblue";
        });
    }
});