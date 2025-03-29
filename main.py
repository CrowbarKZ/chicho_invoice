import calendar
import os
from datetime import datetime, timedelta

import pdfkit
from jinja2 import Environment, FileSystemLoader

import private
import translations

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")


def main():
    # calculate data
    year = int(input("Year [2025]: ") or 2025)
    month = int(input("Month [1]: ") or 1)

    try:
        with open(".last_invoice") as f:
            last_invoice_number = int(f.read() or 0)
    except OSError:
        last_invoice_number = 0

    invoice_number = int(
        input(f"Invoice number [{last_invoice_number + 1}]: ")
        or last_invoice_number + 1
    )
    invoice_number_str = str(invoice_number).zfill(10)

    payment_terms = 14  # days
    last_day = calendar.monthrange(year, month)[1]
    date_of_service = datetime(year=year, month=month, day=last_day)
    date_of_issue = date_of_service + timedelta(days=1)
    due_date = date_of_issue + timedelta(days=payment_terms)

    rate = 1.95583  # EUR to BGN exchange rate
    print(f"Exchange rate: {rate} BGN per 1 EUR (current rate from the Bulgarian National Bank)")

    additional_items = []
    additional_items_needed = input("Do you want to add additional items? [no]: ") or "no"
    additional_items_needed = not(additional_items_needed == "no")
    if additional_items_needed:
        while True:
            item = input("Item description: ")
            if not item:
                break
            item_bg = input("Item description in Bulgarian: ")
            price = float(input("Item price in EUR: "))
            additional_items.append({
                "description": item,
                "description_bg": item_bg,
                "price": price
            })

    print(f"Preparing invoices for {month}.{year} ...")
    for language in ("en", "bg"):
        # load translated labels
        data = getattr(translations, language)

        # load private data
        data.update(getattr(private, language))

        # adjust prices if we are generating a Bulgarian invoice
        price = data["price_pvt"]
        if language != "en":
            price = price * rate
            for item in additional_items:
                item["price"] = round(item["price"] * rate, 2)

        # calculate total
        total = price
        for item in additional_items:
            total += item["price"]

        data.update(
            {
                "language": language,
                "payment_terms_val": payment_terms,
                "date_of_service_val": date_of_service.strftime("%d.%m.%Y"),
                "date_of_issue_val": date_of_issue.strftime("%d.%m.%Y"),
                "due_date_val": due_date.strftime("%d.%m.%Y"),
                "price_val": price,
                "total_val": total,
                "rate_val": rate,
                "invoice_number_val": invoice_number_str,
                "additional_items": additional_items,
            }
        )

        # prepare html
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True)
        html = env.get_template("simple.html").render(**data)
        with open(f"html_output/latest_{language}.html", "w") as f:
            f.write(html)

        # generate pdf
        folder = "output"
        filename = f"invoice_{invoice_number_str}_{language}_{month}_{year}.pdf"
        pdfkit.from_string(html, os.path.join(folder, filename))

        with open(".last_invoice", "w") as f:
            f.write(str(invoice_number))

        print(f"Invoice number {invoice_number_str} has been successfully generated")


if __name__ == "__main__":
    main()
