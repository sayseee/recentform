<?php
// Get the URL parameter from the query string
$url = isset($_GET['url']) ? $_GET['url'] : '';

// Check if the URL parameter is set and not empty
if (!empty($url)) {
    // Initialize a cURL session
    $ch = curl_init();

    // Set cURL options
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HEADER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); // Ignore SSL verification (not recommended in production)

    // Execute the cURL request
    $response = curl_exec($ch);

    // Check if there was an error during the cURL request
    if ($response === false) {
        // Output the cURL error
        echo 'Error: ' . curl_error($ch);
    } else {
        // Set the appropriate headers for CORS
        header('Content-Type: application/json');
        header('Access-Control-Allow-Origin: *'); // Adjust this based on your security requirements

        // Output the response
        echo $response;
    }

    // Close the cURL session
    curl_close($ch);
} else {
    // Output an error message if the URL parameter is not set or empty
    echo 'Error: URL parameter is missing or empty.';
}
?>
