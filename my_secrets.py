from google.cloud import secretmanager

class googleSecrets():

    def __init__(self, project_id):
        # GCP project in which to store secrets in Secret Manager.
        self.project_id = project_id
        # Create the Secret Manager client.
        self.gs_client = secretmanager.SecretManagerServiceClient()
        # Build the parent name from the project.
        self.parent = f"projects/{self.project_id}"

    def read_secret(self, secret_id):
        # Build the resource name of the secret version.
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
        # Access the secret version.
        response = self.gs_client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")