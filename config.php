<?php
$host = "localhost";
$user = "root"; // default XAMPP user
$pass = "";     // default XAMPP has no password
$db   = "share-your-dish";

$conn = new mysqli($host, $user, $pass, $db);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
