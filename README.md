# Facebook Post Notify - Line Bot
This project scrapes **latest** facebook listings/posts from groups. If the post contains any keyword desired, 
it sends a notification to Line users/groups through Line Messaging API.

## What you need
- A Facebook account
- A Line Messaging API channel access token
- ID of Line users/groups you wish to send notifications to

## Config File
Below shows `config.yaml.example`
```yaml
fb_cred:
  account: '<fb_account>'
  password: '<fb_password>'

line_bot:
  channel_access_token: '<channel_access_token>'

group_id: '<group_id>'

keywords:
  - '<keyword1>'
  - '<keyword2>'
  - '<keyword3>'

receivers:
    <user/group name1>: "<user/group's id>"
    <user/group name2>: "<user/group's id>"

message: <message_format>
```
- `<group_id>`: ID of Facebook group you wish to scrape. Go to the group's page, if the url is 
`https://www.facebook.com/groups/1234567890`, then the id is `1234567890`.
- `<keyword1>, <keyword2>...`: Keywords that latest listings/posts must contain to send notifications.
    `keywords: ''` if no keywords desired, which will send notification every new post.
- `<user/group name1>, <user/group name2>...`: Name of users/groups, can be anything you like. Used for logging 
    when sending notifications: `[Log] Sending to <user/group name>...`
- `<user/group's id>`: Line id of user/group you wish to send notifications to
- `<message format>`: Format of the notification message. e.g.
  ```
  NEW POST!!
  
  {url}
  {content}
  ---
  {listing_text}
  ```
  The message will be like
  ```
  NEW POST!
  
  https://www.facebook.com/groups/1234567890/posts/1234567890
  My husband bought it without my permission. Selling for $450.
  ---
  PlayStation 5 (Brand new!)
  ```
You can name your config file anything you like.

### Encrypt
Since the config file contains sensitive data, encrypt it before running on cloud services. \
`python3 fb_scraper/utils/crypto/encryt.py config.yaml` \
The encoded file will be named `config.yaml.enc`.

## Start the script
`python3 main.py config.yaml.enc listing` or \
`python3 main.py config.yaml.enc post` \
The script uses selenium, `-H` for headless. \
Last argument depends on what you want to scrape.