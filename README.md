# kiwi-crawler

Web crawler uses kiwi api to create a calendar of flight directions and low prices for a month from the current date. Updates every day after 00:00 one month in advance since prices change every day. Also periodically confirms of prices of found tickets. It is required to request confirmation of the prices of the found ticket, since:
1. price is subject to change
2. the ticket found may be invalid
