from src.TabSystem import TabPageManager, DefaultLayoutTPM
from src.Page import TestPage, DrawPage

def main():
    tm = TabPageManager(DefaultLayoutTPM)
    tm.main_window.geometry("900x600+50+50")
    tm.main_window.title("NoName")
    tm.register_page(TestPage)
    tm.register_page(DrawPage)
    tm.run()


if __name__ == "__main__":
    main()
