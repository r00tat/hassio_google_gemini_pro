# Google Gemini Pro Home Assistant Integration

This integration allows you to use Google Gemini Pro as an assistant in Home Assistant.

It requires to create a GCP Project, a service account with the necessary permissions and a service account key.

The required role is:

- Vertex AI User

The integration was based on the original [Google Conversation AI Integration in Home Assistant](https://www.home-assistant.io/integrations/google_generative_ai_conversation) for PALM. As authenticating with API Key can lead to an error, if you are located outside the US, I have switched this integration to use a service account.
