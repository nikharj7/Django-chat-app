// Connect to WebSocket
const roomName = 'your_room_name';  // Replace with actual room name/id
const chatSocket = new WebSocket(
    'ws://' + window.location.host +
    '/ws/chat/' + roomName + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    // Handle incoming message
    console.log(data);
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

// Send message through WebSocket
function sendMessage(message) {
    chatSocket.send(JSON.stringify({
        'message': message
    }));
}
