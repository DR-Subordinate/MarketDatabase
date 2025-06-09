import { initMainPage } from "./pages/main_page";

document.addEventListener("DOMContentLoaded", () => {
  const currentPage = window.location.pathname;

  if (currentPage === "/" || currentPage === "/index.cgi/") {
    initMainPage();
  }
});
