window.onload = function() {
    const socket = io("http://localhost:5000")

    socket.on("getQuery", (query) => {
        $(query["faces"]).each(function(idx, data) {
            $(".faces").append(`<img id="${data.id}" src="${data.imgPath}"/>`)
        });

        $(query["recon"]).each(function(idx, data) {

            // ----------------------------------------------------------------
            // archive
            // ----------------------------------------------------------------

            $(data["archive"]).each(function(idx, elem) {
                $(".archive").append(`<div><div class="popup" id="${elem.id}">${elem.url}</div></div>`);
            });

            // ----------------------------------------------------------------
            // analizer
            // ----------------------------------------------------------------

            $(data["ana"]).each(function(idx, elem) {

                const matchs = elem["matchs"]
                const parentDiv = document.createElement("div");
                // parentDiv.innerHTML = `${elem.url}`;

                $(matchs).each(function(idx, elematch) {
                    $.each(elematch, function(key, value) {
                        const childDiv = document.createElement("div")
                        childDiv.innerHTML = `<div class="popup" id="${elem.id}">${key}: ${value}`
                        parentDiv.append(childDiv)
                    })
                })

                $(".analizer").append(parentDiv);
            })
        })
    });

    // ----------------------------------------------------------------
    // Popup
    // ----------------------------------------------------------------

    $("#archive").on("click", "div", function(event) {
        const id = event.target.id;

        if (id) {
            $(this).css("background", "#e26060");
            $('.cd-popup').addClass('is-visible');
            $(".content").css("display", "none");
            $(".cd-popup-container").html(`<object type="text/html" data="${id}" ></object>`);
        }

    });

    $("#faces").on("click", "img", function(event) {
        const id = event.target.id;
        console.log(id);
        if (id) {
            $(this).css("background", "#e26060");
            $('.cd-popup').addClass('is-visible');
            $(".content").css("display", "none");
            $(".cd-popup-container").html(`<object type="text/html" data="${id}" ></object>`);
        }

    });

    $("#analizer").on("click", "div", function(event) {
        const id = event.target.id;

        if (id) {
            $(this).css("background", "#e26060");
            $('.cd-popup').addClass('is-visible');
            $(".content").css("display", "none");
            $(".cd-popup-container").html(`<object type="text/html" data="${id}" ></object>`);
        }

    });

    $('.cd-popup').on('click', function(event) {
        if ($(event.target).is('.cd-popup')) {
            $(this).removeClass('is-visible');
            $(".content").css("display", "");
        }
    });
    // ----------------------------------------------------------------
    // ----------------------------------------------------------------
}