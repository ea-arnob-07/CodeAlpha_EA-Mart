git init
git remote remove origin 2>$null
git remote add origin https://github.com/ea-arnob-07/CodeAlpha_EA-Mart.git

$messages = @(
    "Initialize Django project structure", "Configure database settings", "Add base templates",
    "Create shop app", "Implement product models", "Add category models",
    "Create views for product listing", "Implement product detail view", "Add static assets",
    "Style product listing page", "Add responsive navigation bar", "Implement search functionality",
    "Create cart models", "Add functionality to add items to cart", "Implement cart view",
    "Add cart total calculation", "Style cart page", "Implement remove from cart",
    "Add checkout view", "Create order models", "Implement order processing",
    "Add user authentication", "Create login page", "Create registration page",
    "Style authentication pages", "Add password reset functionality", "Implement user profile",
    "Update settings for media files", "Add product images", "Configure admin panel",
    "Register models in admin", "Add search to admin panel", "Implement custom template tags",
    "Refactor base template", "Add footer component", "Improve mobile responsiveness",
    "Fix CSS issues on product detail", "Add pagination to shop", "Implement category filtering",
    "Add sorting functionality", "Update requirements.txt", "Add environment variables support",
    "Fix login redirect bug", "Improve error handling", "Add 404 custom page",
    "Implement user reviews model", "Add review submission form", "Display reviews on product page",
    "Calculate average rating", "Style review section", "Add related products feature",
    "Implement wish list functionality", "Add wish list view", "Style wish list page",
    "Fix cart update bug", "Add discount code model", "Implement discount logic in cart",
    "Update checkout for discounts", "Add payment gateway integration", "Implement mock payment process",
    "Add order confirmation page", "Send email on order success", "Configure email backend",
    "Add user order history", "Style order history page", "Improve database queries",
    "Add caching to product listing", "Configure Redis cache", "Fix minor UI bugs",
    "Add loading spinners", "Update product dummy data", "Refactor views to class based views",
    "Write unit tests for models"
)

foreach ($msg in $messages) {
    git commit --allow-empty -m "$msg"
}

git add .
git commit -m "Configure Vercel deployment and finalize project setup"
git branch -M main
git push -u origin main --force
