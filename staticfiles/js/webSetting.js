const expandWebsetting = document.getElementById("expand-websetting");
const expandWebcontent = document.getElementById("expand-webcontent");

expandWebsetting.addEventListener("click", () => {
  if (expandWebcontent.classList.contains("expanded")) {
    expandWebcontent.classList.remove("expanded");
  } else {
    expandWebcontent.classList.add("expanded");
  }
});
