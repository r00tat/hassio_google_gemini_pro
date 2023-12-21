# Google Gemini Pro Home Assistant Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

This integration allows you to use Google Gemini Pro as an assistant in Home Assistant.

It requires to create a GCP Project, a service account with the necessary permissions (Vertex AI user) and a service account key.

The integration was based on the original [Google Conversation AI Integration in Home Assistant](https://www.home-assistant.io/integrations/google_generative_ai_conversation) for PALM. As authenticating with API Key can lead to an error, if you are located outside the US, I have switched this integration to use a service account.

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?category=Integration&owner=r00tat&repository=hassio_blaulichtsms)

To be able to use the integration, you need to setup a GCP project with Vertex AI enabled. Create a service account, assigne the IAM role Vertex AI User and download the service account key.
This service account key is required in the configuration.

## Development

Setup your environment and start a test container by running `./dev.sh`.

---

[hassio_google_gemini_pro]: https://github.com/r00tat/hassio_google_gemini_pro
[buymecoffee]: https://www.buymeacoffee.com/r00tat
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/r00tat/hassio_google_gemini_pro.svg?style=for-the-badge
[commits]: https://github.com/r00tat/hassio_google_gemini_pro/commits/main
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/r00tat/hassio_google_gemini_pro.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40r00tat-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/r00tat/hassio_google_gemini_pro.svg?style=for-the-badge
[releases]: https://github.com/r00tat/hassio_google_gemini_pro/releases
