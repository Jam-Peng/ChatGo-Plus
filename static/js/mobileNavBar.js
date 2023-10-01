const expandButton = document.getElementById("expand-button");
const expandContent = document.getElementById("expand-content");

expandButton.addEventListener("click", () => {
  if (expandContent.classList.contains("expanded")) {
    expandContent.classList.remove("expanded");
  } else {
    expandContent.classList.add("expanded");
  }
});
