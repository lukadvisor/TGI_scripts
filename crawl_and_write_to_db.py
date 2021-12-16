import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

def main():

    source = None
    try:
        source = sys.argv[1]
    except:
        print("ERROR! You must provide a valid source in input.")
        return(0)

    try:
        os.system(f'python run_crawler.py {source}')
    except Exception as e:
        print("Something went wrong during crawling. Details:")
        print(e)
    
    try:
        os.system(f'python write_to_db_v1.py {source}')
    except Exception as e:
        print("Something went wrong while writing to database. Details:")
        print(e)

if __name__ == "__main__":
    main()
