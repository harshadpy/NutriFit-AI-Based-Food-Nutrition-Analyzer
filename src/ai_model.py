import os
import requests
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()
usda_api_key = os.getenv("USDA_API_KEY")

# Set up logging
logger.add("logs/app.log", rotation="10 MB", level="INFO")

# Validate API key
if not usda_api_key:
    logger.critical("USDA_API_KEY not found in environment variables. Please set it.")

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"


def query_nutrition_knowledge(question: str) -> str:
    """
    Uses locally running Ollama LLaMA3 model to answer nutrition-related questions.
    """
    try:
        logger.info(f"Querying Ollama for question: {question}")
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": question,
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response from LLaMA3.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama request error: {str(e)}")
        return "Unable to answer the question due to a local LLaMA3 server issue."
    except Exception as e:
        logger.error(f"Unexpected error using Ollama: {str(e)}")
        return "An unexpected error occurred while querying LLaMA3."

def get_nutrition_info(food_item: str) -> str:
    """
    Fetches detailed nutrition information for a specific food item using USDA FoodData Central API.
    """
    if not usda_api_key:
        return "USDA API key is not configured, cannot fetch nutrition information."

    try:
        # Search for the food item
        search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_item}&api_key={usda_api_key}"
        logger.info(f"Searching USDA for: {food_item}")
        search_response = requests.get(search_url)
        search_response.raise_for_status()

        search_data = search_response.json()
        if not search_data.get("foods"):
            logger.warning(f"No food items found for '{food_item}' in USDA search.")
            return f"No detailed nutrition information found for '{food_item}'."

        # Get the first matching food's FDC ID
        fdc_id = search_data["foods"][0].get("fdcId")
        if not fdc_id:
            logger.warning(f"FDC ID not found for the first food item in search for '{food_item}'.")
            return f"Could not retrieve FDC ID for '{food_item}'."

        # Fetch detailed nutrition info
        details_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}?api_key={usda_api_key}"
        logger.info(f"Fetching detailed nutrition info for FDC ID: {fdc_id} ({food_item})")
        details_response = requests.get(details_url)
        details_response.raise_for_status()

        food_data = details_response.json()
        nutrients = food_data.get("foodNutrients", [])

        if not nutrients:
            logger.info(f"No nutrient data found for FDC ID: {fdc_id} ({food_item})")
            return f"No detailed nutrient data available for {food_item}."

        nutrition_info = f"Nutrition info for {food_item}:\n"
        for nutrient in nutrients:
            nutrient_details = nutrient.get("nutrient", {})
            name = nutrient_details.get("name", "Unknown Nutrient")
            amount = nutrient.get("amount", "N/A")
            unit = nutrient_details.get("unitName", "")
            nutrition_info += f"- {name}: {amount} {unit}\n"

        logger.info(f"Successfully fetched and formatted nutrition data for {food_item}")
        return nutrition_info
    except requests.exceptions.RequestException as e:
        logger.error(f"Network or HTTP error fetching USDA data for '{food_item}': {str(e)}")
        return f"Unable to fetch nutrition info for '{food_item}' due to a network error."
    except ValueError as e:
        logger.error(f"JSON decoding error from USDA API for '{food_item}': {str(e)}")
        return f"Unable to process nutrition info for '{food_item}' due to data format issues."
    except Exception as e:
        logger.error(f"An unexpected error occurred fetching USDA data for '{food_item}': {str(e)}")
        return "Unable to fetch nutrition info due to an unexpected error."
