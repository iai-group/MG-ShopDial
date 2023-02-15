# Socket.io events

The socket.io server has 2 different namespaces: lobby and chat. The first one will process all events related to the lobby such as new available chat rooms and control access to them. The second processes the events related to the chat like the update of the countdown timer and sharing messages between participants. 
Socket.io has default events as for example: *connect*, *join*, and *disconnect*. Each namespace can process these events differently. 

## Client events
Following is the list of events that can be sent by a participant to the socket.io server. 

### Lobby namespace

*connect*: default event sent when a connection with the server is established. Always occurs when the page holding the JS script is loaded. The participant will be add to the list of online users.

*log_out*: event emitted when a participant hit the button *Log out*. The server will log out the participant and update the list of available rooms in the lobby if they are a shopping assistant.

*join*: event emitted when the socket joins a room (automatically joins a [default room](https://socket.io/docs/v4/rooms/#default-room)). 

*join_room*: event emitted when a participant click to join a chat room. The server will check if the participant can access the room. If for any reasons the room is not accessible, the participant will be informed and stay in the lobby.


### Chat namespace

*connect*: default event sent when a connection with the server is established. Always occurs when the page holding the JS script is loaded.

*disconnect*: default event fired when the socket connection is broken (*e.g.*, when refreshing a page).

*server_receive*: event sent when a participant sends a message in the chat. 

*join*: event fired when a participant is connected to a server. The participant joins a room associated with the chat room they are into.

*leave*: event sent to notify the server that the participant left the chat room.

*timer*: event fired every second to update the countdown timer associated with a chat room.

*ctimeout*: event sent when the time allocated for a conversation is elapsed.

*typing*: event fired when a participant is typing a message.

## Server events
Following is the list of events that can be sent by the socket.io server to participants that are either in the lobby or in chat rooms. 

### Lobby namespace

*connected*: add the participant to the list of online users and inform all participants in the lobby of a newcomer.

*disconnected*: remove participant from the list of online users and inform all participants in the lobby.

*joined*: event fired whenever a participant joins a chat room to update the list of available rooms in the lobby.

*redirect*: send to the client the URL to redirect to.

*room-status*: inform the clients in a specific chat room of its status (i.e., is the room full?)

*room-full*: event fired when the participant cannot access a chat room.

*countdown*: update the timer (for how long the room is still unavailable) of a specific room.

### Chat namespace

*connect*: event fired when a user is connected, the url of the page is updated with the scenario id if possible.

*disconnected*: start the timer if necessary after a disconnection.

*message*: share message sent from a participant to all the participants in the chat room.

*show-history*: event fired when a participant joins a chat room. If the participants in the room already had a conversation, the last 15 messages are displayed.

*room-status*: event triggered when a participant leaves the room to update front end and execute redirection if necessary.

*redirect*: send to the client the URL to redirect to.

*countdown*: event sent to update the countdown timer associated with a room. This event is sent to both namespace: lobby and chat.

*reset-countdown*: reset the conversation timer.

*chat-timeout*: event emitted to inform that the conversation has reached its end in regards to allocated time.

*private-room-id*: share the private room id  associated with a conversation, and save the value in a cookie.

*share-scenario*: share scenario associated with a conversation with the participants.

*is-typing*: inform the user that the other participant is typing.
