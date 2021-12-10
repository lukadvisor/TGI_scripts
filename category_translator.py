import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

sys.path.append('/home/lbrianza/.local/bin/deep-translator')

from deep_translator import GoogleTranslator 

LANGUAGES = ['it','fr','es','de','pl']

def main():
    with open('categories.txt','r') as f:
        categories = f.read().splitlines()
    print(categories)

    for language in LANGUAGES:
        file_name = f'categories_{language}.txt'
        print('----------------')
        print(f'Translating {language}')
        with open(file_name,'w') as f:
            for category in categories:
                category_translated = GoogleTranslator(source='auto', target=language).translate(category) 
                f.write(category_translated+'\n')
                print(category_translated)

if __name__ == "__main__":
    main()