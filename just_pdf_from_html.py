import os
import pdfkit


def main():
    input_folder = 'html_output'
    output_folder = 'output'

    for filename in ('latest_en.html', 'latest_bg.html'):

        with open(os.path.join(input_folder, filename)) as f:
            html = f.read()
            pdfkit.from_string(html, os.path.join(output_folder, filename + '.pdf'))
            print(f'HTML template {filename} has been successfully converted to pdf')


if __name__ == '__main__':
    main()




