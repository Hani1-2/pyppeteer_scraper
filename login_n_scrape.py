import asyncio
from pyppeteer import launch

async def login_to_website(username, password, login_selectors):
    # browser = await launch(executablePath='/usr/bin/google-chrome-stable', headless=True, args=['--no-sandbox'])
    browser = await launch()
    page = await browser.newPage()

    try:
        login_url = 'https://web.facebook.com/login/?_rdc=1&_rdr'  # Replace with the URL of the login page
        await page.goto(login_url, {'timeout': 240000})

        # Wait for the login page to load
        await page.waitForSelector(login_selectors['email'])
        await page.waitForSelector(login_selectors['password'])

        # Fill in the login form
        await page.type(login_selectors['email'], username)
        await page.type(login_selectors['password'], password)

        # Submit the login form
        await page.click(login_selectors['submit'])

        # Wait for the login process to complete
        await page.waitForNavigation()

        await page.screenshot({'path': 'quotes.png'})
        # Check if login was successful (you may need to adjust the selector based on your website)
        if await page.querySelector(login_selectors['error']) is not None:
            print('Login failed. Check your credentials.')
        else:
            print('Login successful.')
    finally:
        # Make sure to close the browser even if there is an exception
        await browser.close()

# Example usage:
login_selectors = {
    'email': '#email',             # Replace with the selector for the email input element': '#username',        # Replace with the selector for the username input element
    'password': '#pass',        # Replace with the selector for the password input element
    'submit': '#loginbutton',      # Replace with the selector for the login/submit button
    'error': '.login-error',        # Replace with the selector for an error element (if login fails)
}

username = 'your username'
password = 'your paswword'

asyncio.get_event_loop().run_until_complete(login_to_website(username, password, login_selectors))
