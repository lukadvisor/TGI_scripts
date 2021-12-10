import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

def main():

    __import__(sys.argv[1])

if __name__ == "__main__":
    main()
