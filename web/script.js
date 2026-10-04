// ==========================================================
// XQR FOR MERCHANTS — WEB INTERFACE
// ==========================================================

const imageInput = document.getElementById("imageInput");
const chooseButton = document.getElementById("chooseButton");
const analyzeButton = document.getElementById("analyzeButton");
const resetButton = document.getElementById("resetButton");

const dropZone = document.getElementById("dropZone");
const fileName = document.getElementById("fileName");

const previewContainer = document.getElementById("previewContainer");
const previewImage = document.getElementById("previewImage");

const loadingSection = document.getElementById("loadingSection");
const resultsSection = document.getElementById("resultsSection");

const loadingTitle = document.getElementById("loadingTitle");
const loadingStatus = document.getElementById("loadingStatus");

const mainProgressBar = document.getElementById("mainProgressBar");

const elaLoading = document.getElementById("elaLoading");
const quietLoading = document.getElementById("quietLoading");
const noiseLoading = document.getElementById("noiseLoading");

const resultBadge = document.getElementById("resultBadge");

const scoreValue = document.getElementById("scoreValue");
const scoreBar = document.getElementById("scoreBar");

const elaScore = document.getElementById("elaScore");
const quietScore = document.getElementById("quietScore");
const noiseScore = document.getElementById("noiseScore");

const elaBar = document.getElementById("elaBar");
const quietBar = document.getElementById("quietBar");
const noiseBar = document.getElementById("noiseBar");

const quietDescription = document.getElementById("quietDescription");

const evidenceList = document.getElementById("evidenceList");

const heatmapImage = document.getElementById("heatmapImage");

let selectedFile = null;


// ==========================================================
// CHOOSE IMAGE BUTTON
// ==========================================================

chooseButton.addEventListener("click", () => {
    imageInput.click();
});


// ==========================================================
// WHEN FILE IS SELECTED
// ==========================================================

imageInput.addEventListener("change", () => {

    if (imageInput.files.length > 0) {

        handleFile(imageInput.files[0]);

    }

});


// ==========================================================
// DRAG & DROP
// ==========================================================

dropZone.addEventListener("dragover", (event) => {

    event.preventDefault();

    dropZone.classList.add("dragging");

});


dropZone.addEventListener("dragleave", () => {

    dropZone.classList.remove("dragging");

});


dropZone.addEventListener("drop", (event) => {

    event.preventDefault();

    dropZone.classList.remove("dragging");

    const files = event.dataTransfer.files;

    if (files.length > 0) {

        handleFile(files[0]);

    }

});


// ==========================================================
// HANDLE FILE
// ==========================================================

function handleFile(file) {

    const allowedTypes = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ];

    if (!allowedTypes.includes(file.type)) {

        alert("Please select a JPG, PNG or WEBP image.");

        return;

    }


    selectedFile = file;

    fileName.textContent = file.name;


    // Create preview
    const imageURL = URL.createObjectURL(file);

    previewImage.src = imageURL;

    previewContainer.classList.remove("hidden");

}


// ==========================================================
// ANALYZE BUTTON
// ==========================================================

analyzeButton.addEventListener("click", async () => {

    if (!selectedFile) {

        alert("Please select an image first.");

        return;

    }


    await analyzeImage();

});


// ==========================================================
// ANALYZE IMAGE
// ==========================================================

async function analyzeImage() {

    // Hide upload section
    document.querySelector(".upload-card").classList.add("hidden");

    // Show loading
    loadingSection.classList.remove("hidden");

    // Reset loading bars
    mainProgressBar.style.width = "0%";

    elaLoading.style.width = "0%";
    quietLoading.style.width = "0%";
    noiseLoading.style.width = "0%";


    // ------------------------------------------------------
    // CREATE FORM DATA
    // ------------------------------------------------------

    const formData = new FormData();

    formData.append("image", selectedFile);


    // ------------------------------------------------------
    // LOADING ANIMATION
    // ------------------------------------------------------

    const loadingMessages = [
        "Preparing forensic analysis...",
        "Analyzing compression differences...",
        "Checking QR quiet-zone boundaries...",
        "Measuring abnormal noise...",
        "Combining forensic evidence..."
    ];

    let progress = 5;
    let messageIndex = 0;


    loadingTitle.textContent = "Analyzing QR sticker...";
    loadingStatus.textContent = loadingMessages[0];


    const progressTimer = setInterval(() => {

        progress += Math.random() * 8;

        if (progress > 90) {
            progress = 90;
        }

        mainProgressBar.style.width = `${progress}%`;


        if (
            progress > 20 &&
            messageIndex === 0
        ) {
            messageIndex = 1;
            loadingStatus.textContent = loadingMessages[1];
            elaLoading.style.width = "35%";
        }


        if (
            progress > 40 &&
            messageIndex === 1
        ) {
            messageIndex = 2;
            loadingStatus.textContent = loadingMessages[2];
            elaLoading.style.width = "100%";
            quietLoading.style.width = "45%";
        }


        if (
            progress > 60 &&
            messageIndex === 2
        ) {
            messageIndex = 3;
            loadingStatus.textContent = loadingMessages[3];
            quietLoading.style.width = "100%";
            noiseLoading.style.width = "55%";
        }


        if (
            progress > 78 &&
            messageIndex === 3
        ) {
            messageIndex = 4;
            loadingStatus.textContent = loadingMessages[4];
            noiseLoading.style.width = "100%";
        }

    }, 350);


    try {

        // --------------------------------------------------
        // SEND IMAGE TO FLASK
        // --------------------------------------------------

        const response = await fetch("/analyze", {

            method: "POST",

            body: formData

        });


        const data = await response.json();


        clearInterval(progressTimer);


        // --------------------------------------------------
        // ERROR
        // --------------------------------------------------

        if (!response.ok || !data.success) {

            throw new Error(
                data.error || "Analysis failed."
            );

        }


        // --------------------------------------------------
        // COMPLETE LOADING
        // --------------------------------------------------

        mainProgressBar.style.width = "100%";

        elaLoading.style.width = "100%";
        quietLoading.style.width = "100%";
        noiseLoading.style.width = "100%";

        loadingTitle.textContent = "Analysis complete ✓";

        loadingStatus.textContent =
            "Forensic evidence has been processed.";


        // Give the completion animation a moment
        await sleep(700);


        // --------------------------------------------------
        // HIDE LOADING
        // --------------------------------------------------

        loadingSection.classList.add("hidden");


        // --------------------------------------------------
        // SHOW RESULTS
        // --------------------------------------------------

        resultsSection.classList.remove("hidden");


        displayResults(data);


    } catch (error) {

        clearInterval(progressTimer);

        console.error(error);

        alert(
            "Something went wrong during analysis:\n\n" +
            error.message
        );


        loadingSection.classList.add("hidden");

        document
            .querySelector(".upload-card")
            .classList.remove("hidden");

    }

}


