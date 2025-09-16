<?php include 'config.php'; ?>
<?php include 'includes/header.php'; ?>

<h2>Latest Recipes</h2>

<?php
$result = $conn->query("SELECT * FROM recipes ORDER BY created_at DESC LIMIT 5");
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        echo "<div class='recipe-card'>";
        if ($row['image']) {
            echo "<img src='uploads/" . $row['image'] . "' alt='" . $row['title'] . "'>";
        }
        echo "<h3><a href='view-recipe.php?id=" . $row['id'] . "'>" . $row['title'] . "</a></h3>";
        echo "<p>" . substr($row['description'], 0, 120) . "...</p>";
        echo "</div>";
    }
} else {
    echo "<p>No recipes yet. Be the first to share!</p>";
}
?>
<div class="container">
    <h1>Welcome to Share Your Dish 🍲</h1>
    <p>Discover amazing recipes or share your own with the community.</p>
    <a href="recipes.php" class="btn">Browse Recipes</a>
    <a href="add_recipe.php" class="btn">Add a Recipe</a>
</div>
<?php include 'includes/footer.php'; ?>

