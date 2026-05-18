import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#17211b",
        moss: "#4f6f52",
        mint: "#d9f6e5",
        amber: "#f4c95d",
        coral: "#ef7b70",
        paper: "#f7f5ef",
      },
    },
  },
  plugins: [],
};

export default config;

