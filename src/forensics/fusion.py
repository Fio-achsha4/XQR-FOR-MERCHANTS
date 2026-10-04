from pathlib import Path

from .quiet_zone import analyze_quiet_zone
from .noise_variance import analyze_noise_variance
from .ela import analyze_ela
from .combined_heatmap import create_combined_heatmap
from src.classification.mobile_classifier import classify_image


def analyze_image(image_path):
    image_path = Path(image_path)

    print("\n" + "=" * 60)
    print("                 XQR FORENSIC ANALYSIS")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. RUN CLASSICAL FORENSIC MODULES
    # ---------------------------------------------------------

    ela_result = analyze_ela(image_path)
    quiet_result = analyze_quiet_zone(image_path)
    noise_result = analyze_noise_variance(image_path)

    # ---------------------------------------------------------
    # 2. EXPERIMENTAL MOBILENETV3 CLASSIFICATION
    # ---------------------------------------------------------

    classification_result = classify_image(image_path)

    ml_class = classification_result["class"]
    ml_confidence = classification_result["confidence"]
    genuine_probability = classification_result["genuine_probability"]
    tampered_probability = classification_result["tampered_probability"]

    # ---------------------------------------------------------
    # 3. CREATE COMBINED FORENSIC HEATMAP
    # ---------------------------------------------------------

    create_combined_heatmap(image_path)

    # ---------------------------------------------------------
    # 4. EXTRACT FORENSIC SCORES
    # ---------------------------------------------------------

    ela_score = ela_result[1]
    quiet_score = quiet_result[1]
    noise_score = noise_result[1]

    # ---------------------------------------------------------
    # 5. FUSE CLASSICAL FORENSIC SCORES
    # ---------------------------------------------------------

    raw_score = ela_score + quiet_score + noise_score

    # Prototype research scale described in the project report.
    xqr_score = min(99, raw_score)

    # ---------------------------------------------------------
    # 6. COLLECT EVIDENCE
    # ---------------------------------------------------------

    evidence = []

    if ela_score > 0:
        evidence.append(
            "ELA detected a compression/editing difference."
        )

    if quiet_score > 0:
        evidence.append(
            "Quiet-zone analysis detected possible intrusion."
        )

    if noise_score > 0:
        evidence.append(
            "Noise variance detected abnormal texture/noise."
        )

    # ---------------------------------------------------------
    # 7. FINAL FORENSIC RESULT
    # ---------------------------------------------------------

    if xqr_score > 0:
        result = "FORENSIC ANOMALIES DETECTED"
    else:
        result = "NO FORENSIC ANOMALIES DETECTED"

    # ---------------------------------------------------------
    # 8. DISPLAY RESULTS
    # ---------------------------------------------------------

    print("\n" + "-" * 60)
    print("XQR FORENSIC SCORE")
    print("-" * 60)

    print(f"ELA contribution:            {ela_score:.2f} / 25")
    print(f"Quiet-Zone contribution:     {quiet_score:.2f} / 35")
    print(f"Noise Variance contribution: {noise_score:.2f} / 40")

    print()
    print(f"Raw forensic score:          {raw_score:.2f} / 100")
    print(f"XQR prototype score:         {xqr_score:.2f} / 99")

    print("\nFORENSIC RESULT:")
    print(result)

    # ---------------------------------------------------------
    # 9. EXPERIMENTAL ML RESULT
    # ---------------------------------------------------------

    print("\n" + "-" * 60)
    print("EXPERIMENTAL MOBILENETV3 CLASSIFICATION")
    print("-" * 60)

    print("NOTE: MobileNetV3 is currently experimental.")
    print("It is NOT used to determine the final forensic result.")

    print(f"\nPrediction: {ml_class}")
    print(f"Confidence: {ml_confidence:.2f}%")
    print(f"Genuine probability:  {genuine_probability:.2f}%")
    print(f"Tampered probability: {tampered_probability:.2f}%")

    # ---------------------------------------------------------
    # 10. EVIDENCE
    # ---------------------------------------------------------

    print("\n" + "-" * 60)
    print("FORENSIC EVIDENCE")
    print("-" * 60)

    if evidence:
        for item in evidence:
            print(f"- {item}")
    else:
        print("- No forensic anomalies detected.")

    # ---------------------------------------------------------
    # 11. VISUAL EVIDENCE
    # ---------------------------------------------------------

    print("\n" + "-" * 60)
    print("VISUAL EVIDENCE")
    print("-" * 60)

    ela_heatmap = (
        Path("results/heatmaps")
        / f"{image_path.stem}_ela_heatmap.png"
    )

    noise_heatmap = (
        Path("results/heatmaps")
        / f"{image_path.stem}_noise_heatmap.png"
    )

    combined_heatmap = (
        Path("results/heatmaps")
        / f"{image_path.stem}_combined_heatmap.png"
    )

    print(f"ELA heatmap:")
    print(f"  {ela_heatmap}")

    print(f"\nNoise variance heatmap:")
    print(f"  {noise_heatmap}")

    print(f"\nCombined forensic heatmap:")
    print(f"  {combined_heatmap}")

    print("\n" + "=" * 60)

    # ---------------------------------------------------------
    # 12. SAVE FORENSIC REPORT
    # ---------------------------------------------------------

    report_folder = Path("results/reports")
    report_folder.mkdir(parents=True, exist_ok=True)

    report_path = (
        report_folder
        / f"{image_path.stem}_report.txt"
    )

    with open(report_path, "w", encoding="utf-8") as file:

        file.write("=" * 60 + "\n")
        file.write("             XQR FORENSIC ANALYSIS REPORT\n")
        file.write("=" * 60 + "\n\n")

        file.write("IMAGE INFORMATION\n")
        file.write("-" * 60 + "\n")
        file.write(f"Image: {image_path}\n\n")

        # -----------------------------------------------------
        # FORENSIC SCORE
        # -----------------------------------------------------

        file.write("FORENSIC SCORE BREAKDOWN\n")
        file.write("-" * 60 + "\n")

        file.write(
            f"ELA contribution:            "
            f"{ela_score:.2f} / 25\n"
        )

        file.write(
            f"Quiet-Zone contribution:     "
            f"{quiet_score:.2f} / 35\n"
        )

        file.write(
            f"Noise Variance contribution: "
            f"{noise_score:.2f} / 40\n"
        )

        file.write("\n")

        file.write(
            f"Raw forensic score:          "
            f"{raw_score:.2f} / 100\n"
        )

        file.write(
            f"XQR prototype score:         "
            f"{xqr_score:.2f} / 99\n\n"
        )

        # -----------------------------------------------------
        # RESULT
        # -----------------------------------------------------

        file.write("FORENSIC RESULT\n")
        file.write("-" * 60 + "\n")
        file.write(f"{result}\n\n")

        # -----------------------------------------------------
        # INTERPRETATION
        # -----------------------------------------------------

        file.write("INTERPRETATION\n")
        file.write("-" * 60 + "\n")

        if xqr_score == 0:
            file.write(
                "No abnormal forensic signals were detected "
                "by the implemented classical modules.\n"
            )
        else:
            file.write(
                "One or more forensic modules detected "
                "anomalous visual characteristics around "
                "the QR region.\n"
            )

        file.write(
            "\nThe XQR score is a prototype forensic score, "
            "not a probability, accuracy value, or proof of fraud.\n"
        )

        # -----------------------------------------------------
        # EVIDENCE
        # -----------------------------------------------------

        file.write("\nFORENSIC EVIDENCE\n")
        file.write("-" * 60 + "\n")

        if evidence:
            for item in evidence:
                file.write(f"- {item}\n")
        else:
            file.write("- No forensic anomalies detected.\n")

        # -----------------------------------------------------
        # EXPERIMENTAL ML
        # -----------------------------------------------------

        file.write("\nEXPERIMENTAL MOBILENETV3 CLASSIFICATION\n")
        file.write("-" * 60 + "\n")

        file.write(
            "Status: Experimental / research-stage component\n"
        )

        file.write(
            "The MobileNetV3 prediction is NOT used to determine "
            "the final forensic result.\n\n"
        )

        file.write(f"Prediction: {ml_class}\n")
        file.write(f"Confidence: {ml_confidence:.2f}%\n")
        file.write(
            f"Genuine probability:  {genuine_probability:.2f}%\n"
        )
        file.write(
            f"Tampered probability: {tampered_probability:.2f}%\n"
        )

        # -----------------------------------------------------
        # VISUAL EVIDENCE
        # -----------------------------------------------------

        file.write("\nVISUAL EVIDENCE\n")
        file.write("-" * 60 + "\n")

        file.write(
            f"ELA heatmap:\n"
            f"{ela_heatmap}\n\n"
        )

        file.write(
            f"Noise variance heatmap:\n"
            f"{noise_heatmap}\n\n"
        )

        file.write(
            f"Combined forensic heatmap:\n"
            f"{combined_heatmap}\n\n"
        )

        # -----------------------------------------------------
        # DISCLAIMER
        # -----------------------------------------------------

        file.write("PROJECT NOTE\n")
        file.write("-" * 60 + "\n")

        file.write(
            "This prototype is intended for research and "
            "forensic-assistance purposes. The current score "
            "thresholds require validation and calibration using "
            "a larger real-world dataset.\n"
        )

        file.write(
            "A forensic anomaly does not by itself establish "
            "fraudulent ownership or fraudulent payment activity.\n"
        )

        file.write("\n" + "=" * 60 + "\n")

    print(f"\nReport saved at: {report_path}")


if __name__ == "__main__":
    analyze_image("data/tampered/tampered_01.png")
    analyze_image("data/genuine/genuine_01.png")