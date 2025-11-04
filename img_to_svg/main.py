import argparse
from pixels2svg.main import pixels2svg

def main():
    parser = argparse.ArgumentParser(description='Convert an image to SVG.')
    parser.add_argument('input_file', help='The input image file (PNG or JPEG).')
    parser.add_argument('output_file', help='The output SVG file.')
    args = parser.parse_args()

    try:
        pixels2svg(input_path=args.input_file, output_path=args.output_file)
        print(f"Successfully converted {args.input_file} to {args.output_file}")
    except FileNotFoundError:
        print(f"Error: Input file not found at {args.input_file}")
    except Exception as e:
        print(f"An error occurred during conversion: {e}")

if __name__ == '__main__':
    main()
