<?php
include("includes/header.php");
include("config.php");

// Fetch all dessert recipes
$sql = "SELECT id, title, description, ingredients, instructions, image, created_at 
        FROM recipes 
        ORDER BY created_at DESC";
$result = $conn->query($sql);
?>

<h2>Dessert Recipes 🍰</h2>
<a href="add_recipe.php" class="btn">+ Add a Recipe</a>

<?php if ($result->num_rows > 0): ?>
    <div class="recipe-list">
        <?php while ($row = $result->fetch_assoc()): ?>
            <div class="recipe-card" style="border:1px solid #ccc; padding:15px; margin:15px 0; border-radius:8px; background:#f9fff9;">
                <h3><?= htmlspecialchars($row['title']); ?></h3>
                <p><strong>Description:</strong><br><?= nl2br(htmlspecialchars($row['description'])); ?></p>
                <p><strong>Ingredients:</strong><br><?= nl2br(htmlspecialchars($row['ingredients'])); ?></p>
                <p><strong>Instructions:</strong><br><?= nl2br(htmlspecialchars($row['instructions'])); ?></p>

                <?php if (!empty($row['image'])): ?>
                    <img src="uploads/<?= htmlspecialchars($row['image']); ?>" alt="Recipe Image" style="max-width:200px; margin-top:10px;">
                <?php endif; ?>

                <br><small>Posted on <?= $row['created_at']; ?></small>
            </div>
        <?php endwhile; ?>
    </div>
<?php else: ?>
    <p>No dessert recipes yet. Be the first to add one!</p>
<?php endif; ?>

<?php include("includes/footer.php"); ?>
