from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time


def scrape_aicte_trivandrum():
    driver = webdriver.Safari()
    driver.get("https://facilities.aicte-india.org/dashboard/pages/angulardashboard.php#!/approved")

    wait = WebDriverWait(driver, 30)

    # 🟢 Wait for state dropdown
    state_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "state")))
    state_dropdown.send_keys("Kerala")
    time.sleep(3)

    # 🟢 Debug: print page HTML snippet to find district element
    html_snippet = driver.page_source
    print("\n===== DEBUG: First 2000 chars of HTML =====\n")
    print(html_snippet[:2000])
    print("\n==========================================\n")

    # Try different locators for district
    try:
        district_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "district")))
    except:
        try:
            district_dropdown = wait.until(EC.presence_of_element_located((By.ID, "district")))
        except:
            print("❌ Could not find district dropdown — check the printed HTML above")
            driver.quit()
            return []

    district_dropdown.send_keys("Thiruvananthapuram")
    time.sleep(3)

    # 🟢 Click search button
    search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Search')]")))
    search_btn.click()

    # 🟢 Wait for results table
    table = wait.until(EC.presence_of_element_located((By.ID, "example")))
    time.sleep(5)

    rows = table.find_elements(By.XPATH, ".//tbody/tr")
    colleges = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) > 5:
            colleges.append({
                "Institute Code": cols[0].text.strip(),
                "College Name": cols[1].text.strip(),
                "State": cols[2].text.strip(),
                "District": cols[3].text.strip(),
                "City": cols[4].text.strip(),
                "Website": cols[8].text.strip() if len(cols) > 8 else "N/A"
            })

    driver.quit()
    return colleges


def main():
    data = scrape_aicte_trivandrum()
    if data:
        df = pd.DataFrame(data)
        df.to_excel("trivandrum_colleges.xlsx", index=False)
        print(f"✅ Saved {len(df)} colleges to trivandrum_colleges.xlsx")
    else:
        print("⚠️ No data collected. Check the printed HTML snippet to update locators.")


if __name__ == "__main__":
    main()
