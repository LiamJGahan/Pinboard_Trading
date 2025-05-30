# Pinboard Trading
#### Video Demo:  <(https://youtu.be/umCg9-xSZmQ)>
#### Description:

Pinboard Trading is a practice trading web application built using Flask and PostgreSQL, inspired by CS50x’s Finance problem set. This project represents a reinterpretation of the original assignment, extending its functionality, user experience and interface design.
Pinboard Trading allows users to simulate the buying and selling of stocks using real-world market data. Users can search for stock symbols using a search bar on the homepage (the “Index”), create interactive stock cards, and manage their portfolio with a user-friendly drag-and-drop interface. The application's key feature is its “pinboard” layout, each stock added is visualised as a card containing real-time data, trading options and performance indicators.

Features

Stock Cards
Once a user searches for a stock symbol, a trading card is generated and added to their personal pinboard. Each card displays:
Company symbol and name
Current price
Total shares held
Total investment
An icon showing the price movement compared to the previous day 

Cards can be reordered using SortableJS, which updates their position in the database to reflect the user’s preferences.

Trading 
Each card includes options to buy or sell additional shares. These actions are tracked in a transactions table, and the user’s cash balance is updated. A “quick sell/remove card” option, marked with a red x button, allows users to instantly sell all remaining stock and remove the card from their dashboard.
Price Change Tracking
To enhance user insight, each card features a small icon in the top-left corner reflecting the stock’s price change from the previous day. This is implemented by storing the previous closing price and comparing it to the latest closing price upon user login or daily refresh. This involved handling of when to update stored prices to avoid stale data, especially when the user is inactive.

Analytics Page
A dedicated Analytics page provides further stock information. This includes a Chart.js doughnut chart representing analyst ratings (Strong Buy, Buy, Hold, Sell, Strong Sell), parsed and prepared in the backend for display. This required converting AlphaVantage's analyst rating data into a format suitable for Chart.js visualisation.

User Account Management
The application includes an Account page that lets users:
Change their password
Update their username (with username checks)
Top up their cash balance for further trading

Backend and Database
Initially developed using an Aiven MySQL databse, the application was migrated to PostgreSQL hosted by Clever Cloud due to hosting limitations with Aiven. This required significant restructuring of database commands, including query syntax and connection handling. Despite the challenge, PostgreSQL provided better performance and integration for deployment.
The backend is structured using Flask, and each route is protected by a @login_required decorator where necessary. The stocks table stores each user’s saved stock cards, along with price data, position (for ordering), and timestamps for tracking changes. The transactions table logs every buy or sell action, providing historical data for potential future features like performance tracking or graphing.

API and Rate Limiting
Market data is retrieved from the AlphaVantage API, which imposes strict rate limits. To manage this, API requests are spaced out logically, for example, the app only fetches new data for each stock if it's outdated or when the user triggers a relevant action (e.g., login or visiting analytics). This not only preserves quota but also improves loading speed by avoiding unnecessary calls.

User Interface and Experience
The frontend uses HTML, CSS, and JavaScript (including Fetch API and Chart.js), with Jinja templating from Flask. Special attention was given to mobile responsiveness and usability. Cards collapse into a list layout on smaller screens, and drag-and-drop functionality remains usable via SortableJS.
The username availability check during registration and when updating the username is handled asynchronously using a separate /check_username route. The frontend calls this via Fetch on input change and updates the interface with appropriate feedback messages e.g., “Username available” or “Username already taken” coloured green or red respectively.

Hosting
The project is hosted on Clever Cloud, using their managed PostgreSQL and Python Flask support. This required environment configuration and the secure handling of API keys and database credentials via environment variables.

Design Decisions
Some important design decisions include:
Choosing PostgreSQL over MySQL for better hosting compatibility.
Using session-based card updates for responsiveness and performance.
Limiting AlphaVantage API calls by tracking when prices were last updated.
Avoiding large dependencies or JS frameworks, to keep the frontend lightweight and maintainable.

Conclusion
Pinboard Trading represents an extension and reinterpretation of the CS50x Finance project. It combines practical frontend interactivity with solid backend logic and careful API/data handling. Through this project, I deepened my skills in Flask, REST APIs, PostgreSQL, JavaScript interactivity, and full-stack deployment.


To run locally, please uncomment the following lines below found in api.py

if __name__ == '__main__':
    app.run(port=5002)

Alternativley use the online version linked below (Hosted by Clever Cloud)

Online version
https://app-3c8fd804-a8bd-4e0f-ad40-add41e7a8f8a.cleverapps.io/


## Citations

https://cs50.harvard.edu/x/2025/psets/9/finance/
CS50 Harvardx
-(finance) Helper.py functions used a reference/base for (pinboard) helper.py. (7/4/2025)
-Used MySQL table queries from finance for pinboard database (transactions, users). (4/4/2025)
-(finance) Login, logout, apology and login_required imported to project with some minor adjustments for postgres. (25/04/2025)
-(finance) Register function imported into project and modified for postgres. (06/05/2025)
-(finance) Buy and sell funtions were used as a base in which to create the trade function. (07/05/2025)

https://cs50.harvard.edu/x/2025/psets/9/finance/
LiamJGahan problem set 
-(finance) Password API handler imported to project and modified for postgres. (06/05/2025)

https://www.w3schools.com/python
W3Schools
-Understanding Try:/Except: (7/4/2025)
-Understanding .get (7/4/2025)
-Researching how to merge dictionaries. (28/04/2025)
-Researching Python abs() Function. (08/05/2025)
-Researching Window confirm(). (10/05/2025)
-Research on overflow: Auto. (17/05/2025)
-Researching how to place text over images. (18/05/2025)
-Research on transitions. (21/05/2025)
-Research on CSS background. (23/05/2025)
-Researched HTML data. (20/05/2025)
-Researched oninput Event and textContent. (28/05/2025)

