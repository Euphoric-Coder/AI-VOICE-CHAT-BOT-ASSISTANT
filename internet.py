import requests

def check_internet_connection(url="https://www.google.com", timeout=10):
    """
    Got this idea from the following link and modified it in my way:
    https://www.geeksforgeeks.org/how-to-check-whether-users-internet-is-on-or-off-using-python/

    Checks if the internet connection is active by making a request to a specified URL.

    Args:
        url (str): The URL to request. Default is "https://www.google.com".
        timeout (int): The maximum time (in seconds) to wait for a response. Default is 10 seconds.

    Returns: 
        Return True if the internet is on, False otherwise.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raises an HTTPError for bad responses (like 4xx and 5xx)
        return True
    except requests.RequestException:
        return False


if __name__ == "__main__":
    if check_internet_connection():
        print("Internet is on")
    else:
        print("Internet is off")
