import requests

def serp_image_api():
    import os
    import serpapi

    #pip install serpapi
    # https://serpapi.com/playground 

    # Initialize the client with your SerpApi key
    # Best practice is to use an environment variable: export SERPAPI_KEY="your_api_key"
    client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY", "YOUR_ACTUAL_API_KEY"))

    # Define your image search query parameters
    search_parameters = {
        "engine": "google_images",  # Targets the Google Images engine directly
        "q": "red panda",            # Your search term
        "gl": "us",                  # Country to search from
        "hl": "en",                   # Language for the search results
        "ijn": 10,                  # number of pages for pagination
        "tbs": "il:cl"              #: Used to filter images. For instance, setting "tbs": "il:cl" filters the engine to only display images with Creative Commons licenses.
    }

    try:
        # Execute the image search
        results = client.search(search_parameters)
        
        # Extract the array of image results from the response dictionary
        images = results.get("images_results", [])
        
        print(f"Successfully retrieved {len(images)} images.\n")
        
        # Iterate through the images and print structured details
        for index, image in enumerate(images[:5], start=1):
            print(f"--- Image #{index} ---")
            print(f"Title:     {image.get('title')}")
            print(f"Source:    {image.get('source')} ({image.get('link')})")
            print(f"Original:  {image.get('original')}")
            print(f"Thumbnail: {image.get('thumbnail')}")
            print(f"Resolution: {image.get('width')}x{image.get('height')}\n")

            #save images to local path
        
        #return a list of paths
        return []

    except Exception as e:
        print(f"An error occurred while fetching images: {e}")
        return None

def brave_image_api():
    #docs: https://api-dashboard.search.brave.com/api-reference/images/image_search
    import requests

    response = requests.get(
        "https://api.search.brave.com/res/v1/images/search",
        headers={
            "X-Subscription-Token": "<YOUR_API_KEY>",
            "Accept": "application/json",
            "Accept-Encoding": "gzip"
        },
        params={
            "q": "mountain landscape",
            "search_lang": "en",
            "country": "US",
            "safesearch": "strict",
            "count": "50",
            "spellcheck": "true"
        },
    ).json()
