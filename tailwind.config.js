/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./chat/templates/chat/*.html",
    "./*/templates/*/*.html",
    "./templates/*.html",
  ],
  theme: {
    fontFamily: {
      body: ["Roboto"],
    },
    extend: {},
    fontSize: {
      xs: ".75rem",
      sm: ".88rem",
      base: "1rem",
      lg: "1.2rem",
      xl: "1.5rem",
    },
  },
  plugins: [],
};
