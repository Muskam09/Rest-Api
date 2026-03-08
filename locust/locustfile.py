from locust import HttpUser, task, between

class LibraryLoadUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def get_all_books(self):
        """Тестуємо основний ендпоінт читання книг"""
        with self.client.get("/books/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")