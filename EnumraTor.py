import requests
import configparser

class SecurityTrailsAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_subdomains(self, domain):
        url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
        headers = {"APIKEY": self.api_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("subdomains", [])
        else:
            print(f"Error fetching subdomains from SecurityTrails. Status code: {response.status_code}")
            return []

class CRTShAPI:
    @staticmethod
    def fetch_subdomains(domain):
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        response = requests.get(url)
        if response.status_code == 200:
            subdomains = set()
            for entry in response.json():
                subdomain = entry["name_value"]
                subdomains.add(subdomain)
            return list(subdomains)
        else:
            print(f"Error fetching subdomains from crt.sh. Status code: {response.status_code}")
            return []

class FileManager:
    @staticmethod
    def save_subdomains_to_file(subdomains, domain, file_path):
        with open(file_path, "w") as file:
            for subdomain in subdomains:
                full_domain = f"{subdomain}.{domain}"
                file.write(full_domain + "\n")

class SubdomainFetcher:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.api_key = self.config.get("SecurityTrails", "api_key")
        self.security_trails_api = SecurityTrailsAPI(self.api_key)

    def fetch_and_save_subdomains(self, domain):
        print("Fetching subdomains from SecurityTrails...")
        subdomains_security_trails = self.security_trails_api.fetch_subdomains(domain)
        print(f"Found {len(subdomains_security_trails)} subdomains from SecurityTrails.")

        print("Fetching subdomains from crt.sh...")
        subdomains_crtsh = CRTShAPI.fetch_subdomains(domain)
        print(f"Found {len(subdomains_crtsh)} subdomains from crt.sh.")
        
        all_subdomains = subdomains_security_trails + subdomains_crtsh
        if all_subdomains:
            file_path = f"{domain}_subdomains.txt"
            FileManager.save_subdomains_to_file(all_subdomains, domain, file_path)
            print(f"Subdomains saved to {file_path}")
        else:
            print("No subdomains found.")

def main():
    domain = input("Enter a domain name: ")
    subdomain_fetcher = SubdomainFetcher()
    subdomain_fetcher.fetch_and_save_subdomains(domain)

if __name__ == "__main__":
    main()
