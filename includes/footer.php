    </main>
  <footer>
    <p>© <?php echo date("Y"); ?> Share Your Dish | Cook. Share. Inspire.</p>
  </footer>

  <!-- Mobile Menu Script -->
  <script>
    const toggle = document.getElementById('menu-toggle');
    const nav = document.getElementById('navbar');
    toggle.addEventListener('click', () => {
      nav.classList.toggle('active');
    });
  </script>
</body>
</html>
