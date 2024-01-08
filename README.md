# Nanohost

This thing helps you share working html pages by storing them in db and serving to you when needed.

There are only 2 endpoints:
- /upload - uploads post body to db
- /id/<id> gets stored content
- details are here: https://realnice.page/docs#/

Pages are limited by views and storing duration. Default limit is 1000 views and 1 day of duration. You can change them if you need to.
