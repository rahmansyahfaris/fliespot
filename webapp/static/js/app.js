// Function to check the current button status
function checkButtonStatus() {
    fetch('/status')
        .then(response => response.json())
        .then(data => {
            const button = document.getElementById("action-button");
            const header = document.getElementById("header"); // Get the header element

            button.innerText = data.button_text;
            button.setAttribute("data-action", data.next_action);
            header.innerText = data.header_text; // Update the header text
        })
        .catch(error => console.error('Error:', error));
}

// Function to handle button clicks
function handleButtonClick() {
    const button = document.getElementById("action-button");
    const action = button.getAttribute("data-action");

    fetch(action, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            const header = document.getElementById("header"); // Get the header element

            button.innerText = data.button_text;
            button.setAttribute("data-action", data.next_action);
            header.innerText = data.header_text; // Update the header text
        })
        .catch(error => console.error('Error:', error));
}

// Initialize polling and set up button click listener
window.onload = () => {
    checkButtonStatus();
    setInterval(checkButtonStatus, 1000);

    const button = document.getElementById("action-button");
    button.addEventListener('click', handleButtonClick);
};
