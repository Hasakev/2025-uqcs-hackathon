import requests
from http.cookies import SimpleCookie

def scrape_website_with_cookie(url: str, cookie_string: str) -> str:
    """
    Scrapes a website's HTML content using a provided cookie string.

    Args:
        url: The URL of the website to scrape.
        cookie_string: The cookie string to set for the request.

    Returns:
        The HTML content of the website as a string.
    """
    try:
        # Parse the cookie string into a SimpleCookie object
        cookie = SimpleCookie()
        cookie.load(cookie_string)

        # Convert SimpleCookie to a dictionary for requests
        cookies_dict = {key: morsel.value for key, morsel in cookie.items()}

        response = requests.get(url, cookies=cookies_dict)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error scraping website: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
    
def main():
    # Example Usage:

    # Replace with a real URL and a valid cookie string for testing
    test_url = "https://learn.uq.edu.au/webapps/bb-mygrades-BB5fd17f67f4120/myGrades?course_id=_182657_1&stream_name=mygrades&is_stream=true"
    BBsessionid = "expires:1755366777,id:EAD57E9B40DBA308687FF8A1CF2A370B,sessionId:2875487893,signature:a7ed9acd81cb080bd71bbdbe4cdd9575e1c31c8800791e9ac1988f548e756063,site:332f5b37-e3c3-43c4-8a0e-c1d71613da3d,timeout:10800,user:8eecbe69b7d4462ab7e76b170690e5df,v:2,xsrf:62e3b5bd-de48-48ac-8389-92be654e59ea"
    test_cookie_string = "BbRouter="+BBsessionid+"; Path=/; Secure; HttpOnly;"
    print(f"Scraping {test_url} with cookie: {test_cookie_string}")
    html_content = scrape_website_with_cookie(test_url, test_cookie_string)
    print(html_content[1000:2000]) # Print first 500 characters of the HTML

if __name__ == '__main__':
    main()
