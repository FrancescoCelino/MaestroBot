import sys

def print_first_200_lines(filename):
    try:
        with open(filename, 'r') as file:
            for i, line in enumerate(file):
                if i >= 10000000:
                    break
                print(line, end='')  # `end=''` to avoid adding extra newlines
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python stampa_prime_righe.py <filename>")
    else:
        print_first_200_lines(sys.argv[1])
