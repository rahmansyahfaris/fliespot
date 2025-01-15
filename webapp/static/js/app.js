document.addEventListener("DOMContentLoaded", function() {
    // Add event listener to toggle button
    const toggleButton = document.getElementById("toggle-advanced-configs");
    const advancedConfigs = document.getElementById("advanced-configs");

    toggleButton.addEventListener("click", function() {
        // Toggle the visibility of the advanced configurations
        if (advancedConfigs.style.display === "none") {
            advancedConfigs.style.display = "block";
        } else {
            advancedConfigs.style.display = "none";
        }
    });

    // Add event listener to the form for submitting configurations
    document.getElementById("config-form").addEventListener("submit", async function(event) {
        event.preventDefault();  // Prevent the form from submitting normally

        // Collect all form data
        const formData = new FormData(document.getElementById("config-form"));
        
        // Send the form data to the backend via a POST request
        const response = await fetch("/set_configs", {
            method: "POST",
            body: formData
        });

        // Parse the JSON response
        const result = await response.json();

        // Display the success message
        document.getElementById("notification").innerText = result.message;
    });


    // 1 Second Interval Refresh
    //setInterval(function () {}, 1000); // Interval in milliseconds (1 second)
});
