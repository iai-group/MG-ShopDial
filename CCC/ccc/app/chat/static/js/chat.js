// https://github.com/alexsmartens/simple-chat-app/blob/master/static/js/chat_client.js

let user = JSON.parse(document.getElementById("chat_client").getAttribute("user")),
    currentRoomName = document.getElementById("chat_client").getAttribute("room"),
    scenario = JSON.parse(document.getElementById("chat_client").getAttribute("scenario")),
    socket = io.connect("https://gustav1.ux.uis.no:81/chat", { path: window.url_prefix + "/socket.io/" });     // window.location.href

let timer;
let countdown = 1020;

function updateUrl() {
    let regex = /\/\d+$/g;

    if (scenario.id !== undefined) {
        if (document.URL.match(regex) === null) {
            history.replaceState(null, null, document.URL + "/" + scenario.id);
        } else {
            history.replaceState(null, null, String(document.URL).replace("/\/\d+$/i", "/" + scenario.id));
        }
    }
}

function idleTimer() {
    // Adapted from https://gist.github.com/gerard-kanters/2ce9daa5c23d8abe36c2
    var t;

    window.onmousemove = resetTimer;
    window.onmousedown = resetTimer;
    window.onclick = resetTimer;
    window.onscroll = resetTimer;
    window.onkeypress = resetTimer;

    function resetTimer() {
        clearTimeout(t);
        t = setTimeout(function () { leaveChat(user.user_id, user.role, currentRoomName); }, 90000);  // time is in milliseconds (1000 is 1 second)
    }
}

if (user.role === "1") {
    // Automatically log out the assistant if inactive
    idleTimer();
}

// socket.io events handlers //

// OnFirstConnection
socket.on("connect", function () {
    updateUrl();
    joinRoom(currentRoomName);
});

// socket.on("connected", function (message) {
//     $("div.msg-wrapper").append(
//         "<div class='bg-white fst-italic text-dark'>" +
//         message.username + " joined the chat." +
//         "</div>"
//     );
// });

socket.on("disconnected", function () {
    if (timer == null && Object.keys(scenario).length !== 0) {
        startTimer();
    }
});

socket.on("room-status", function (message) {
    if (message.close == true) {
        // Send the user back to lobby if the assistant decides to leave the chat room.
        $("#info-log").html('<div class="alert alert-warning alert-dismissible fade show" ' +
            'role="alert">All other participants left the room. You will receive a token and be ' +
            'redirected to the lobby shortly.<button type="button" class="btn-close" ' +
            'data-bs-dismiss="alert" aria-label="Close"></button></div>'
        );
        $("#send").attr("disabled", "");
        $("#submit-search").attr("disabled", "");
        setTimeout(function () {
            leaveChat(user.user_id, user.role, currentRoomName);
        }, 5000);
    }
    else if (message.is_full == true) {
        $("#send").removeAttr("disabled");
        $("#submit-search").removeAttr("disabled");
        if (timer == null) {
            startTimer();
        }
    } else {
        $("#send").attr("disabled", "");
        $("#submit-search").attr("disabled", "");
        $("div.msg-wrapper").empty();
        resetTimer();
    }
});

// Receive a message
socket.on("message", function (msg2client) {
    if (typeof msg2client.msg == "string") {
        // Message content and style
        displayMessage(msg2client);
        $("#isTyping").html("");
    } else
        console.error("Received message has unexpected content");
});

socket.on("redirect", function (message) {
    // Redirect to url send by the server.
    if (message.token !== undefined && message.token !== "") {
        alert("Copy the conversation token in the task form on mturk.\nConversation token: " + message.token)
        setCookie("convToken", "", 1);
    }
    window.location.href = window.url_prefix + message.url;
});

socket.on("countdown", function (message) {
    // Update countdown timer.
    countdown = message["countdown"]
    $("#timer").html(message["time"]);
    timerElement = document.getElementById("timer");
    timerElement.className = "badge bg-success rounded-pill";
});

socket.on("reset-countdown", function () {
    // Reset countdown timer.
    $("div.msg-wrapper").empty();
    resetTimer();
});

socket.on("show-history", function (data) {
    $("div.chat_msg").remove();
    var messages = data.messages;
    for (index = 0; index < messages.length; index++) {
        displayMessage(messages[index]);
    }
    if (data.room_status) {
        $("#info-log").html(
            "<div class='bg-white fst-italic text-dark'>The chat has started.</div>"
        );
    }
});

socket.on("private-room-id", function (privateRoomId) {
    $("#private-room-id").attr("value", privateRoomId);
    setCookie("convToken", privateRoomId, 20);
});

socket.on("share-scenario", function (data) {
    scenario = JSON.parse(data.scenario);
    updateUrl();
});

socket.on("chat-timeout", function () {
    resetTimer();
    $("#info-log").html('<div class="alert alert-warning alert-dismissible fade show" ' +
        'role="alert">The time for this conversation is elapsed. You will be ' +
        'redirected to the lobby shortly.<button type="button" class="btn-close" ' +
        'data-bs-dismiss="alert" aria-label="Close"></button></div>'
    );
    setTimeout(function () {
        leaveChat(user.user_id, user.role, currentRoomName);
    }, 15000);
})

