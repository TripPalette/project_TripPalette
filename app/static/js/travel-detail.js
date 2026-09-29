document.addEventListener("DOMContentLoaded", () => {

    /* =====================================
       여행지 이미지
    ===================================== */

    const hero =
        document.querySelector(".travel-hero");


    if (hero) {

        const destinationId =
            hero.dataset.destinationId;


        const image =
            document.getElementById(
                "destination-image"
            );


        const loading =
            document.getElementById(
                "destination-image-loading"
            );


        if (destinationId) {

            /*
             * ⚠️
             * 여기의 API 주소는
             * 네가 현재 사용 중인
             * 비동기 이미지 API 주소로
             * 바꿔야 함.
             */

            fetch(
                `/destinations/api/${destinationId}/image`
            )
            .then(response => {

                if (!response.ok) {
                    throw new Error(
                        "여행지 이미지 요청 실패"
                    );
                }

                return response.json();

            })
            .then(data => {

                if (!data.image_url) {
                    throw new Error(
                        "이미지가 없습니다."
                    );
                }


                image.src =
                    data.image_url;


                image.onload = () => {

                    image.classList.add(
                        "loaded"
                    );

                    loading.style.display =
                        "none";

                };

            })
            .catch(error => {

                console.error(error);

                loading.textContent =
                    "이미지를 불러오지 못했습니다.";

            });

        }

    }



    /* =====================================
       숙소 이미지
    ===================================== */

    const stayCard =
        document.querySelector(
            ".stay-card"
        );


    if (stayCard) {

        const accommodationId =
            stayCard.dataset.accommodationId;


        const image =
            document.getElementById(
                "accommodation-image"
            );


        const loading =
            document.getElementById(
                "accommodation-image-loading"
            );


        if (
            accommodationId &&
            image
        ) {

            fetch(
                `/accommodations/api/${accommodationId}/image`
            )
            .then(response => {

                if (!response.ok) {
                    throw new Error(
                        "숙소 이미지 요청 실패"
                    );
                }

                return response.json();

            })
            .then(data => {

                if (!data.image_url) {
                    throw new Error(
                        "숙소 이미지가 없습니다."
                    );
                }


                image.src =
                    data.image_url;


                image.onload = () => {

                    loading.style.display =
                        "none";

                };

            })
            .catch(error => {

                console.error(error);

                loading.textContent =
                    "숙소 이미지를 불러오지 못했습니다.";

            });

        }

    }

});