https://chatgpt.com/
Chat GPT
-Finding database hosting providers. (Aiven). (4/4/2025)
-Assistance in understanding postgres. (25/04/2025)
-Goal milestones and productivity assistance. (27/04/2025 to project completion) 
-Bugfinding and troubleshooting assistance. (28/04/2025 to project completion) 
-Psycopg2 assistance (30/04/2025)
-Assistance deploying Clever Cloud application. (11/05/2025)

https://www.pythonhelp.org/tutorials/first-key-dictionary-python/
Python Help
-Research how to get the first item in a python dict "first_key = next(iter(my_dict))". (7/4/2025)

https://cs50.ai/chat
CS50 AI chat 
-help with understanding dictionaries in Python. (8/4/2025)

https://www.clever-cloud.com/developers/doc
Clever Cloud 
-Documentation for postgres database. (25/04/2025)
-Documentation for Python application. (11/05/2025)

https://gist.github.com/bmaupin/0ce79806467804fdbbf8761970511b8c
bmaupin
-Finding a new database that offers free hosting. (Clever Cloud)(25/04/2025)

https://github.com/SJK9476?tab=repositories
LiamJGahan
-Researching various code snippets with previous work I have done. (25/04/2025)
-Viewing previous JS fetch examples. (21/05/2025)

https://ttl255.com/jinja2-tutorial-part-2-loops-and-conditionals/
ttl255.com
-Research on jinja2. (28/04/2025)
-Research on template filters. (14/05/2025)

https://www.favicon.cc/
favicon.cc
-Favicon creation. (28/04/2025)

https://www.alphavantage.co
Alphavantage
-Linked 2 APIs to my project. (7/4/2025)
-Researched the key limit of the APIs I am using. (28/04/2025)

https://dribbble.com/tags/card-ui
dribbble.com
-Research on card design. (29/04/2025)

https://dbeaver.io/
DBeaver
-Used to recreate user and transaction tables. (25/04/2025)
-Used to create stocks table. (29/04/2025)

https://www.geeksforgeeks.org/get-current-timestamp-using-python/
geeksforgeeks.org
-Researching how to get the date/datetime using python. (30/04/2025)

https://www.psycopg.org/docs/
-Research on psycopg. (25/04/2025)
-Research on realdict for psycopg2. (30/04/2025)

https://getbootstrap.com/docs/5.3/getting-started/introduction/
BootStrap
-Research on position translate. (30/04/2025)
-Research on d-flex. (30/04/2025)
-Research on shadow. (01/05/2025)

https://icons.getbootstrap.com/
BootStrap icons
-Found an icon for my card delete button. (01/05/2025)
-Found icons for change in price. (26/05/2025)

https://www.youtube.com/watch?app=desktop&v=UGtB7i9gD4s
Coding Yaar
-Learning how to use BootStrapicons in buttons. (01/05/2025)

https://ico.org.uk/for-organisations/advice-for-small-organisations/create-your-own-privacy-notice/
ico.org.uk
-Generated a privacy policy. (01/05/2025)

https://stackoverflow.com/questions/33730538/difference-between-decimal-and-numeric-datatypes-in-postgresql#:~:text=For%20PostgreSQL%20the%20answer%20is,part%20of%20the%20SQL%20standard.
stackoverflow
-Researching why NUMERIC in postgres was creating a Decimal value type. (08/05/2025)

https://www.postgresql.org/docs/current/plpython-data.html
Postgresql.org
-Research on how to convert data type to Decimal using decimal import. (08/05/2025)

https://getbootstrap.com/docs/4.0
-Researched how to style a welcome message. (12/05/2025)
-Research on list groups. (17/05/2025)
-Research on flex column. (17/05/2025)

https://www.chartjs.org/docs/latest/
Chartjs
-Research on doughnut style pie chart. (14/05/2025)
-Researched responsive chart option. (18/05/2025)

https://docs.rewst.help/documentation/jinja/list-of-jinja-filters
-Reseach on tojson. (14/05/2025)

https://www.pexels.com
Pexels
-Photo by Alesia  Kozik: https://www.pexels.com/photo/graph-of-the-movement-of-the-value-of-bitcoin-6770775/ (17/05/2025)

https://github.com/SortableJS/Sortable
SortableJS
-Researched SortableJS. (20/05/2025)
-Reseaching a way to scroll properly on mobile using touchStartThreshold. (24/05/2025)
-Researched the AutoScroll plugin. (25/05/2025)

https://www.kryogenix.org/code/browser/custom-drag-image.html
Kryogenix.org
-Researching how to set custom ghost image for drag and drop. (20/05/2025)

https://developer.mozilla.org/en-US/docs
Mozilla
-Researching drag and drop in html. (21/05/2025)
-Research on fetch. (22/05/2025)

https://stackoverflow.com/questions/335516/simple-javascript-problem-onclick-confirm-not-preventing-default-action
stackoverflow
-Fixing bug caused by confirm() where cancel would still delete a card. (23/05/2025)

https://www.geeksforgeeks.org/how-to-make-an-image-rounded-in-bootstrap/
Geeksforgeeks
-Researched how to round the corners of an image using bootstrap. (23/05/2025)

## Acknowledgement of Academic Honesty

This project was completed in accordance with CS50x's policy on academic honesty. Any external help, including AI-generated guidance, documentation, or previously written work, is cited. All code in this project was written by me, with referenced ideas adapted and implemented independently.