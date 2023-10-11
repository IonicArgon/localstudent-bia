import toml
import re
import pandas as pd
from pathlib import Path
from playwright.sync_api import sync_playwright

# read config file
config = toml.load("config.toml")
urls = config["config"]["urls"]
output_file = Path(config["config"]["output_file"])

print("Config file loaded with following settings:\n" "urls:")
for url in urls:
    print('\t"' + url + '"')
print("output_file:\n\t" + str(output_file))


# set up pandas dataframe
df = pd.DataFrame(columns=["BIA", "email", "phone"])

# now scrape the data, looping through urls
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    for url in urls:
        page.goto(url)

        # get all accordion sections
        sections = page.query_selector_all("div.accordion__section")
        
        # loop through sections
        for section in sections:
            # bia name
            bia_name = section.query_selector("h2").inner_text()
            print(f"Processing {bia_name}...")

            # bia email
            bia_email_elem = section.query_selector("a[href^='mailto:']")
            
            # doing all this to get the phone number
            bia_inner_html = section.inner_html()
            bia_phone = re.search(r"\d{3}.\d{3}.\d{4}", bia_inner_html)

            # if email and phone are found, add to dataframe, or none if not found
            if bia_email_elem:
                bia_email = bia_email_elem.inner_text()
            else:
                bia_email = "N/A"
            
            if bia_phone:
                bia_phone = bia_phone.group()
            else:
                bia_phone = "N/A"

            # add to dataframe
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        [[bia_name, bia_email, bia_phone]],
                        columns=["BIA", "email", "phone"],
                    ),
                ]
            )

    browser.close()

# write dataframe to xlsx file
df.to_excel(output_file, index=False)