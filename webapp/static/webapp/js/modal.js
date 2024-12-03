function openModal() {
    document.getElementById("imageModal-standfree").style.display = "block";
}

function closeModal() {
    document.getElementById("imageModal-standfree").style.display = "none";
}

let slideIndex = 1;
showSlides(slideIndex);

function plusSlides(n) {
    showSlides(slideIndex += n);
}

function currentSlide(n) {
    showSlides(slideIndex = n);
}

function showSlides(n) {
    let i;
    let slides = document.getElementsByClassName("mySlides");
    let thumbnails = document.querySelectorAll(".thumbnail-container img");
    let captionText = document.getElementById("caption");

    if (n > slides.length) { slideIndex = 1 }
    if (n < 1) { slideIndex = slides.length }

    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    for (i = 0; i < thumbnails.length; i++) {
        thumbnails[i].classList.remove("active");
    }

    slides[slideIndex - 1].style.display = "block";
    thumbnails[slideIndex - 1].classList.add("active");
    captionText.innerHTML = thumbnails[slideIndex - 1].alt;
}