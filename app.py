from pathlib import Path
from uuid import uuid4

from flask import Flask, request, jsonify, send_from_directory

from src.forensics.ela import analyze_ela
from src.forensics.quiet_zone import analyze_quiet_zone
from src.forensics.noise_variance import analyze_noise_variance
from src.forensics.combined_heatmap import create_combined_heatmap


# ==================================================
# FOLDERS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

WEB_DIR = BASE_DIR / "web"
UPLOAD_DIR = WEB_DIR / "uploads"
HEATMAP_DIR = BASE_DIR / "results" / "heatmaps"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
HEATMAP_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# FLASK APP
# ==================================================

app = Flask(
    __name__,
    static_folder="web",
    static_url_path=""
)

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


# ==================================================
# HOME PAGE
# ==================================================

@app.route("/")
def home():
    return app.send_static_file("index.html")


# ==================================================
# ANALYZE IMAGE
# ==================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    # --------------------------------------------------
    # CHECK UPLOAD
    # --------------------------------------------------

    if "image" not in request.files:
        return jsonify({
            "success": False,
            "error": "No image was uploaded."
        }), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "error": "No image was selected."
        }), 400


    # --------------------------------------------------
    # CHECK FILE TYPE
    # --------------------------------------------------

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({
            "success": False,
            "error": (
                "Please upload a JPG, JPEG, PNG or WEBP image."
            )
        }), 400


    # --------------------------------------------------
    # SAVE IMAGE WITH UNIQUE NAME
    # --------------------------------------------------

    unique_name = f"{uuid4().hex}{extension}"

    image_path = UPLOAD_DIR / unique_name

    file.save(image_path)


    try:

        # ==================================================
        # 1. ELA ANALYSIS
        # ==================================================

        ela_result = analyze_ela(image_path)

        ela_score = float(ela_result[0])
        ela_mean = float(ela_result[1])


        # ==================================================
        # 2. QUIET ZONE ANALYSIS
        # ==================================================

        quiet_result = analyze_quiet_zone(image_path)

        quiet_details = quiet_result[0]

        quiet_score = float(quiet_result[1])

        quiet_side = quiet_details.get(
            "suspicious_side",
            "none"
        )

        quiet_values = quiet_details


        # ==================================================
        # 3. NOISE VARIANCE ANALYSIS
        # ==================================================

        noise_result = analyze_noise_variance(image_path)

        noise_variance = float(noise_result[0])
        noise_score = float(noise_result[1])


        # ==================================================
        # TEMPORARY DEBUG INFORMATION
        # ==================================================

        print()
        print("=" * 60)
        print("NOISE VARIANCE DEBUG")
        print("=" * 60)
        print("Noise score:", noise_score)
        print("Mean variance:", noise_variance)
        print("=" * 60)
        print()


        # ==================================================
        # TOTAL XQR SCORE
        # ==================================================

        raw_score = (
            ela_score
            + quiet_score
            + noise_score
        )

        # Maximum prototype score = 99
        xqr_score = min(raw_score, 99)


        # ==================================================
        # FINAL RESULT
        # ==================================================

        if xqr_score > 0:

            result = (
                "FORENSIC ANOMALIES DETECTED"
            )

        else:

            result = (
                "NO FORENSIC ANOMALIES DETECTED"
            )


        # ==================================================
        # BUILD EVIDENCE
        # ==================================================

        evidence = []


        if ela_score > 0:

            evidence.append(
                "ELA detected abnormal compression differences."
            )


        if quiet_score > 0:

            evidence.append(
                f"Quiet-zone violation detected on the "
                f"{quiet_side} side."
            )


        if noise_score > 0:

            evidence.append(
                "Abnormal noise variance detected around "
                "the QR region."
            )


        if not evidence:

            evidence.append(
                "No significant forensic anomalies were detected."
            )


        # ==================================================
        # CREATE COMBINED HEATMAP
        # ==================================================

        create_combined_heatmap(image_path)

        heatmap_name = (
            f"{image_path.stem}_combined_heatmap.png"
        )


        # ==================================================
        # CONVERT QUIET-ZONE VALUES
        # ==================================================

        clean_quiet_values = {}

        for key, value in quiet_values.items():

            # Do not send the bounding box to the browser
            if key == "bbox":
                continue

            if hasattr(value, "item"):
                clean_quiet_values[key] = value.item()

            else:
                clean_quiet_values[key] = value


        # ==================================================
        # SEND RESULT TO WEBSITE
        # ==================================================

        return jsonify({

            "success": True,

            "result": result,

            "score": round(xqr_score, 2),


            # ------------------------------------------
            # MODULE SCORES
            # ------------------------------------------

            "scores": {

                "ela": round(
                    ela_score,
                    2
                ),

                "quiet_zone": round(
                    quiet_score,
                    2
                ),

                "noise_variance": round(
                    noise_score,
                    2
                )
            },


            # ------------------------------------------
            # MAXIMUM SCORES
            # ------------------------------------------

            "maximum_scores": {

                "ela": 25,

                "quiet_zone": 35,

                "noise_variance": 40
            },


            # ------------------------------------------
            # TECHNICAL DETAILS
            # ------------------------------------------

            "details": {

                "ela_mean": round(
                    ela_mean,
                    2
                ),

                "quiet_side": quiet_side,

                "noise_variance": round(
                    noise_variance,
                    2
                ),

                "quiet_values": clean_quiet_values
            },


            # ------------------------------------------
            # EVIDENCE
            # ------------------------------------------

            "evidence": evidence,


            # ------------------------------------------
            # HEATMAP
            # ------------------------------------------

            "heatmap": (
                f"/heatmaps/{heatmap_name}"
            )
        })


    # ==================================================
    # ERROR HANDLING
    # ==================================================

    except Exception as error:

        print()
        print("=" * 60)
        print("ANALYSIS ERROR")
        print("=" * 60)
        print(error)
        print("=" * 60)
        print()

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# ==================================================
# SERVE HEATMAP
# ==================================================

@app.route("/heatmaps/<filename>")
def serve_heatmap(filename):

    return send_from_directory(
        HEATMAP_DIR,
        filename
    )


# ==================================================
# START SERVER
# ==================================================

if __name__ == "__main__":

    print()

    print("=" * 60)

    print(
        "             XQR FOR MERCHANTS"
    )

    print(
        "        Web Forensic Analysis Server"
    )

    print("=" * 60)

    print()

    print(
        "Open this in your browser:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )