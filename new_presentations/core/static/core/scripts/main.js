const urls = 'http://127.0.0.1'
const port = 8000

//const urls = 'newpresentations.uksouth.cloudapp.azure.com'
//const port = 80

document.addEventListener("DOMContentLoaded", HomePageSetUp);

function HomePageSetUp() {
    if (window.innerWidth >= 768) {
        setUpScrollBar();
    }
    setUpCarousel();
}

// Get valid title
var titleInput = document.getElementById("myInput");
var mainForm = document.getElementById("appForm");
var allSupportedTitles;
var languageSelector = document.getElementById("lang");

titleInput.addEventListener('input', filterFunction);
function filterFunction() {
    const request = new XMLHttpRequest();

    request.onreadystatechange = function () {
        if (this.readyState == 4) {
            if (this.status == 200) {
                allSupportedTitles = JSON.parse(this.responseText)["titles"];
                const drop = document.getElementById("myDropdown");
                resetElement(drop);
                for (const option of allSupportedTitles) {
                    const btn = document.createElement('button');
                    btn.innerText = option;
                    btn.classList.add("option");
                    btn.addEventListener("click", function (e) {
                        titleInput.value = btn.innerText;
                        checkTitleExists();
                        resetElement(drop);
                    })
                    drop.appendChild(btn);
                }
                checkTitleExists();
            }
        }
    }

    request.open('GET', `${urls}:${port}/title?title=${titleInput.value}&language=${languageSelector.value}`);
    request.send();
}

function checkTitleExists() {
    let ok = false;
    for (const title of allSupportedTitles) {
        if (titleInput.value == title) {
            ok = true;
            break;
        }
    }

    resetElement(mainForm);

    if (!ok) {
        return;
    }

    const in0 = document.createElement('label');
    in0.innerText = "Number of slides";
    in0.classList.add("pad");

    const in1 = document.createElement('select');
    in1.setAttribute('id', 'numberOfSlides');

    const in01 = document.createElement('option');
    in01.setAttribute('value', '4-8');
    in01.innerText = "4-8";
    const in02 = document.createElement('option');
    in02.setAttribute('value', '8-12');
    in02.innerText = "8-12";
    const in03 = document.createElement('option');
    in03.setAttribute('value', '12-16');
    in03.innerText = "12-16";
    const in04 = document.createElement('option');
    in04.setAttribute('value', '16-18');
    in04.innerText = "16+";
    const in05 = document.createElement('option');
    in05.setAttribute('value', 'AI');
    in05.setAttribute('selected', true);
    in05.innerText = "Let AI decide (recomended)";

    in1.appendChild(in01);
    in1.appendChild(in02);
    in1.appendChild(in03);
    in1.appendChild(in04);
    in1.appendChild(in05);

    const in2 = document.createElement('label');
    in2.innerText = "Your name";

    const in3 = document.createElement('input');
    in3.setAttribute('type', 'text');
    in3.setAttribute('placeholder', 'Name');
    in3.setAttribute('required', 'true');
    in3.setAttribute('id', 'namename');

    const in4 = document.createElement('input');
    in4.setAttribute('type', 'submit');
    in4.setAttribute('value', 'START');
    in4.setAttribute('id', 'submit');

    mainForm.appendChild(in0);
    mainForm.appendChild(in1);
    mainForm.appendChild(in2);
    mainForm.appendChild(in3);
    mainForm.appendChild(in4);
}

// Create Presentation
mainForm.addEventListener('submit', function (e) {
    document.getElementById("submit").setAttribute('disabled', 'true');
    e.preventDefault();
    const request = new XMLHttpRequest();

    const finalTitle = document.getElementById("myInput").value;
    const finalLanguage = document.getElementById("lang").value;
    const finalNumSlides = document.getElementById("numberOfSlides").value;
    const finalName = document.getElementById("namename").value;

    request.onreadystatechange = function () {
        if (this.readyState == 4) {
            if (this.status == 200) {
                window.location.replace(`/download?presentation_name=${JSON.parse(this.responseText)["presentation"]}`);
            }
        }
    }

    request.open('GET', `${urls}:${port}/create?title=${finalTitle}&language=${finalLanguage}&slides=${finalNumSlides}&name=${finalName}`);
    request.send();
    showLoader();
});

function showLoader() {
    const appSection = document.getElementById('app');
    appSection.innerHTML = `<div class="loadingio-spinner-spinner-f4u3u8w9sjo"><div class="ldio-ehwdr0nm5dp">
    <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>
    </div></div> <div><p class='info'>We are getting your presentation ready</p></div>`
}

// Helper functions

function setUpScrollBar() {
    const screen = document.documentElement;
    document.addEventListener('scroll', () => $(".scrollBar2").css("height", (window.scrollY / (screen.scrollHeight - window.innerHeight)) * 90 + "%"));
}

function setUpCarousel() {
    $(".owl-carousel").owlCarousel({
        loop: true,
        margin: 10,
        autoplay: true,
        autoplayHoverPause: false,
        responsive: {
            0: {
                items: 1
            },
            768: {
                items: 3
            },
            1070: {
                items: 4
            }
        }
    });
}

function resetElement(element) {
    while (element.childElementCount > 2) {
        element.removeChild(element.lastChild);
    }
}

// Nav 2

const toggle2 = document.querySelector(".toggle");
const toggleBtn2 = document.querySelector(".toggle-btn");
const menu2 = document.querySelector(".menu");
const menuList2 = document.querySelector(".menu-list");
const menuItems2 = document.querySelectorAll(".menu-item");
var showMenu = false;

toggle2.addEventListener("click", toggleMenu);

function toggleMenu() {
    if (!showMenu) {
        toggleBtn2.classList.add("open");
        menu2.classList.add("open");
        menuList2.classList.add("open");
        menuItems2.forEach(item => item.classList.add("open"));

        showMenu = true;
    } else {
        toggleBtn2.classList.remove("open");
        menu2.classList.remove("open");
        menuList2.classList.remove("open");
        menuItems2.forEach(item => item.classList.remove("open"));

        showMenu = false;
    }
}