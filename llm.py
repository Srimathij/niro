################ aws model api response ####################
def get_aws_response(prompt_template):
    try:
        # Define the API endpoint and request payload
        url = "http://13.200.171.249:11434/api/generate"
        payload = {
            "model": "mistral:latest",
            "prompt": prompt_template,
            "stream": False
        }

        # Make the API request
        response = requests.post(url, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            response_text = response_data.get("response", "").strip()  # Adjust key based on API response structure
        else:
            response_text = f"Error: {response.status_code}, {response.text}"

        # return jsonify({'response': response_text})
        return response_text

    except Exception as e:
        return jsonify({'error': str(e)})