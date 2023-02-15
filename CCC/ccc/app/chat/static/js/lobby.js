let user = $("#user").data("user");

let socket = io.connect("https://gustav1.ux.uis.no:81/lobby", { path: window.url_prefix + "/socket.io/" });

socket.on("connected", function (message) {
    updateRooms(JSON.parse(message.rooms));

    // $("ul.lobby-log").append(
    //     "<li class='list-group-item' id='online-'" + message.username + "><span class='icon-green'></span>  " +
    //     message.username + "</li>"
    // );
});

socket.on("disconnected", function (message) {
    if ("rooms" in message) {
        updateRooms(JSON.parse(message.rooms));
    }
    // $("ul.lobby-log").append(
    //     "<li class='list-group-item'>" +
    //     message.username + " left the lobby." +
    //     "</li>"
    // );
});

socket.on("room-full", function (message) {
    alert("Sorry the room " + message.room_id + " is not available at the moment.");
    // toggleButton(message.room_id);
});

socket.on("joined", function (message) {
    updateRooms(JSON.parse(message.rooms));
});

socket.on("redirect", function (message) {
    // Redirect to url send by the server.
    window.location.href = window.url_prefix + message.url;
});

socket.on("countdown", function (message) {
    // Update countdown timer for a room.
    var roomButton = document.getElementById(message["room_id"]);
    var childElement = roomButton.children[0];

    if (childElement) {
        childElement.innerHTML = message["time"];
    }
    else {
        var span = document.createElement("span");
        span.className = "badge bg-secondary";
        span.innerHTML = message["time"];
        roomButton.textContent += "\t";
        roomButton.appendChild(span);
    }
});

function updateRooms(rooms) {
    // Update the list of rooms when a participant joins or leaves the lobby.
    var parentDiv = document.getElementById("rooms");

    var div = document.createElement("div");
    div.id = "rooms";

    for (let index = 0; index < rooms.length; index++) {
        var room = rooms[index];

        id = room.room_id.split(":").at(-1);
        if (user.role == "1" && user.user_id != id) {
            continue;
        }
        var button = document.createElement("button");
        if (user.role == "1") {
            button.className = "btn btn-success";
        } else if (room.is_full == false && room.has_assistant == true) {
            button.className = "btn btn-success";
        } else {
            button.className = "btn btn-danger";
            button.setAttribute("disabled", "");
        }
        button.id = room.room_id;
        button.innerHTML = room.room_id;
        button.style = "margin-left: 10px";
        button.setAttribute("onclick", "joinChat(" + user.user_id + ", " + user.role + ", '" + room.room_id + "')");

        div.appendChild(button);

    }

    parentDiv.replaceWith(div);
}

function joinChat(user_id, role, room_id) {
    // Join a chat room.
    socket.emit(
        "join_room",
        {
            "user_id": user_id,
            "role": role,
            "room_id": room_id,
        }
    );
}

function toggleButton(button_id) {
    // Enable/Disable button.
    var button = document.getElementById(button_id);
    button.disabled = !button.disabled;
}

function logout() {
    socket.emit(
        "log_out"
    );
}
