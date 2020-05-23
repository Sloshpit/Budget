from datetime import datetime, date, timedelta
from calendar import monthrange
import calendar

def get_first_of_month (some_date):
    first_of_month =  (str(some_date.year)+"-"+ str(some_date.month)+"-"+"1")
    return first_of_month

def get_last_of_month (some_date):
    
    days_in_month = calendar.monthrange(some_date.year,some_date.month)[1]
    last_of_month = (str(some_date.year)+"-"+str(some_date.month)+"-"+str(days_in_month))
    #next_month = some_date + timedelta (days_in_month)
    return last_of_month

def get_first_of_next_month (some_date):
        days_in_month = calendar.monthrange(some_date.year, some_date.month)[1]
        next_month =some_date + timedelta (days_in_month)
        next_first_of_month = (str(next_month.year)+"-"+str(next_month.month)+"-"+"1")  
        return next_first_of_month

def get_first_of_last_month (some_date):
        days_in_month = calendar.monthrange(some_date.year, some_date.month)[-1]
        last_month =some_date - timedelta (days_in_month)
        last_first_of_month = (str(last_month.year)+"-"+str(last_month.month)+"-"+"1")  
        return last_first_of_month

def get_last_of_last_month (some_date):
        first_of_last_month = get_first_of_last_month(some_date)
        first_of_last_month = datetime.strptime(first_of_last_month, '%Y-%m-%d')
        days_in_month = calendar.monthrange(first_of_last_month.year, first_of_last_month.month)[1]
        print (days_in_month)
        last_month =some_date - timedelta (days_in_month)
        last_last_of_month = (str(last_month.year)+"-"+str(last_month.month)+"-"+str(days_in_month))  
        return last_last_of_month

