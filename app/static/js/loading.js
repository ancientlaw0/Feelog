document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll("a[href]");
    const loader = document.getElementById("page-loader");
    
  
    if (loader) {
        loader.style.display = "none";
    }
    
    for (let link of links) {
       if (
                link.href.startsWith(window.location.origin) &&
                !link.href.includes("#") // skip anchor links
            ) {
            link.addEventListener("click", function () {
                if (loader) {
                    loader.style.display = "flex";
                }
            });
        }
    }
});


window.addEventListener("pageshow", function() {
    const loader = document.getElementById("page-loader");
    if (loader) {
        loader.style.display = "none";
    }
});