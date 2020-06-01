import re


def main():
    text = "value="

    res = re.search(r'\d+', text)

    print(res)


if __name__ == '__main__':
    main()
