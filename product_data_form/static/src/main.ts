import { initMainPage } from "./pages/main_page";
import { initProductRegister } from "./pages/product_register";

document.addEventListener("DOMContentLoaded", () => {
  const currentPage = window.location.pathname;

  if (currentPage === "/" || currentPage === "/index.cgi/") {
    initMainPage();
  } else if (currentPage.includes("register")) {
    initProductRegister();
  }
});
