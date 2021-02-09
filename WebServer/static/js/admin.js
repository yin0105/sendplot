$(document).ready(function() {
    console.log("begin");
    if (typeof(data) != "undefined" && data !== null) {
        console.log("yes");
        if (data == "ok") {
            $("#alert").css("display", "none")
        } else {
            // $("#alert").css("display", "block")
            alert("Wrong user name or password");
        }
        console.log("data = " + data);
    } else {
        console.log("no");
    }
    
    $('#btn_gohome').on('click', function() {
        window.location.href = "/";
    });
    
    $('#btn_del').on('click', function() {
        console.log("btn_del clicked")
        $.ajax({
            url: '/api/json_del'
        }).done(function(data) {
            console.log("json del ok")
            if (data == "ok") {
                // $("#alert").css("display", "block")
                alert("The data of all json files are removed.");
            } else {
                $("#alert").css("display", "none")
            }
        }).fail(function(data) {
            console.log("json del failed")
        });
    });

});

//# sourceMappingURL=app.js.map
