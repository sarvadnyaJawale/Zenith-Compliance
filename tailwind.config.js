/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // HTML templates
    "./frontend/templates/**/*.html",
    "./frontend/templates/Dashboard/**/*.html",
    "./frontend/templates/partials/**/*.html",
    
    // JavaScript files
    "./frontend/static/js/**/*.js",
    "./frontend/static/js/about-us/**/*.js",
    "./frontend/static/js/contact-us/**/*.js",
    "./frontend/static/js/dashboard/**/*.js",
    "./frontend/static/js/features/**/*.js",
    "./frontend/static/js/home/**/*.js",
    "./frontend/static/js/sign-in/**/*.js",
    "./frontend/static/js/sign-up/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}