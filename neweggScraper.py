from bs4 import BeautifulSoup as soup
import csv
import requests


class UserBenchScraper:
    def __init__(self,part):
        self.url = "https://cpu.userbenchmark.com"

        # opening connection, grabbing the page
        self.client = requests.get(self.url)
        self.part = part
        # does html parsing
        self.pageSoup = soup(self.client.text,features="html.parser")
        print(self.pageSoup)

    def start_scrape(self):
        # grabs each product
        cells = self.pageSoup.find_all("div", attrs={"class": "hovertarget"})

        with open(self.part + '.csv', mode='w', newline='') as partFile:
            file_writer = csv.writer(partFile)
            file_writer.writerow(['Brand', 'Product Name', 'Price', 'Shipping'])
            for cell in cells:
                # checking to see if cell is an advertisement, if
                # condition is true, then cell is not an advertisement
                # and we can execute the code below without an error
                try:
                    # obtaining the brand name
                    partTitle = cell.find_all("div", attrs={"class": "semi-strongs lighterblacktexts"})
                    partName = partTitle[0].img["innerText"]
                    print(partName)

                    # obtaining the product name
                    #title_tag = cell.find_all("a", attrs={"class": "item-title"})
                    #product_name = title_tag[0].text

                    # checking for promo situations (out of stock, limited time offer)
                    #if cell.find_all("p", attrs={"class": "item-promo"}) != []:
                        # obtaining the price info
                        #promo_tag = cell.find_all("p", attrs={"class": "item-promo"})
                        #promo_info = promo_tag[0].text

                        #if promo_info == "OUT OF STOCK":
                            #pricing_info = promo_info
                            #shipping_tag = cell.find_all("a", attrs={"class": "shipped-by-newegg"})
                            #shipping_info = shipping_tag[0].text
                        #else:  # handles limited time offer
                            #price_tag = cell.find_all("li", attrs={"class": "price-current"})
                            #dollar_sign = price_tag[0].text[0]
                            #dollars = price_tag[0].strong.text
                            #cents = price_tag[0].sup.text

                            #pricing_info = dollar_sign + dollars + cents + ', ' + promo_info

                            #shipping_tag = cell.find_all("li", attrs={"class": "price-ship"})
                            #shipping_info = shipping_tag[0].text
                    #else:
                        # obtaining the price info
                        #price_tag = cell.find_all("li", attrs={"class": "price-current"})
                        #dollar_sign = price_tag[0].text[0]
                        #dollars = price_tag[0].strong.text
                        #cents = price_tag[0].sup.text
                        #pricing_info = dollar_sign + dollars + cents

                        # obtaining the shipping info
                        #shipping_tag = cell.find_all("li", attrs={"class": "price-ship"})
                        #shipping_info = shipping_tag[0].text

                    #file_writer.writerow([brand_name, product_name, pricing_info, shipping_info])
                except Exception as error:
                    print(f'Error that occurred: {error.__class__.__name__}')
                    print(f'Error message: {error}')
                    print(f'Cell where error occurred: {cell}')
                    print()
if __name__ == '__main__':
    scraper = UserBenchScraper("cpu")
    scraper.start_scrape()