// ==========================================================
// DISPLAY RESULTS
// ==========================================================

function displayResults(data) {

    const scores = data.scores;


    // ------------------------------------------------------
    // RESULT
    // ------------------------------------------------------

    resultBadge.textContent = data.result;


    // ------------------------------------------------------
    // XQR SCORE
    // ------------------------------------------------------

    animateNumber(
        scoreValue,
        0,
        data.score,
        900
    );


    setTimeout(() => {

        scoreBar.style.width =
            `${(data.score / 99) * 100}%`;

    }, 100);


    // ------------------------------------------------------
    // ELA
    // ------------------------------------------------------

    elaScore.textContent =
        scores.ela.toFixed(1);

    setTimeout(() => {

        elaBar.style.width =
            `${(scores.ela / 25) * 100}%`;

    }, 150);


    // ------------------------------------------------------
    // QUIET ZONE
    // ------------------------------------------------------

    quietScore.textContent =
        scores.quiet_zone.toFixed(1);

    setTimeout(() => {

        quietBar.style.width =
            `${(scores.quiet_zone / 35) * 100}%`;

    }, 250);


    // ------------------------------------------------------
    // NOISE
    // ------------------------------------------------------

    noiseScore.textContent =
        scores.noise_variance.toFixed(1);

    setTimeout(() => {

        noiseBar.style.width =
            `${(scores.noise_variance / 40) * 100}%`;

    }, 350);


    // ------------------------------------------------------
    // QUIET ZONE DESCRIPTION
    // ------------------------------------------------------

    if (data.details.quiet_side) {

        quietDescription.textContent =
            `Most suspicious side: ${data.details.quiet_side}`;

    } else {

        quietDescription.textContent =
            "No significant boundary violation detected.";

    }


    // ------------------------------------------------------
    // EVIDENCE
    // ------------------------------------------------------

    evidenceList.innerHTML = "";


    data.evidence.forEach((evidence) => {

        const item = document.createElement("div");

        item.className = "evidence-item";

        item.innerHTML = `
            <span>⚠️</span>
            <span>${escapeHTML(evidence)}</span>
        `;

        evidenceList.appendChild(item);

    });


    // ------------------------------------------------------
    // HEATMAP
    // ------------------------------------------------------

    heatmapImage.src =
        data.heatmap + "?t=" + Date.now();

}


// ==========================================================
// RESET
// ==========================================================

resetButton.addEventListener("click", () => {

    selectedFile = null;

    imageInput.value = "";

    fileName.textContent =
        "No image selected";

    previewImage.src = "";

    previewContainer.classList.add("hidden");

    resultsSection.classList.add("hidden");

    loadingSection.classList.add("hidden");

    document
        .querySelector(".upload-card")
        .classList.remove("hidden");


    // Reset progress bars

    mainProgressBar.style.width = "0%";

    scoreBar.style.width = "0%";

    elaBar.style.width = "0%";
    quietBar.style.width = "0%";
    noiseBar.style.width = "0%";

});


// ==========================================================
// ANIMATED NUMBER
// ==========================================================

function animateNumber(element, start, end, duration) {

    const startTime = performance.now();


    function update(currentTime) {

        const elapsed =
            currentTime - startTime;

        const progress =
            Math.min(elapsed / duration, 1);


        // Smooth easing
        const eased =
            1 - Math.pow(1 - progress, 3);


        const value =
            start + (end - start) * eased;


        element.textContent =
            value.toFixed(1);


        if (progress < 1) {

            requestAnimationFrame(update);

        }

    }


    requestAnimationFrame(update);

}


// ==========================================================
// SMALL DELAY HELPER
// ==========================================================

function sleep(milliseconds) {

    return new Promise(resolve => {

        setTimeout(resolve, milliseconds);

    });

}


// ==========================================================
// BASIC HTML ESCAPING
// ==========================================================

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}