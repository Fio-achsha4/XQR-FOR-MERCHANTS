from pathlib import Path
from datetime import datetime

from src.forensics.ela import analyze_ela
from src.forensics.quiet_zone import analyze_quiet_zone
from src.forensics.noise_variance import analyze_noise_variance


GENUINE_IMAGE = Path("data/genuine/genuine_01.png")
TAMPERED_IMAGE = Path("data/tampered/tampered_01.png")

RESULTS_FOLDER = Path("results/evaluation")


def evaluate_image(image_path):
    """Run the three classical forensic modules on one image."""

    ela_result = analyze_ela(image_path)
    quiet_result = analyze_quiet_zone(image_path)
    noise_result = analyze_noise_variance(image_path)

    ela_score = ela_result[1]
    quiet_score = quiet_result[1]
    noise_score = noise_result[1]

    raw_score = ela_score + quiet_score + noise_score
    xqr_score = min(99, raw_score)

    if xqr_score > 0:
        result = "FORENSIC ANOMALIES DETECTED"
    else:
        result = "NO FORENSIC ANOMALIES DETECTED"

    return {
        "ela": ela_score,
        "quiet": quiet_score,
        "noise": noise_score,
        "raw": raw_score,
        "xqr": xqr_score,
        "result": result,
    }


def print_result(name, result):
    """Display one image's evaluation."""

    print("\n" + "-" * 60)
    print(name)
    print("-" * 60)

    print(f"ELA:             {result['ela']:.2f} / 25")
    print(f"Quiet-Zone:      {result['quiet']:.2f} / 35")
    print(f"Noise Variance:  {result['noise']:.2f} / 40")

    print()
    print(f"Raw Score:       {result['raw']:.2f} / 100")
    print(f"XQR Score:       {result['xqr']:.2f} / 99")

    print()
    print(f"Result: {result['result']}")


def main():

    print("\n" + "=" * 60)
    print("             XQR CONTROLLED EVALUATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # CHECK INPUT FILES
    # ---------------------------------------------------------

    if not GENUINE_IMAGE.exists():
        print("\nERROR: Genuine image not found:")
        print(GENUINE_IMAGE)
        return

    if not TAMPERED_IMAGE.exists():
        print("\nERROR: Tampered image not found:")
        print(TAMPERED_IMAGE)
        return

    # ---------------------------------------------------------
    # RUN TESTS
    # ---------------------------------------------------------

    print("\nRunning genuine sample...")
    genuine_result = evaluate_image(GENUINE_IMAGE)

    print("Running tampered sample...")
    tampered_result = evaluate_image(TAMPERED_IMAGE)

    # ---------------------------------------------------------
    # DISPLAY RESULTS
    # ---------------------------------------------------------

    print_result("GENUINE SAMPLE", genuine_result)
    print_result("TAMPERED SAMPLE", tampered_result)

    # ---------------------------------------------------------
    # COMPARISON
    # ---------------------------------------------------------

    score_difference = (
        tampered_result["xqr"]
        - genuine_result["xqr"]
    )

    print("\n" + "=" * 60)
    print("                    COMPARISON")
    print("=" * 60)

    print(
        f"\nGenuine XQR score:  "
        f"{genuine_result['xqr']:.2f} / 99"
    )

    print(
        f"Tampered XQR score: "
        f"{tampered_result['xqr']:.2f} / 99"
    )

    print(
        f"\nScore difference:    "
        f"{score_difference:.2f} points"
    )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("                    SUMMARY")
    print("=" * 60)

    print("\nGenuine:")
    print(f"  → {genuine_result['result']}")

    print("\nTampered:")
    print(f"  → {tampered_result['result']}")

    if (
        genuine_result["xqr"] == 0
        and tampered_result["xqr"] > 0
    ):
        outcome = (
            "PASS - The forensic pipeline separated "
            "the genuine and tampered samples."
        )
    else:
        outcome = (
            "REVIEW - The samples were not separated "
            "by the current forensic scoring system."
        )

    print("\nControlled test outcome:")
    print(f"  {outcome}")

    # ---------------------------------------------------------
    # SAVE RESULTS
    # ---------------------------------------------------------

    RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)

    report_path = (
        RESULTS_FOLDER / "controlled_evaluation.txt"
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(report_path, "w", encoding="utf-8") as file:

        file.write("=" * 60 + "\n")
        file.write("             XQR CONTROLLED EVALUATION\n")
        file.write("=" * 60 + "\n\n")

        file.write(f"Evaluation date: {timestamp}\n\n")

        # Genuine
        file.write("GENUINE SAMPLE\n")
        file.write("-" * 60 + "\n")

        file.write(
            f"Image: {GENUINE_IMAGE}\n"
        )

        file.write(
            f"ELA:             "
            f"{genuine_result['ela']:.2f} / 25\n"
        )

        file.write(
            f"Quiet-Zone:      "
            f"{genuine_result['quiet']:.2f} / 35\n"
        )

        file.write(
            f"Noise Variance:  "
            f"{genuine_result['noise']:.2f} / 40\n"
        )

        file.write(
            f"Raw Score:       "
            f"{genuine_result['raw']:.2f} / 100\n"
        )

        file.write(
            f"XQR Score:       "
            f"{genuine_result['xqr']:.2f} / 99\n"
        )

        file.write(
            f"Result:          "
            f"{genuine_result['result']}\n\n"
        )

        # Tampered
        file.write("TAMPERED SAMPLE\n")
        file.write("-" * 60 + "\n")

        file.write(
            f"Image: {TAMPERED_IMAGE}\n"
        )

        file.write(
            f"ELA:             "
            f"{tampered_result['ela']:.2f} / 25\n"
        )

        file.write(
            f"Quiet-Zone:      "
            f"{tampered_result['quiet']:.2f} / 35\n"
        )

        file.write(
            f"Noise Variance:  "
            f"{tampered_result['noise']:.2f} / 40\n"
        )

        file.write(
            f"Raw Score:       "
            f"{tampered_result['raw']:.2f} / 100\n"
        )

        file.write(
            f"XQR Score:       "
            f"{tampered_result['xqr']:.2f} / 99\n"
        )

        file.write(
            f"Result:          "
            f"{tampered_result['result']}\n\n"
        )

        # Comparison
        file.write("COMPARISON\n")
        file.write("-" * 60 + "\n")

        file.write(
            f"Genuine XQR score:  "
            f"{genuine_result['xqr']:.2f} / 99\n"
        )

        file.write(
            f"Tampered XQR score: "
            f"{tampered_result['xqr']:.2f} / 99\n"
        )

        file.write(
            f"Score difference:    "
            f"{score_difference:.2f} points\n\n"
        )

        # Outcome
        file.write("CONTROLLED TEST OUTCOME\n")
        file.write("-" * 60 + "\n")
        file.write(f"{outcome}\n\n")

        file.write(
            "NOTE: The XQR score is a prototype forensic "
            "score and is not a probability or accuracy "
            "measurement. Larger real-world evaluation is "
            "required for calibration and performance "
            "metrics.\n"
        )

        file.write("\n" + "=" * 60 + "\n")

    print(
        f"\nEvaluation report saved at:\n"
        f"{report_path}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()