console.log("Archivo main.js cargado");

const nav = document.querySelector("#nav");
const abrir = document.querySelector("#abrir");
const cerrar = document.querySelector("#cerrar");

abrir.addEventListener("click", () => {
    nav.classList.add("visible");
})

cerrar.addEventListener("click", () => {
    nav.classList.remove("visible");
})

function openModal(src) {
    const modal = document.getElementById("imageModal-standfree");
    const modalImg = document.getElementById("expandedImage-standfree");

    modal.style.display = "flex";
    modalImg.src = src;
}

function closeModal() {
    document.getElementById("imageModal-standfree").style.display = "none";
}

