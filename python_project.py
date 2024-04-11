
#Midproject - Adi Carmeli

#Importing Libraries

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#pd.set_option('display.max_columns', None)

#load the CSV file into a DataFrame
data_path = '/content/python_project_naya/hotel_bookings.csv'
data = pd.read_csv(data_path)

"""**Data Observation & Verification**"""

# Displaying how much data the file contains
len (data)
data.shape

# Displaying the first few rows of the DataFrame
data.head()

# Displaying the last few rows of the DataFrame
data.tail()

# Overview of the values each column contains
data.describe()

#dataset information
data.info()

"""**Data Cleaning and Manipulation**"""

#Checking features with NaN values
NaN = data.isna().sum()
NaN

# Replace missing values:
# children: If no number is given, I assumed that there are no children included.
# country: If none given - it is unknown.
# agent: If no agency is given, booking was most likely made without one.
# company: If none given, it was most likely private.

nan_replacements = {"children": 0, "country": "Unknown", "agent": 0, "company": 0}
data = data.fillna(nan_replacements)

# change the children column data type
data['children'] = data['children'].astype(int)
data['children'].dtype

# Some rows contain entreis with 0 adults, 0 children and 0 babies.
# I'm creating new column named 'Total Guests'
# then, drop these entries with zero total guests

data['Total_guests'] = data['adults'] + data['children'] + data['babies']
#data['Total Guests'].head(10)

data = data.drop(data[data['Total_guests'] == 0].index)

# Convert string month to numerical one (Dec = 12, Jan = 1, etc.)
data['Month_number'] = pd.to_datetime(data['arrival_date_month'], format='%B').dt.month

# Convert the month numbers to integers
data['Month_number'] = data['Month_number'].astype(int)

data = data.reset_index(drop=True)

# Total Number of Days Stayed
data['Total_Stays'] = data['stays_in_weekend_nights'] + data['stays_in_week_nights']

# Checking for the missing values after drops
NaN_updated = data.isna().sum()
NaN_updated

# After cleaning, separate Resort and City hotel
# To know the acutal visitor numbers, only bookings that were not canceled are included.
rh = data[(data["hotel"] == "Resort Hotel") & (data["is_canceled"] == 0)]
ch = data[(data["hotel"] == "City Hotel") & (data["is_canceled"] == 0)]

"""**Data Visualization**

***How does the price per night vary over the year?***
"""

# adr - Avreage Daily Rate :
# is the measure of the average paid for rooms sold in a given time period.
# The metric covers only revenue-generating guestrooms

# Counting adults and children as paying guests only, not babies.
rh["adr_pp"] = rh["adr"] / (rh["adults"] + rh["children"])
ch["adr_pp"] = ch["adr"] / (ch["adults"] + ch["children"])

# barplot:
avg_adr_pp_per_month_rh = rh.groupby('Month_number')['adr_pp'].mean()
avg_adr_pp_per_month_ch = ch.groupby('Month_number')['adr_pp'].mean()

# Set figure size
plt.figure(figsize=(9, 4))

# Plot line plot for Resort Hotel
plt.plot(avg_adr_pp_per_month_rh.index, avg_adr_pp_per_month_rh.values, label='Resort Hotel', linestyle='-', color='c', marker='.')

# Plot line plot for City Hotel
plt.plot(avg_adr_pp_per_month_ch.index, avg_adr_pp_per_month_ch.values, label='City Hotel', linestyle='-', color='m', marker='.')

# Set title and labels
plt.title("Room price per night and person over the year", fontsize=16)
plt.xlabel("Month", fontsize=10)
plt.ylabel("Price [EUR]", fontsize=10)
plt.xticks(rotation=45)
plt.legend()

# Show plot
plt.grid(True)
plt.show()

"""This clearly shows that the prices in the Resort hotel are much higher during the summer. The rest of the months at a fairly stable average price per night.

The price of the city hotel varies less and is most expensive during spring and autumn.

***Which are the most busy month?***
"""

resort_guests_monthly = rh.groupby("Month_number")["hotel"].count()
city_guests_monthly = ch.groupby("Month_number")["hotel"].count()

resort_guest_data = pd.DataFrame({"month": list(resort_guests_monthly.index),
                    "hotel": "Resort hotel",
                    "guests": list(resort_guests_monthly.values)})

city_guest_data = pd.DataFrame({"month": list(city_guests_monthly.index),
                    "hotel": "City hotel",
                    "guests": list(city_guests_monthly.values)})
full_guest_data = pd.concat([resort_guest_data,city_guest_data], ignore_index=True)

# Set figure size
plt.figure(figsize=(9, 4))

# Plot line plot for Resort Hotel
plt.plot(resort_guest_data['month'], resort_guest_data['guests'], label='Resort hotel',color='c', marker='o', linestyle='-.')

# Plot line plot for City Hotel
plt.plot(city_guest_data['month'], city_guest_data['guests'], label='City hotel',color='m', marker='o', linestyle='-.')

# Customize plot
plt.title("Average number of hotel guests per month", fontsize=16)
plt.xlabel("Month", fontsize=10)
plt.xticks(rotation=45)
plt.ylabel("Number of guests", fontsize=10)
plt.legend()
plt.grid(True)

# Show plot
plt.show()

"""The City hotel has more guests during spring and autumn, when the prices are also highest.
In July and August there are more visitors, when prices are lower.

Guest numbers for the Resort hotel goes up slighty from July and August, which is also when the prices are highest.

Both hotels have the fewest guests during the winter.

***How long do people stay at the hotels?***
"""

# Create a DateFrame with the relevant data:

num_nights_res = list(rh["Total_Stays"].value_counts().index)
num_bookings_res = list(rh["Total_Stays"].value_counts())
sum_rh = rh["Total_Stays"].sum()
rel_bookings_res = rh["Total_Stays"].value_counts() / sum(num_bookings_res) * 100 # convert to percent

num_nights_cty = list(ch["Total_Stays"].value_counts().index)
num_bookings_cty = list(ch["Total_Stays"].value_counts())
rel_bookings_cty = ch["Total_Stays"].value_counts() / sum(num_bookings_cty) * 100 # convert to percent

res_nights = pd.DataFrame({"hotel": "Resort hotel",
                           "num_nights": num_nights_res,
                           "rel_num_bookings": rel_bookings_res})

cty_nights = pd.DataFrame({"hotel": "City hotel",
                           "num_nights": num_nights_cty,
                           "rel_num_bookings": rel_bookings_cty})


nights_data = pd.concat([res_nights, cty_nights], ignore_index=True)

#show figure:
plt.figure(figsize=(9, 4))
sns.barplot(x = "num_nights", y = "rel_num_bookings", hue="hotel",
            data=nights_data, palette=['m', 'c'],
            hue_order = ["City hotel", "Resort hotel"])
plt.title("Length of stay", fontsize=16)
plt.xlabel("Number of nights", fontsize=10)
plt.ylabel("Guests [%]", fontsize=10)
plt.legend(loc="upper right")
plt.xlim(0,22)
plt.show()

"""On average, guests of the City hotel stay 2.92 nights, and 48 at maximum.
On average, guests of the Resort hotel stay 4.14 nights, and 69 at maximum.

For the city hotel there is a clear preference for 1-4 nights. For the resort hotel, 1-4 nights are also often booked, but 7 nights also stand out as being very popular.
"""