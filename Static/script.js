document.addEventListener("DOMContentLoaded", function () {
  const box = document.getElementById("missionBox");
  const toggleBtn = document.querySelector(".toggle-mission");

  function toggleMission() {
    const isVisible = box.classList.toggle("show");

    if (isVisible) {
      toggleBtn.style.opacity = "0";
      setTimeout(() => (toggleBtn.style.display = "none"), 300);
    } else {
      toggleBtn.style.display = "block";
      setTimeout(() => (toggleBtn.style.opacity = "1"), 10);
    }
  }

  // Expose toggle function globally
  window.toggleMission = toggleMission;

  // Close if clicked outside
  document.addEventListener("click", function (event) {
    if (
      box.classList.contains("show") &&
      !box.contains(event.target) &&
      !toggleBtn.contains(event.target)
    ) {
      box.classList.remove("show");
      toggleBtn.style.display = "block";
      setTimeout(() => (toggleBtn.style.opacity = "1"), 10);
    }
  });
});
