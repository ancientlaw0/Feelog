// Show image preview when a user selects a file from the input.

document.getElementById("attach-image").addEventListener("change", function(event) {
  const file = event.target.files[0];
  const previewBox = document.getElementById("file-preview");
  const previewImg = document.getElementById("preview-img");

  if (file && file.type.startsWith("image/")) {
    const reader = new FileReader();
    reader.onload = function (e) {
      previewImg.src = e.target.result;
      previewBox.style.display = "block";
    };
    reader.readAsDataURL(file);
  } else {
    previewBox.style.display = "none";
  }
});

document.getElementById("remove-preview").addEventListener("click", function () {
  const fileInput = document.getElementById("attach-image"); 
  const previewBox = document.getElementById("file-preview");
  const previewImg = document.getElementById("preview-img");

  fileInput.value = "";              
  previewImg.src = "#";                
  previewBox.style.display = "none";   
});
