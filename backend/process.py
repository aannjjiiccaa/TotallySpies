from process_repos import main
from connect_repos import second_pass


def process():
    main()
    second_pass()


if __name__ == '__main__':
    process()
