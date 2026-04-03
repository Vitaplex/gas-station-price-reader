document.addEventListener("DOMContentLoaded", () => {
    const location = window.location.href;
    initDarkMode(location);
    imageElement.addEventListener("change", async () => { await readFile() });
    cameraElement.addEventListener("change", async () => { await readFile() });
    document.getElementById("uploadButton").addEventListener("click", async () => { await readFile() }); 3
});

let latitude = 0;
let longitude = 0;

async function readFile() {

    navigator.geolocation.getCurrentPosition(
        (position) => {
            var { latitude, longitude } = position.coords;
            console.log(latitude, longitude);
        },
        (err) => {
            console.error("Location error:", err);
        }
    );

    let cameraElement = document.getElementById("cameraElement");
    let imageElement = document.getElementById("imageElement");

    if (imageElement.files.length == 0) {
        imageElement = cameraElement
    }

    for (let i = 0; i < imageElement.files.length; i++) {
        const curFile = imageElement.files[i];

        if (!curFile) { alert("No file selected!"); return; }

        const reader = new FileReader();

        let fileContent;

        reader.onload = async function (e) {
            await sendFile(e.target.result);
        };

        reader.readAsDataURL(curFile);
    }
}

async function sendFile(content) {
    const format = dropdown.value;

    const response = await fetch(`/parse-gas-station-picture?format=${format}`, {
        method: "POST",
        headers: { "User-Coordinates": `${latitude}, ${longitude}` },
        body: content
    })

    const container = document.createElement("div");
    container.classList.add("picture_with_results")

    const image = document.createElement("img");
    image.src = await getAsJpg(content);
    container.appendChild(image);

    const responseBox = document.createElement("pre");
    let responseContent = await response.json();
    responseBox.innerText = JSON.stringify(responseContent, null, 2);
    container.appendChild(responseBox);

    document.body.appendChild(container);
}

async function getAsJpg(image) {
    const response = await fetch("/get-as-jpg", {
        method: "POST",
        body: image
    })
    const imageBytes = await response.bytes();
    return await bytesToDataURL(imageBytes, "image/jpeg")
}

function bytesToDataURL(bytes, mimeType) {
    let uint8 = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);

    let binary = '';
    for (let i = 0; i < uint8.length; i++) {
        binary += String.fromCharCode(uint8[i]);
    }

    let base64 = btoa(binary);

    return `data:${mimeType};base64,${base64}`;
}

async function initDarkMode(location) {
    var button = document.createElement("details");
    button.appendChild(document.createElement("summary"));
    button.id = "darkmode-button";
    button.classList.add("noarrow");

    button.addEventListener("click", () => {
        const dark = document.documentElement.classList.toggle("dark");
        document.cookie = dark
            ? "darkmode=true; max-age=31536000; path=/;"
            : "darkmode=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/;";
        console.log(document.cookie);
    });

    document.body.appendChild(button);

    if (document.cookie.includes(`darkmode=true`)) {
        button.click();
        button.open = true;
    }

}