socket.on("is-typing", function (data) {
    if (user.username != data.username && data.msg_length > 0) {
        $("#isTyping").html("Someone is typing...");
    } else {
        $("#isTyping").html("");
    }
});

// OnSendMessageClicked function
$("#send").click(function (e) {
    text = $("#msg_text").val();

    if (text) {
        let msg2server = {
            from: user.username,
            msg: text,
            room_id: currentRoomName,
            date: Date.now(),
            scenario: scenario,
        };
        socket.emit("server_receive", msg2server);

        msg2server.private_room_id = document.getElementById("private-room-id").value;
        $.ajax({
            type: "POST",
            url: "/woz/chat/save",
            contentType: "application/json;charset=UTF-8",
            data: JSON.stringify({ "data": msg2server })
        });
    }
    $("#msg_text").val("");
});

function keyPressed(event) {
    if (event.keyCode == 13) {
        $("#send").click();
    }
}

$("#stalling").click(function (e) {
    var stalling_msg = this.innerText;
    document.getElementById("msg_text").value = stalling_msg;
});

function typing() {
    var val = document.getElementById("msg_text").value;
    socket.emit("typing", { username: user.username, length: val.length, room_id: currentRoomName });
}

function displayMessage(msg2client) {
    let msg_inf = {
        bg_type: msg2client.from === user.username ? "bg-dark text-light bg-opacity-75" : msg2client.from ? "bg-light text-dark" : "bg-transparent fst-italic text-dark ",
        style: msg2client.from === user.username ? "margin-left: 30%; " : "margin-right:30%; ",
        icon: msg2client.from === user.username ? "bi-person-fill" : msg2client.from ? "bi-person" : "",
        msg: msg2client.msg,
    };

    let msg_html = "<div class='chat_msg " + msg_inf.bg_type + "' style='" + msg_inf.style + " word-wrap: break-word;'>";
    try {
        let url = new URL(msg_inf.msg);
        msg_html = msg_html + "<img src='" + url + "' style='max-height:280px;max-width:280px;height: auto;'>";
    } catch (_) {
        msg_html = msg_html + "<i class='bi " + msg_inf.icon + "'></i>  " + msg_inf.msg;
    }
    msg_html = msg_html + "</div>";

    $("div.msg-wrapper").append(msg_html);
}

function joinRoom(roomName) {
    socket.emit(
        "join",
        {
            "room_id": roomName,
            "scenario": scenario,
        }
    );
};

function leaveChat(user_id, role, roomName, privateRoomId, checklist) {
    if (privateRoomId === undefined) {
        privateRoomId = document.getElementById("private-room-id").value;
    }
    if (checklist === undefined) {
        checklist = $("input[name=checklist]:checked").map(function () {
            return this.value;
        }).get();
    }

    socket.emit(
        "leave",
        {
            "user_id": user_id,
            "role": role,
            "room_id": roomName,
            "private_room_id": privateRoomId,
            "checklist": JSON.stringify(checklist),
        }
    );


};

function startTimer() {
    // var countdown = 900;

    timer = setInterval(function () {
        countdown--;

        var minutes = Math.floor(countdown / 60);
        var seconds = countdown % 60;

        remaining_time = "00:" + String(minutes).padStart(2, '0') + ":" + String(seconds).padStart(2, '0');
        socket.emit('timer', { "time": remaining_time, "room_id": currentRoomName, "countdown": countdown });

        if (countdown === 0) {
            socket.emit('ctimeout', { "room_id": currentRoomName });
            clearInterval(timer);
        }
    }, 1000);
};

function resetTimer() {
    clearInterval(timer);
    countdown = 1020;
    $("#timer").html("00:17:00");
    timerElement = document.getElementById("timer");
    timerElement.className = "badge bg-danger rounded-pill";
};


let leaveUrl = document.getElementById("chat_client").getAttribute("leave-url");

$(document).on("submit", "#chat-checklist", function (event) {
    event.preventDefault();

    var data = new FormData(this);
    fetch(leaveUrl, {
        "method": "POST",
        "body": data,
    }).then(response => {
        if (response.redirected) {
            window.location = response.url;
        } else {
            return response.json();
        }
    }).then(data => {
        if (confirm(data["msg"])) {
            leaveChat(user.user_id, user.role, currentRoomName);
        }
    })
});


// When the user scrolls the page, execute stickHeader 
window.onscroll = function () { stickHeader() };

// Get the header
var header = document.getElementById("room-info");
// Get the offset position of the navbar
var sticky = header.offsetTop;

// Add the sticky class to the header when you reach its scroll position. Remove "sticky" when you leave the scroll position
function stickHeader() {
    if (window.pageYOffset > sticky) {
        header.classList.add("sticky");
    } else {
        header.classList.remove("sticky");
    }
}