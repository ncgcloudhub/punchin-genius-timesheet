/* GPT Submit Command Script */

    function submitTimeCommand() {
        // Get the user's input
        const userInput = document.getElementById('time_command').value;

        // Send an XMLHttpRequest to the Flask server to interpret the command
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/process_time_entry', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

        xhr.onload = function() {
            if (this.status === 200) {
                const jsonResponse = JSON.parse(this.responseText);
                const messagesDiv = document.querySelector('.gpt-messages');
                messagesDiv.innerHTML += `<div class="user-message">${userInput}</div>`;
                
                // After interpreting the command, send a second XMLHttpRequest to actually perform the clock-in or clock-out action
                const actionEndpoint = jsonResponse.action === "clock_in" ? "/clock_in" : "/clock_out";
                const xhr2 = new XMLHttpRequest();
                xhr2.open('POST', actionEndpoint, true);
                xhr2.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');

                xhr2.onload = function() {
                    if (this.status === 200) {
                        const actionResponse = JSON.parse(this.responseText);
                        const message = actionResponse.message || "Action successful.";
                        messagesDiv.innerHTML += `<div class="bot-message">${message}</div>`;
                    }
                };

                // Send the time as JSON data to the appropriate endpoint
                xhr2.send(JSON.stringify({ time: jsonResponse.time }));
            }
        };

        // Send the time command as form data
        xhr.send(`time_command=${encodeURIComponent(userInput)}`);
    }