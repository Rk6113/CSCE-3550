import requests

def main():
    url = "http://127.0.0.1:8080/auth"  # Change if your server is running on a different URL or port
    
    # Attempt to send a POST request to /auth with no body
    response = requests.post(url)

    # Check if the request was successful
    if response.status_code == 200:
        print("Success! Received JWT:")
        print(response.json())  # Assuming the response is in JSON format
    else:
        print(f"Failed to retrieve JWT. Status code: {response.status_code}")
        print("Response:", response.text)

if __name__ == "__main__":
    main()

