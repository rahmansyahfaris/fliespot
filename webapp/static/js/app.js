document.addEventListener("DOMContentLoaded", function() {
    // Add event listener to toggle button
    const toggleButton = document.getElementById("toggle-advanced-configs");
    const advancedConfigs = document.getElementById("advanced-configs");
    const configDisplay = document.getElementById("config-display");
    const operationDisplay = document.getElementById("operation-display");
    const operationStatus = document.getElementById("operation-status");
    const operationButton = document.getElementById("operation-button");
    const imgElement = document.getElementById("dynamic-image");
    const detectionClasses = document.getElementById("detection-classes");
    const classImg = document.getElementById("class-img");

    toggleButton.addEventListener("click", function() {
        // Toggle the visibility of the advanced configurations
        if (advancedConfigs.style.display === "none") {
            advancedConfigs.style.display = "block";
        } else {
            advancedConfigs.style.display = "none";
        }
    });

    function initializeImage() {
        const selectedValue = detectionClasses.value; // Get the initial value of the combobox
        const imageMap = {
            phone: "static/images/phone_icon.png",
            bottle: "static/images/bottle_icon.png",
            key: "static/images/key_icon.png",
            wallet: "static/images/wallet_icon.png"
        };
    
        classImg.src = imageMap[selectedValue]; // Set the initial image source
        classImg.alt = selectedValue.charAt(0).toUpperCase() + selectedValue.slice(1); // Set the alt text
    }

    // Add an event listener for changes to the combobox
    detectionClasses.addEventListener("change", function () {
        // Map the selected value to the corresponding image
        const selectedValue = detectionClasses.value;
        const imageMap = {
            phone: "static/images/phone_icon.png",
            bottle: "static/images/bottle_icon.png",
            key: "static/images/key_icon.png",
            wallet: "static/images/wallet_icon.png"
        };

        // Update the image src attribute
        classImg.src = imageMap[selectedValue];
        classImg.alt = selectedValue.charAt(0).toUpperCase() + selectedValue.slice(1); // e.g., "Phone"
    });

    // Add event listener to the form for submitting configurations
    document.getElementById("submit-form").addEventListener("click", async function() {
        // Collect data from both forms
        const formData = new FormData(document.getElementById("config-form"));

        // Append data from the second form (config-form-classes)
        const classFormData = new FormData(document.getElementById("config-form-classes"));
        classFormData.forEach((value, key) => {
            formData.append(key, value);
        });

        // Send the combined form data to the backend via a POST request
        const response = await fetch("/set_configs", {
            method: "POST",
            body: formData
        });

        // Parse the JSON response
        const result = await response.json();

        // Display the success message
        const notificationElement = document.getElementById("notification");
        const notificationMessage = document.getElementById("notification-message");
        notificationMessage.innerText = result.message;

        // Make the notification appear
        notificationElement.style.display = "block";
    });

    // Add event listener to the "X" button to close the notification
    document.getElementById("close-notification").addEventListener("click", function() {
        const notificationElement = document.getElementById("notification");
        notificationElement.style.display = "none"; // Hide the notification
    });

    document.getElementById("crazy-start").addEventListener("click", async function() {
        try {
            const response = await fetch("/crazy_start"); // This triggers a GET request
            const data = await response.json();
            console.log("Status:", data.status);
        } catch (error) {
            console.error("Error occurred:", error);
        }
    });

    document.getElementById("operation-button").addEventListener("click", async function() {
        try {
            const response = await fetch("/crazy_stop"); // This triggers a GET request
            const data = await response.json();
            console.log("Status:", data.status);
        } catch (error) {
            console.error("Error occurred:", error);
        }
    });

    // 1 Second Interval Refresh
    setInterval(async function () {
        try {
            const response = await fetch("/crazy_check");
            const data = await response.json();
            if (data.error_occurred === true) {
                operationDisplay.style.display = "block"
                operationButton.style.display = "none"
                operationStatus.textContent = "Error occurred..."
                imgElement.src = "static/images/error.png"
            } else {
                if (data.ready === true) {
                    operationDisplay.style.display = "none"
                    configDisplay.style.display = "block"
                } else {
                    configDisplay.style.display = "none"
                    operationDisplay.style.display = "block"
                    if (data.aborted === true) {
                        operationButton.style.display = "none"
                        if (data.detected === true) {
                            operationButton.style.display = "none"
                            operationStatus.textContent = "Finishing..."
                            imgElement.src = "static/images/object_detected.gif"
                        } else {
                            operationButton.style.display = "none"
                            operationStatus.textContent = "Aborting..."
                            imgElement.src = "static/images/error.png"
                        }
                    } else {
                        if (data.detected === true) {
                            operationStatus.textContent = "Object is Detected!"
                            operationButton.textContent = "Finish"
                            operationButton.style.backgroundColor = "#0ec992"
                            imgElement.src = "static/images/object_detected.gif"
                        } else {
                            operationStatus.textContent = "Operating..."
                            operationButton.textContent = "Abort"
                            operationButton.style.backgroundColor = "#e14444"
                            imgElement.src = "static/images/operating.gif"
                        }
                        operationButton.style.display = "block"
                    }
                }
            }
            console.log("Status:", data);
        } catch (error) {
            console.error("Error occurred:", error);
        }

    }, 1000); // Interval in milliseconds (1 second)

    initializeImage()
});
