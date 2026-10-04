from pathlib import Path

from src.forensics.fusion import analyze_image


def main():
    print("\n" + "=" * 50)
    print("        XQR FOR MERCHANTS")
    print("   QR FORENSIC TAMPER DETECTION")
    print("=" * 50)

    image_path = input("\nEnter the path of the QR image: ").strip()

    # Remove quotes if a path was pasted with quotes
    image_path = image_path.strip('"').strip("'")

    path = Path(image_path)

    if not path.exists():
        print("\nERROR: Image file not found.")
        print("Please check the path and try again.")
        return

    print("\nAnalyzing image...")
    analyze_image(path)


if __name__ == "__main__":
    main()