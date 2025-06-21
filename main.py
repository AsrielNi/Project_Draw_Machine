from src.TabSystem import TabPageManager
from src.Page import TestPage, DrawPage


def main():
    bm = TabPageManager()
    bm.register_page(TestPage)
    bm.register_page(DrawPage)
    bm.run()

if __name__ == "__main__":
    main()
