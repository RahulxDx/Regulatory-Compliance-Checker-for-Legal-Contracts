import requests
import json
import pandas as pd

# API Key and URL
API_KEY = "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"
url = "https://api.groq.com/openai/v1/chat/completions"

# Load the dataset
df = pd.read_csv("dataset.csv")

# Create a new column for Exact Laws
df["Exact Law"] = ""

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    prompt = row["contract"]  # Get the contract text

    # Prepare the payload for the API
    data = {
        "messages": [
            {
                "role": "system",
                "content": "You're Legal Contract Analyzer. Identify Exact Laws from given contract text.(Just list the extract laws alone no extra texts)"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": "llama3-8b-8192",
        "temperature": 0
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        # Make the API call
        res = requests.post(url, data=json.dumps(data), headers=headers)
        res.raise_for_status()
        response = res.json()

        # Extract and process the response
        if "choices" in response and response["choices"]:
            laws_text = response["choices"][0]["message"]["content"]
            # Split and clean up the laws list
            laws_list = laws_text.split("*")[1:]  # Skip the first empty split
            # Join the list into a single string for the DataFrame
            df.at[index, "Exact Law"] = "; ".join(laws_list).strip()
        else:
            df.at[index, "Exact Law"] = "No laws identified"
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed for index {index}: {e}")
        df.at[index, "Exact Law"] = "Error during API call"
    except Exception as e:
        print(f"An error occurred for index {index}: {e}")
        df.at[index, "Exact Law"] = "Error during processing"

# Save the updated DataFrame to a new CSV file
df.to_csv("updated_dataset.csv", index=False)

print("Processing complete. Updated dataset saved as 'updated_dataset.csv'.")