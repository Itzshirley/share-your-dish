<?php include 'config.php'; ?>
<?php include 'includes/header.php'; ?>

<?php
if (isset($_GET['id'])) {
    $id = intval($_GET['id']);
    $result = $conn->query("SELECT * FROM recipes WHERE id=$id");
    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        echo "<div class='recipe-full'>";
        if ($row['image']) {
            echo "<img src='uploads/" . $row['image'] . "' alt='" . $row['title'] . "'>";
        }
        echo "<h2>" . $row['title'] . "</h2>";
        echo "<p><b>Description:</b> " . $row['description'] . "</p>";
        echo "<p><b>Ingredients:</b><br>" . nl2br($row['ingredients']) . "</p>";
        echo "<p><b>Instructions:</b><br>" . nl2br($row['instructions']) . "</p>";
        echo "<small>Posted on " . $row['created_at'] . "</small>";
        echo "</div>";
    } else {
        echo "<p>Recipe not found.</p>";
    }
} else {
    echo "<p>No recipe selected.</p>";
}
?>

<?php include 'includes/footer.php'; ?>
