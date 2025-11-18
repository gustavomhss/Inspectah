document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".flash").forEach((node) => {
    setTimeout(() => {
      node.classList.add("fade-out");
    }, 4000);
  });
});
