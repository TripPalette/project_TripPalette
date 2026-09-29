const favorite = document.getElementById("favorite");

if (favorite) {

    favorite.addEventListener("click", function () {

        this.classList.toggle("active");

        if (this.classList.contains("active")) {
            this.innerHTML = "♥";
        } else {
            this.innerHTML = "♡";
        }

    });

}