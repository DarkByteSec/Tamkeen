import json
import os


# Default path for the JSON database file (Variable -> snake_case)
data_path = os.path.join("data", "services.json")

# Mapping English disability names to Arabic database categories (Variable -> snake_case)
disability_mapping = {
    "Motor": "حركية",
    "Visual": "بصرية",
    "Hearing": "سمعية",
    "Cognitive": "ذهنية"
}


class ServiceManager:
    """
    Class name uses PascalCase.
    Manages loading and filtering services from the JSON database.
    """

    def __init__(self, file_path=data_path):
        # Variables inside class use snake_case
        self.file_path = file_path

    def loadServicesData(self):
        """
        Function name uses camelCase.
        Loads services from the JSON file.
        Returns an empty list if the file is missing or invalid.
        """
        if not os.path.exists(self.file_path):
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as file_object:
                services_list = json.load(file_object)

                return services_list if isinstance(services_list, list) else []

        except (OSError, json.JSONDecodeError):
            return []

    def getFilteredServices(self, selected_language, target_disability):
        """
        Function name uses camelCase.
        Filters services according to the selected language
        and disability category.
        """
        # Variables inside function use snake_case
        all_services = self.loadServicesData()
        filtered_results = []

        if not target_disability:
            return filtered_results

        for service in all_services:
            allowed_categories = service.get("target_disabilities", [])

            if (
                "جميع الإعاقات" in allowed_categories
                or target_disability in allowed_categories
            ):

                service_name = service.get("service_name", {})
                description = service.get("description", {})
                requirements = service.get("requirements", {})

                formatted_item = {
                    "service_id": service.get("service_id"),
                    "service_name": service_name.get(
                        selected_language, service_name.get("ar", "")
                    ),
                    "description": description.get(
                        selected_language, description.get("ar", "")
                    ),
                    "requirements": requirements.get(
                        selected_language, requirements.get("ar", "")
                    )
                }

                filtered_results.append(formatted_item)

        return filtered_results