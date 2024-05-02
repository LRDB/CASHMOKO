import freecurrencyapi

def get_currency():
    API_KEY = "fca_live_zzq4Am5d6loNPz9rCjJEmOnUMWK30uqPwV3yC4KA"
    client = freecurrencyapi.Client(API_KEY)
    result = client.latest("PHP",["USD", "EUR", "JPY", "CAD"])
    return result["data"]

# print(client.status())
# print("Hello, World!")