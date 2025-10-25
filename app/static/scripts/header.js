const openIdentitiesBtn = document.getElementById("toggle-identities");
const closeIdentitiesBtn = document.getElementById("close-identities");
const identitesContainer = document.getElementById("select-identity");
const mobileOptionsBtn = document.getElementById("show-mobile-options");
const mobileOptionsContainer = document.getElementById("mobile-nav-group");
const openFooterBtn = document.getElementById("open-footer");
const closeFooterBtn = document.getElementById("close-footer");
const footerContainer = document.querySelector("footer");

openIdentitiesBtn.onclick = () => {
    if (identitesContainer.classList.contains('show-all')) {
        openIdentitiesBtn.classList.remove('rotate-up');
        identitesContainer.classList.remove('show-all');
        return;
    }

    openIdentitiesBtn.classList.add("rotate-up");
    identitesContainer.classList.add("show-all");
};

closeIdentitiesBtn.onclick = () => identitesContainer.classList.remove("show-all");

mobileOptionsBtn.onclick = () => mobileOptionsContainer.classList.toggle("expanded");

openFooterBtn.onclick = () => {
    mobileOptionsContainer.classList.remove("expanded");
    footerContainer.classList.add("expanded");
};

closeFooterBtn.onclick = () => footerContainer.classList.remove("expanded");